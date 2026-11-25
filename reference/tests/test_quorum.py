from __future__ import annotations

from pathlib import Path

import pytest

from veriindex.attest import sign_result, verify_attestation
from veriindex.indexer import build_result, load_logs
from veriindex.quorum import quorum

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "events.json"
CONTRACT = "0xAbC0000000000000000000000000000000000001"
KEYS = [
    "0x" + "0" * 63 + "1",
    "0x" + "0" * 63 + "2",
    "0x" + "0" * 63 + "3",
]


def _result():
    logs = load_logs(FIXTURE)
    return build_result(logs, "deposit_total", CONTRACT, 5_000_000, 5_010_000)


def test_valid_attestation() -> None:
    attestation = sign_result(_result(), KEYS[0])
    assert verify_attestation(attestation)


def test_consensus_with_one_lying_node() -> None:
    result = _result()
    attestations = [sign_result(result, key) for key in KEYS]
    tampered = dict(result)
    tampered["value"] = "999999"
    attestations[1] = sign_result(tampered, KEYS[1])

    outcome = quorum(attestations, 2)
    assert outcome["status"] == "CONSENSUS"
    assert outcome["selected_result"]["value"] == result["value"]
    assert attestations[1]["node_id"] in outcome["dissenting_nodes"]
    assert len(outcome["agreeing_nodes"]) == 2


def test_strict_threshold_disputes() -> None:
    result = _result()
    attestations = [sign_result(result, key) for key in KEYS]
    tampered = dict(result)
    tampered["value"] = "999999"
    attestations[1] = sign_result(tampered, KEYS[1])

    outcome = quorum(attestations, 3)
    assert outcome["status"] == "DISPUTED"
    assert outcome["selected_hash"] is None


def test_invalid_signature_is_ignored() -> None:
    result = _result()
    attestations = [sign_result(result, key) for key in KEYS[:2]]
    attestations[1]["signature"] = "0x" + "00" * 65

    outcome = quorum(attestations, 2)
    assert outcome["status"] == "INSUFFICIENT"
    assert len(outcome["invalid_nodes"]) == 1


def test_insufficient_nodes() -> None:
    result = _result()
    attestations = [sign_result(result, KEYS[0])]
    outcome = quorum(attestations, 2)
    assert outcome["status"] == "INSUFFICIENT"


def test_threshold_must_be_positive() -> None:
    with pytest.raises(ValueError):
        quorum([], 0)
