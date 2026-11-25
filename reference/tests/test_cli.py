from __future__ import annotations

from veriindex.cli import main


def test_demo_passes(capsys) -> None:
    code = main(["demo"])
    output = capsys.readouterr().out
    assert code == 0
    assert "RESULT: PASS" in output
    assert "CONSENSUS" in output
    assert "DISPUTED" in output


def test_evaluate_passes(capsys) -> None:
    code = main(["evaluate"])
    output = capsys.readouterr().out
    assert code == 0
    assert '"all_offline_checks_pass": true' in output


def test_index_prints_hash(capsys) -> None:
    code = main(["index", "--metric", "deposit_total"])
    output = capsys.readouterr().out
    assert code == 0
    assert '"result_hash": "0x' in output
    assert '"value": "750"' in output
