from __future__ import annotations

from pathlib import Path

from veriindex.indexer import build_result, filter_logs, load_logs
from veriindex.metrics import compute_metric

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "events.json"
CONTRACT = "0xAbC0000000000000000000000000000000000001"


def _logs():
    return load_logs(FIXTURE)


def test_expected_metrics() -> None:
    logs = filter_logs(_logs(), CONTRACT, 5_000_000, 5_010_000)
    assert compute_metric(logs, "deposit_total") == 750
    assert compute_metric(logs, "withdraw_total") == 50
    assert compute_metric(logs, "swap_volume") == 1500
    assert compute_metric(logs, "unique_senders") == 4
    assert compute_metric(logs, "event_count") == 6


def test_result_filters_contract_and_range_and_dedupes() -> None:
    result = build_result(
        _logs(), "deposit_total", CONTRACT, 5_000_000, 5_010_000
    )
    assert result["value"] == "750"
    assert result["event_count"] == 6
    assert result["contract"] == CONTRACT.lower()
    assert result["from_block"] == 5_000_000
    assert result["to_block"] == 5_010_000


def test_event_count_uses_deduped_logs() -> None:
    result = build_result(
        _logs(), "event_count", CONTRACT, 5_000_000, 5_010_000
    )
    assert result["value"] == "6"


def test_empty_range_returns_zero() -> None:
    result = build_result(
        _logs(), "deposit_total", CONTRACT, 1, 2
    )
    assert result["value"] == "0"
    assert result["event_count"] == 0
