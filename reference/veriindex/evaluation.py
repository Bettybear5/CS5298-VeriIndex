"""Repeatable offline evaluation for the reference implementation."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .canonical import canonical_json, result_hash
from .indexer import build_result, load_logs
from .quorum import quorum
from .attest import sign_result

PRIVATE_KEYS = [
    "0x" + "0" * 63 + "1",
    "0x" + "0" * 63 + "2",
    "0x" + "0" * 63 + "3",
]


def _fixture() -> Path:
    return Path(__file__).resolve().parent.parent / "fixtures" / "events.json"


def _independent_deposit_total(logs: list[dict[str, Any]]) -> int:
    total = 0
    seen: set[tuple[str, int]] = set()
    for log in logs:
        key = (
            str(log.get("transactionHash", "")).lower(),
            int(log.get("logIndex", 0)),
        )
        if key in seen:
            continue
        seen.add(key)
        if log.get("event") == "Deposit":
            total += int(str(log["args"]["amount"]), 0)
    return total


def run_evaluation(fixture_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(fixture_path) if fixture_path else _fixture()
    logs = load_logs(path)
    contract = str(logs[0]["address"])

    # E1: determinism and order independence.
    results = [
        build_result(logs, "deposit_total", contract, 5_000_000, 5_010_000)
        for _ in range(5)
    ]
    hashes = {result_hash(result) for result in results}
    reversed_result = build_result(
        list(reversed(logs)), "deposit_total", contract, 5_000_000, 5_010_000
    )
    determinism = {
        "pass": len(hashes) == 1 and result_hash(reversed_result) in hashes,
        "unique_hashes": len(hashes),
        "canonical": canonical_json(results[0]),
    }

    # E2: correctness against an independent recomputation.
    expected = _independent_deposit_total(
        [
            log
            for log in logs
            if str(log["address"]).lower() == contract.lower()
            and 5_000_000 <= int(log["blockNumber"]) <= 5_010_000
        ]
    )
    actual = int(results[0]["value"])
    correctness = {
        "pass": expected == actual,
        "expected": expected,
        "actual": actual,
    }

    # E3: tamper detection with one lying node.
    attestations = [
        sign_result(results[0], key) for key in PRIVATE_KEYS
    ]
    tampered_result = dict(results[0])
    tampered_result["value"] = str(int(tampered_result["value"]) + 999)
    attestations[1] = sign_result(tampered_result, PRIVATE_KEYS[1])

    consensus = quorum(attestations, 2)
    strict = quorum(attestations, 3)
    tamper = {
        "pass": (
            consensus["status"] == "CONSENSUS"
            and consensus["selected_hash"] == result_hash(results[0])
            and attestations[1]["node_id"] in consensus["dissenting_nodes"]
            and strict["status"] == "DISPUTED"
        ),
        "consensus": consensus,
        "strict": strict,
    }

    # E4: local latency for the reference path.
    start = time.perf_counter()
    for _ in range(100):
        build_result(logs, "deposit_total", contract, 5_000_000, 5_010_000)
    elapsed_ms = (time.perf_counter() - start) * 1000 / 100
    latency = {"runs": 100, "mean_ms": round(elapsed_ms, 3)}

    report = {
        "fixture": str(path),
        "contract": contract,
        "e1_determinism": determinism,
        "e2_correctness": correctness,
        "e3_tamper": tamper,
        "e4_latency": latency,
        "all_offline_checks_pass": all(
            [
                determinism["pass"],
                correctness["pass"],
                tamper["pass"],
            ]
        ),
    }
    return report


def write_evidence(report: dict[str, Any], out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "evaluation.json"
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
