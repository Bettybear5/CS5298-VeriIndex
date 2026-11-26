# VeriIndex: A Verifiable Historical Event Indexer on Lyquor

**Bettybear5**  
Department of Computer Science, City University of Hong Kong  
CS5298 Final Project

> **Status.** The report includes the problem analysis, design,
> reference-implementation results, the single-node Lyquid devnet run, and the
> evaluation plan. The direct registry path is verified; the oracle two-phase
> update path is implemented but not validated on a single-node committee.
> External-user testing and instructor approval remain pending.

## Abstract

Historical on-chain analytics are usually produced by trusted off-chain
indexers. A consumer can see the reported value but cannot easily check who
computed it, over which block range, or whether independent nodes agree.
VeriIndex is a Lyquor application that turns a historical range query into a
small, auditable protocol: independent nodes fetch the same logs, compute a
canonical metric, propose the result hash to a Lyquid oracle committee, and a
quorum-backed commitment is recorded in network state. This report describes the problem, the protocol, a runnable
reference implementation, the Sepolia-facing contracts, and an evaluation that
includes a deliberately lying node. The reference evaluation passes
determinism and tamper checks. A single-node Lyquid devnet run verifies the
direct registry path (`index_local -> submit_result -> get_result`); the
multi-node oracle update path and the external-user study remain future work.

## 1. Problem Analysis

### 1.1 The trust problem in historical indexing

Decentralized applications increasingly depend on historical on-chain data:
trading volume over a period, total value locked at a past block, the number of
unique users of a contract, or the event history behind an AI agent's input.
The data itself is public, but producing a usable aggregate is not free. A
service must scan logs, decode events, filter by contract and range, and compute
a result.

Today this work is usually delegated to an off-chain indexer such as The Graph
or Dune. These systems are valuable, but the consumer receives a result without
a compact way to verify:

- which exact block range was used;
- whether the computation was performed as claimed;
- whether independent operators agree;
- whether one compromised operator changed the answer.

Oracles such as Chainlink are optimized for delivering current values, not for
arbitrary historical range queries. UMA's optimistic oracle can handle disputes,
but it is slow and human-checked. ZK coprocessors can prove a computation, but
the proving cost is high for simple analytics. The gap is a lightweight,
auditable middle ground for historical aggregates.

### 1.2 Target users and scenario

The primary users are:

1. DeFi protocols that need historical volume or TVL for rewards, risk limits,
   or dashboards.
2. On-chain AI or agent applications that need trustworthy historical inputs.
3. Auditors and analysts who need to check a reported metric.
4. Consumer contracts that want to read a result without running an indexer.

A concrete scenario: a protocol wants the total value deposited into
`EventSource` between blocks 5,000,000 and 5,010,000 on Sepolia. A single
indexer can return `750`, but the consumer cannot tell whether that number came
from the requested range or from a different query. VeriIndex returns the value
together with a canonical result, a hash, independent oracle proposals, and a
quorum-backed network-state commitment.

### 1.3 Practical value

The value is not a new token or a faster indexer. It is **auditability at low
cost**. The full history remains off chain; only a 32-byte hash and a small
metadata record go on chain. A consumer can fetch the full result from any node
and check that its hash matches the on-chain record. If one node lies, the
disagreement is visible instead of silent.

## 2. Original Contribution

The contribution is a protocol and a reproducible implementation, not a copy of
an official example:

1. **Historical range queries with multi-node re-execution.** The unit of work is
   a `(contract, metric, fromBlock, toBlock)` query, not a latest-value feed.
2. **Canonical result format.** Sorted keys, compact JSON, lowercase addresses,
   decimal strings for integers, and a fixed schema make independent
   implementations comparable byte-for-byte.
3. **Oracle-backed proposals and quorum.** Each node proposes the result hash
   to the Lyquid oracle; the aggregate step groups by hash and records dissent.
4. **Hash-only on-chain commitment.** The registry stores the result hash and
   metadata, not the full result, keeping gas low.
5. **Tamper-oriented evaluation.** The evaluation includes a lying node and a
   strict-threshold dispute case, not only happy paths.

