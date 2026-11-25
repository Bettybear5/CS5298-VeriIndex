# VeriIndex: A Verifiable Historical Event Indexer on Lyquor

CS5298 final project. VeriIndex lets a consumer request a metric over a historical
block range (for example, the total deposited value of a contract), has multiple
Lyquor nodes independently recompute the metric, and records a quorum-backed
result hash on chain.

> **Status.** This repository contains a runnable offline reference
> implementation, the Sepolia-facing Solidity contracts, and a Lyquid crate
> targeting the official LDK 0.8.4. The reference implementation is what the
> tests and the reproducibility script execute. A single-node Lyquid devnet run
> verifies the direct registry path (`index_local -> submit_result ->
> get_result`); the oracle two-phase update path is implemented but not validated
> on a single-node committee. See `lyquid/README.md` and
> `report/evidence/lyquid-run-direct.json`.

## Why this project

Historical on-chain analytics are usually served by trusted off-chain indexers.
A consumer can see the reported value, but cannot easily check who computed it,
which block range was used, or whether independent nodes agree. VeriIndex turns
that into a small, auditable protocol:

1. A requester specifies a contract, block range, and metric.
2. Independent nodes fetch the same logs and compute the same canonical result.
3. Nodes sign the result hash.
4. A quorum of matching signatures becomes a shared fact.
5. Only the result hash and metadata are stored on chain; the full history stays
   off chain.

This is a good fit for Lyquor because the computation is naturally off chain,
the result is small, and independent nodes can vouch for it before an on-chain
consumer reads it.

## Architecture

```text
 requester / CLI / web
          |
          v
  +-------------------+       logs / RPC        +----------------------+
  |  Lyquid indexer   | <---------------------> |  Sepolia EventSource |
  |  (Rust, 3 nodes)  |                         +----------------------+
  +---------+---------+
            | signed attestations
            v
  +-------------------+       submitResult()    +----------------------+
  |  quorum aggregator| ----------------------> |  ResultRegistry.sol  |
  +---------+---------+                         +----------+-----------+
            |                                              |
            v                                              v
   comparison/report view                         consumer contracts
```

On-chain state: result hash, metric id, block range, quorum size, timestamp.
Off-chain state: raw logs, per-node results, signatures, disagreement records.

## Quick start: runnable reference implementation

The reference implementation is intentionally dependency-light so that the
evaluation is reproducible on any machine with Python 3.11+.

```bash
cd reference
python3 -m pip install -e .
python3 -m pytest -q
python3 -m veriindex.cli demo
```

`demo` runs three simulated nodes over the same fixture, tampers with one node,
and prints the individual attestations plus the quorum outcome. It exits with a
non-zero status if the tampered node is not detected.

Run the full reproducibility check from the repository root:

```bash
bash scripts/reproduce.sh
```

## Contracts

Solidity sources are under `contracts/src`:

- `EventSource.sol`: a small event emitter used as the indexing target.
- `ResultRegistry.sol`: stores one result per `(metric, fromBlock, toBlock)` key,
  with an authorized-submitter allowlist and a quorum field.

The contracts are written for Solidity 0.8.24 and Foundry. If Foundry is not
installed, the reference tests still run; contract compilation is a separate
step.

```bash
cd contracts
forge test
forge script script/Deploy.s.sol --rpc-url "$SEPOLIA_RPC_URL" --broadcast
```

Never commit `.env` or a real private key. Use a dedicated test key funded from a
Sepolia faucet.

## Lyquid integration

The Rust crate in `lyquid/` mirrors the reference types:

- canonical JSON and SHA-256 result hash;
- metric computation;
- quorum grouping;
- oracle proposal/aggregate flow using the official LDK oracle group;
- `eth_getLogs` fetching through the host HTTP capability;
- certified `update` and read-only `get_result` network methods.

See `lyquid/README.md` and `docs/ldk-runbook.md` for the exact commands. The short version:

1. Start the official LDK Docker devnet.
2. Add `lyquid/` to the LDK workspace (or build it standalone with the same
   toolchain).
3. Build the WASM target and deploy with `shaker` per the LDK tutorial.
4. Configure the oracle committee with `configure_committee(node_ids)`.
5. Set each node's RPC with `set_rpc_url(...)`, then call
   `report_result(contract, metric, from, to)` and read with `get_result(...)`.
6. The Lyquid network state is the primary registry. `ResultRegistry.sol` is an
   optional Sepolia anchor for external consumers.

## Repository layout

```text
contracts/          Solidity event source, registry, tests, deploy script
reference/          Runnable Python reference indexer, quorum, CLI, tests
lyquid/             Lyquid crate for LDK 0.8.4 (oracle two-phase + registry)
scripts/            Reproduce, demo, deploy helpers
docs/               Scope, architecture, evaluation plan, report outline
report/             Report draft and evidence placeholders
demo/               Demo script and recording checklist
```

## Evaluation

The evaluation plan is in `docs/evaluation-plan.md`. The reference script
checks:

- deterministic canonicalization and hashing;
- metric correctness against an independent re-computation;
- tamper detection with one lying node;
- quorum behavior when no majority exists;
- end-to-end demo with stable output.

## Single-person group

The course handout requires a three-student team unless the instructor approves
an exception. **Obtain written approval before submission** and keep the approval
with the project records. The report's contribution section must state that the
project is solo and cite the approval date.

## AI use

AI tools used during development must be listed in `docs/ai-use-log.md` and in
the report's AI Use Statement, including the task supported and how the output
was reviewed. Do not submit unreviewed generated code or claims.

## License

MIT. See `LICENSE`.
