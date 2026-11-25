"""Command-line interface for the VeriIndex reference implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .attest import sign_result
from .canonical import canonical_json, result_hash
from .evaluation import PRIVATE_KEYS, run_evaluation, write_evidence
from .indexer import build_result, load_logs
from .quorum import quorum


def _fixture() -> Path:
    return Path(__file__).resolve().parent.parent / "fixtures" / "events.json"


def _contract(logs: list[dict[str, Any]]) -> str:
    return str(logs[0]["address"])


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def command_demo(_: argparse.Namespace) -> int:
    logs = load_logs(_fixture())
    contract = _contract(logs)
    result = build_result(logs, "deposit_total", contract, 5_000_000, 5_010_000)
    expected = result["value"]

    attestations = [sign_result(result, key) for key in PRIVATE_KEYS]
    tampered = dict(result)
    tampered["value"] = str(int(tampered["value"]) + 999)
    attestations[1] = sign_result(tampered, PRIVATE_KEYS[1])

    outcome = quorum(attestations, 2)
    strict = quorum(attestations, 3)

    print("== VeriIndex reference demo ==")
    print(f"contract: {contract}")
    print(f"metric:   deposit_total")
    print(f"range:    5000000..5010000")
    print(f"expected: {expected}")
    print()
    print("== node attestations ==")
    for attestation in attestations:
        print(
            f"{attestation['node_id']}  "
            f"hash={attestation['result_hash'][:18]}...  "
            f"value={attestation['result']['value']}"
        )
    print()
    print("== quorum (threshold 2) ==")
    _print_json(outcome)
    print()
    print("== quorum (threshold 3, tampered node included) ==")
    print(f"status: {strict['status']}")

    ok = (
        outcome["status"] == "CONSENSUS"
        and outcome["selected_hash"] == result_hash(result)
        and attestations[1]["node_id"] in outcome["dissenting_nodes"]
        and strict["status"] == "DISPUTED"
    )
    print()
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def command_index(args: argparse.Namespace) -> int:
    logs = load_logs(args.logs)
    contract = args.contract or _contract(logs)
    result = build_result(
        logs,
        args.metric,
        contract,
        args.from_block,
        args.to_block,
        args.chain_id,
    )
    payload: dict[str, Any] = {
        "result": result,
        "result_hash": result_hash(result),
        "canonical_json": canonical_json(result),
    }
    if args.private_key:
        payload["attestation"] = sign_result(result, args.private_key)
    _print_json(payload)
    return 0


def command_quorum(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.attestations).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "attestations" in data:
        data = data["attestations"]
    if not isinstance(data, list):
        raise SystemExit("attestations file must contain a list")
    outcome = quorum(data, args.threshold)
    _print_json(outcome)
    return 0 if outcome["status"] != "INSUFFICIENT" else 1


def command_evaluate(args: argparse.Namespace) -> int:
    report = run_evaluation(args.logs)
    if args.evidence_dir:
        path = write_evidence(report, args.evidence_dir)
        print(f"wrote {path}")
    _print_json(report)
    return 0 if report["all_offline_checks_pass"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="veriindex")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run the three-node tamper demo")
    demo.set_defaults(func=command_demo)

    index = sub.add_parser("index", help="index a log fixture")
    index.add_argument("--logs", default=str(_fixture()))
    index.add_argument("--contract", default=None)
    index.add_argument("--metric", default="deposit_total")
    index.add_argument("--from-block", type=int, default=5_000_000)
    index.add_argument("--to-block", type=int, default=5_010_000)
    index.add_argument("--chain-id", type=int, default=11155111)
    index.add_argument("--private-key", default=None)
    index.set_defaults(func=command_index)

    q = sub.add_parser("quorum", help="aggregate an attestation file")
    q.add_argument("--attestations", required=True)
    q.add_argument("--threshold", type=int, default=2)
    q.set_defaults(func=command_quorum)

    ev = sub.add_parser("evaluate", help="run the offline evaluation")
    ev.add_argument("--logs", default=str(_fixture()))
    ev.add_argument("--evidence-dir", default=None)
    ev.set_defaults(func=command_evaluate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