Reused components include the official LDK template, standard Solidity/Ethereum
tooling, and open-source Python libraries. Those are clearly separated from the
contribution in Section 7.

## 3. Technical Design

### 3.1 Architecture

```text
 requester / CLI / web
          |
          v
  +-------------------+       eth_getLogs        +----------------------+
  |  Lyquid indexer   | <---------------------> |  Sepolia EventSource |
  |  (3 node configs) |                         +----------------------+
  +---------+---------+
            | oracle proposals
            v
  +-------------------+       submitResult()    +----------------------+
  |  quorum aggregator| ----------------------> |  ResultRegistry.sol  |
  +---------+---------+                         +----------+-----------+
            |                                              |
            v                                              v
   comparison/report view                         consumer contracts
```

On-chain state is deliberately small: result hash, metric id, block range,
quorum, timestamp, submitter. Off-chain state contains raw logs, per-node
results, oracle proposals, and disagreement records.

### 3.2 Workflow

1. The requester submits `contract`, `metric`, `fromBlock`, `toBlock`, and a
   threshold.
2. Each node fetches logs for the range.
3. Each node computes the metric with integer arithmetic.
4. The result is canonicalized and hashed with SHA-256.
5. Each node publishes its proposal to the Lyquid oracle group.
6. The oracle aggregate groups proposals by hash and requires the threshold.
7. If consensus is reached, the result hash is written to `ResultRegistry`.
8. A consumer reads the on-chain record and checks it against the full result.

### 3.3 Canonical result

```json
{
  "schema_version": 1,
  "chain_id": 11155111,
  "contract": "0xabc0000000000000000000000000000000000001",
  "metric": "deposit_total",
  "from_block": 5000000,
  "to_block": 5010000,
  "event_count": 6,
  "value": "750"
}
```

`value` is a decimal string, never a float. `contract` is lowercase. Keys are
sorted lexicographically in the canonical JSON. The result hash is
`sha256(canonical_json)`.

### 3.4 Quorum rules

- The demo uses 2-of-3.
- Group valid proposals by result hash.
- `CONSENSUS` if a group reaches the threshold.
- `DISPUTED` if no group reaches the threshold.
- `INSUFFICIENT` if fewer than the threshold valid proposals exist.
- The outcome lists agreeing, dissenting, and invalid nodes.

### 3.5 Trust assumptions

Trusted: the registry owner/authorized submitter, at least `threshold`
independent honest nodes, and the canonicalization rules. Not solved: a
malicious majority, a single RPC lying to every node, reorgs after recording,
and the absence of economic stake or slashing. Quorum is evidence of agreement,
not a cryptographic proof of correctness.

## 4. Implementation

### 4.1 Repository

```text
contracts/   EventSource.sol, ResultRegistry.sol, Foundry tests, deploy script
reference/   Python reference indexer, attestation, quorum, CLI, tests
lyquid/      Lyquid crate for LDK 0.8.4 (oracle two-phase + registry)
scripts/     reproduce.sh, run_demo.sh, deploy_sepolia.sh
docs/        scope, architecture, evaluation plan, demo script, checklist
report/      this report and evidence
```

The public repository is: https://github.com/Bettybear5/CS5298-VeriIndex

### 4.2 Contracts

`EventSource` emits `Deposit`, `Withdraw`, and `Swap` events. It is intentionally
small; it is an event fixture, not a production vault.

`ResultRegistry` stores one `Result` per `(metricId, fromBlock, toBlock)` key.
It has an owner, an authorized-submitter allowlist, a `submitResult` function, a
`getResult` view, and events for submission and update. Re-submission overwrites
the record and emits both the old and new hash for audit.

### 4.3 Reference indexer

The Python reference is a deterministic oracle for the evaluation. It:

- loads a JSON log fixture;
- filters by contract and inclusive block range;
- deduplicates by `(transactionHash, logIndex)`;
- computes `event_count`, `deposit_total`, `withdraw_total`, `swap_volume`, or
  `unique_senders`;
- builds the canonical result;
- signs the hash with an Ethereum test key;
- aggregates proposals with the quorum rules.

### 4.4 Lyquid adapter

