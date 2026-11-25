"""Deterministic metric computation over event logs."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

METRICS = (
    "event_count",
    "deposit_total",
    "withdraw_total",
    "swap_volume",
    "unique_senders",
)


def _amount(log: Mapping[str, Any]) -> int:
    raw = log.get("args", {}).get("amount", "0")
    if isinstance(raw, int):
        return raw
    return int(str(raw), 0)


def _swap_in(log: Mapping[str, Any]) -> int:
    raw = log.get("args", {}).get("amountIn", "0")
    if isinstance(raw, int):
        return raw
    return int(str(raw), 0)


def _dedupe(logs: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Deduplicate logs by (transaction hash, log index)."""
    seen: set[tuple[str, int]] = set()
    out: list[Mapping[str, Any]] = []
    for log in logs:
        key = (
            str(log.get("transactionHash", "")).lower(),
            int(log.get("logIndex", 0)),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(log)
    return out


def compute_metric(
    logs: Iterable[Mapping[str, Any]],
    metric: str,
) -> int:
    """Compute a metric over the given logs.

    The caller is responsible for filtering by contract and block range.
    """
    if metric not in METRICS:
        raise ValueError(f"unknown metric: {metric}")

    ordered = sorted(
        _dedupe(logs),
        key=lambda log: (
            int(log.get("blockNumber", 0)),
            int(log.get("logIndex", 0)),
            str(log.get("transactionHash", "")).lower(),
        ),
    )

    if metric == "event_count":
        return len(ordered)

    if metric == "deposit_total":
        return sum(
            _amount(log) for log in ordered if log.get("event") == "Deposit"
        )

    if metric == "withdraw_total":
        return sum(
            _amount(log) for log in ordered if log.get("event") == "Withdraw"
        )

    if metric == "swap_volume":
        return sum(
            _swap_in(log) for log in ordered if log.get("event") == "Swap"
        )

    if metric == "unique_senders":
        senders = {
            str(log.get("args", {}).get("from", "")).lower()
            for log in ordered
            if log.get("args", {}).get("from")
        }
        return len(senders)

    raise AssertionError("unreachable")
