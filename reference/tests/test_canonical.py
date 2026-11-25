from __future__ import annotations

from veriindex.canonical import canonical_json, result_hash


def test_canonical_json_is_sorted_and_compact() -> None:
    result = {"b": 2, "a": 1, "c": {"z": 3, "y": 4}}
    assert canonical_json(result) == '{"a":1,"b":2,"c":{"y":4,"z":3}}'


def test_result_hash_is_stable_and_order_independent() -> None:
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert result_hash(a) == result_hash(b)
    assert result_hash(a).startswith("0x")
    assert len(result_hash(a)) == 66


def test_unicode_is_preserved() -> None:
    result = {"summary": "交易量"}
    assert "交易量" in canonical_json(result)