The Lyquid crate mirrors the same logic: canonical JSON and SHA-256, metric
computation, `eth_getLogs` fetching over the host HTTP capability, and the
official LDK oracle two-phase flow. Each node calls `propose`; `aggregate`
requires a quorum of matching hashes; the certified `update` method writes a
`ResultRecord` into network state. `get_result` and `has_result` expose the
registry to consumers. The integration steps are documented in
`lyquid/README.md`.

The single-node devnet run used:

- `lyquid_id`: `Lyquid-ahjg4huwvban3bvhxue7rcbaw4mnltwyolhqa`
- contract: `0x0165878a594ca255338adfa4d48449f69242eb8f`
- committee node: `Node-ve3tav5jw5ico7or34gcb6ni7rtmd35uokriuijygabd3tsltd7fj6ia`
- direct-path value: `0`
- event count: `0`
- block range: `12210249..12211249`
- result hash: `0x7bfd1cccbe002850c39035c2f624b27f04021791ce23e4bbe880e37dbc741431`

The verified path is `index_local` (fetch logs and canonicalize), then
`submit_result` (network-state registry write), then `get_result`. The run
returned `get_result_count = 1`, `has_result = true`, and the JSON record
quoted in Section 5.5.

The oracle two-phase path (`report_result -> propose -> aggregate -> update`)
is implemented but did not complete on the single-node committee: the run
reached `propose` but produced no `aggregate`/`update` certificate. The
validated submission therefore uses the direct registry path; multi-node
oracle validation is future work.

## 5. Evaluation and Results

### 5.1 Objectives and setup

The offline evaluation checks determinism, correctness against an independent
recomputation, tamper detection, and the reference latency. The fixture contains
10 logs across three contracts/ranges, including one duplicate log and one
out-of-range log. The target contract is `0xAbC...0001`, range
5,000,000–5,010,000.

The reference runs on Python 3.11+ with `eth-account` and `pytest`. The contract
tests require Foundry. The single-node Lyquid direct registry path was executed
in GitHub Actions against the local Lyquor devnet. The Sepolia-facing
`ResultRegistry` mirror was not deployed; the verified registry is the Lyquid
network state.

### 5.2 Results

| Check | Result | Evidence |
|---|---|---|
| Unit tests | 16 passed | `reference/tests` |
| Determinism | 5/5 identical hashes; reversed input identical | `report/evidence/evaluation.json` |
| Correctness | 750 = independent recomputation | `report/evidence/evaluation.json` |
| Tamper detection (2-of-3) | `CONSENSUS`, correct value, lying node in dissent | `reference/tests/test_quorum.py` |
| Strict threshold (3-of-3) | `DISPUTED`, no selected hash | `reference/tests/test_quorum.py` |
| Demo | `RESULT: PASS` | `python -m veriindex.cli demo` |
| Lyquid devnet, direct path | `get_result_count=1`, `has_result=true`, JSON returned | `report/evidence/lyquid-run-direct.json` |
| External user study | Not completed in this draft | Documented as a limitation |
| Reference latency | ~0.006 ms per query on the fixture | microbenchmark, not production |

The selected result hash for the fixture is
`0x5105d284ff7de6b8fc177447a27366c5af8d170bf12a8560a357bfa3468b7c0b`.

### 5.3 Interpretation

The results support three claims: the canonicalization is deterministic, the
metric can be checked against an independent implementation, and a single lying
node cannot change a 2-of-3 result while remaining invisible. They do not support
claims about production throughput, cryptographic correctness, or resistance to
a malicious majority. The microbenchmark is intentionally reported as a
reference-path latency, not as a system-level performance claim.

### 5.4 User testing

The external-user study has not been completed in the current submission. The
reproduction workflow was checked with the Python test suite, the CLI demo, and
the GitHub Actions single-node Lyquid run. A three-user study remains required;
it is not claimed as completed here.

### 5.5 On-chain and Lyquid results

The clean single-node run produced:

```text
lyquid_id: Lyquid-ahjg4huwvban3bvhxue7rcbaw4mnltwyolhqa
contract:  0x0165878a594ca255338adfa4d48449f69242eb8f
node:      Node-ve3tav5jw5ico7or34gcb6ni7rtmd35uokriuijygabd3tsltd7fj6ia
range:     12210249..12211249
submit tx: 0x109ed399a05dfb3208f1c8a2e0f4a914196a28b11d8d7d08f9bc92898925c1cb
count:     1
has_result:true
```

