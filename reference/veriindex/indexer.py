"""Reference indexer: filter logs, compute a metric, build a canonical result."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .canonical import result_hash
from .metrics import compute_metric

DEFAULT_CHAIN_ID = 11155111  # Sepolia


def load_logs(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON array of event logs."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("log fixture must be a JSON array")
    return data


def filter_logs(
    logs: Iterable[Mapping[str, Any]],
    contract: str,
    from_block: int,
    to_block: int,
) -> list[Mapping[str, Any]]:
    """Filter by contract address and inclusive block range."""
    if from_block > to_block:
        raise ValueError("from_block must be <= to_block")
    target = contract.lower()
    return [
        log
        for log in logs
        if str(log.get("address", "")).lower() == target
        and from_block <= int(log.get("blockNumber", 0)) <= to_block
    ]


def build_result(
    logs: Iterable[Mapping[str, Any]],
    metric: str,
    contract: str,
    from_block: int,
    to_block: int,
    chain_id: int = DEFAULT_CHAIN_ID,
) -> dict[str, Any]:
    """Build the canonical result object.

    The object intentionally contains only deterministic scalar values.
    """
    filtered = filter_logs(logs, contract, from_block, to_block)
    value = compute_metric(filtered, metric)
    return {
        "schema_version": 1,
        "chain_id": int(chain_id),
        "contract": contract.lower(),
        "metric": metric,
        "from_block": int(from_block),
        "to_block": int(to_block),
        "event_count": compute_metric(filtered, "event_count"),
        "value": str(value),
    }


def build_result_with_hash(
    logs: Iterable[Mapping[str, Any]],
    metric: str,
    contract: str,
    from_block: int,
    to_block: int,
    chain_id: int = DEFAULT_CHAIN_ID,
) -> dict[str, Any]:
    """Build a result and attach its canonical hash."""
    result = build_result(
        logs, metric, contract, from_block, to_block, chain_id
    )
    return {"result": result, "result_hash": result_hash(result)}
