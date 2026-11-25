"""Quorum aggregation for signed indexer attestations."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .attest import verify_attestation


def quorum(
    attestations: list[dict[str, Any]],
    threshold: int,
) -> dict[str, Any]:
    """Aggregate attestations by result hash.

    Returns a dict with:
        status: CONSENSUS, DISPUTED, or INSUFFICIENT
        threshold: the requested threshold
        selected_hash: the winning hash or None
        selected_result: the winning result or None
        agreeing_nodes: node ids in the winning group
        dissenting_nodes: valid node ids outside the winning group
        invalid_nodes: node ids whose attestation failed verification
        valid_count: number of valid attestations
    """
    if threshold < 1:
        raise ValueError("threshold must be >= 1")

    valid: list[dict[str, Any]] = []
    invalid: list[str] = []
    for attestation in attestations:
        node_id = str(attestation.get("node_id", "<unknown>"))
        try:
            verify_attestation(attestation)
        except ValueError:
            invalid.append(node_id)
            continue
        valid.append(attestation)

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for attestation in valid:
        groups[str(attestation["result_hash"]).lower()].append(attestation)

    if len(valid) < threshold:
        return {
            "status": "INSUFFICIENT",
            "threshold": threshold,
            "selected_hash": None,
            "selected_result": None,
            "agreeing_nodes": [],
            "dissenting_nodes": [a["node_id"] for a in valid],
            "invalid_nodes": invalid,
            "valid_count": len(valid),
        }

    # Deterministic winner: most attestations, then lexicographically smallest
    # hash. A valid consensus still requires the threshold.
    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
    best_hash, best_group = ordered[0]

    if len(best_group) < threshold:
        return {
            "status": "DISPUTED",
            "threshold": threshold,
            "selected_hash": None,
            "selected_result": None,
            "agreeing_nodes": [],
            "dissenting_nodes": [a["node_id"] for a in valid],
            "invalid_nodes": invalid,
            "valid_count": len(valid),
        }

    agreeing = [a["node_id"] for a in best_group]
    dissenting = [
        a["node_id"]
        for a in valid
        if str(a["result_hash"]).lower() != best_hash
    ]
    return {
        "status": "CONSENSUS",
        "threshold": threshold,
        "selected_hash": best_hash,
        "selected_result": best_group[0]["result"],
        "agreeing_nodes": agreeing,
        "dissenting_nodes": dissenting,
        "invalid_nodes": invalid,
        "valid_count": len(valid),
    }