`get_result` returned:

```json
"{\"result_hash\":\"0x7bfd1cccbe002850c39035c2f624b27f04021791ce23e4bbe880e37dbc741431\",\"contract\":\"0xabc0000000000000000000000000000000000001\",\"metric\":\"deposit_total\",\"from_block\":12210249,\"to_block\":12211249,\"event_count\":0,\"value\":\"0\",\"quorum\":1,\"timestamp\":12,\"signers\":[]}"
```

The timestamp is the Lyquor block number, produced by `chain_pos().block()`,
not wall-clock time. The empty signer list is expected for the direct
`submit_result` path; signers are populated by the oracle `update` path.

The oracle path is not claimed as verified. In the single-node run it reached
`propose` but did not produce `aggregate/update`, so no oracle-certified record
was written. The direct path is the supported single-node result.

## 6. Limitations and Reflection

- **Quorum is not proof.** A malicious majority or colluding nodes can sign a
  wrong result. The design makes disagreement visible, but it does not eliminate
  trust.
- **RPC centrality.** If all nodes use one RPC provider, that provider can lie
  consistently. A second independent RPC is the next step.
- **Reorgs.** The prototype does not detect a reorg after recording. A block hash
  commitment and a re-check window are needed.
- **Scope.** Only one contract family, one chain, and five simple metrics are
  implemented. This is deliberate for a solo project.
- **Evaluation scale.** The fixture is small; no production-scale throughput is
  claimed.
- **Usability and user testing.** The CLI is minimal, and no external-user
  study was completed before this draft. A three-user study is still required
  to evaluate whether the workflow is understandable to non-authors.
- **Single-node oracle path.** The two-phase `report_result -> propose ->
  aggregate -> update` path is implemented but did not complete on the
  single-node committee. The validated run uses direct `submit_result`; a
  multi-node oracle run is the next step.

Concrete next step: add a second independent RPC and a reorg check that stores
the block hash alongside the result hash, then re-run the tamper evaluation.

## 7. Contributions and Attribution

This is a solo project. The course handout requires three students unless the
instructor approves an exception. **Instructor approval: `[TBD: date and
evidence]`.** All design, implementation, evaluation, and writing were done by
Bettybear5.

External resources: the official Lyquor whitepaper/litepaper/LDK, Ethereum
Sepolia, Solidity, Foundry, Python, `eth-account`, and the libraries listed in
the repository. AI tools are recorded in Section 8 and in
`docs/ai-use-log.md`.

## 8. AI Use Statement

I used an AI assistant (opencode) to extract the assignment text, organize the
project plan, scaffold the reference implementation and tests, and edit the
language of this report. I reviewed the generated code by running the test
suite, the CLI demo, and the offline evaluation, and I checked every technical
claim against the implementation and the cited sources. I am responsible for the
correctness of the submitted work.

## References

[1] Lyquor Network. Whitepaper, Litepaper, and Lyquid Development Kit (LDK).
Course materials, 2026.

[2] The Graph. "About The Graph." https://thegraph.com/docs/, accessed 2026.

[3] Chainlink. "Off-Chain Reporting." https://docs.chain.link/, accessed 2026.

[4] UMA. "Optimistic Oracle." https://docs.uma.xyz/, accessed 2026.

[5] Brevis. "Guide to Brevis." https://docs.brevis.network/, accessed 2026.

[6] Ethereum Foundation. "Sepolia Testnet." https://ethereum.org/en/developers/docs/networks/, accessed 2026.

[7] Solidity Documentation. https://docs.soliditylang.org/, accessed 2026.

[8] Foundry Book. https://book.getfoundry.sh/, accessed 2026.

## Appendix A: Reproduction commands

```bash
bash scripts/reproduce.sh
```

Expected: 16 tests pass, the demo prints `RESULT: PASS`, and
`report/evidence/evaluation.json` reports `all_offline_checks_pass: true`.
