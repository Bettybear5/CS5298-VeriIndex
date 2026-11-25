# Evaluation plan

## Objectives

1. Check that the indexer is **deterministic**: the same logs always produce the
   same canonical result and hash.
2. Check that the metric is **correct** against an independent re-computation.
3. Check that a **lying node cannot change** the quorum result.
4. Check that the on-chain registry stores and returns the expected commitment.
5. Check that an external user can follow the README and complete the workflow.

## Test scenarios

### E1. Determinism and canonicalization

- Run the indexer five times on the same fixture.
- Assert identical canonical JSON and identical `result_hash`.
- Reorder input logs and assert the result is unchanged.
- Change whitespace in the input and assert the result is unchanged.
- Add a duplicate log and assert it is handled according to the metric rule
  (deduplicate by `(tx_hash, log_index)`).

Evidence: `reference/tests/test_canonical.py`, captured output in
`report/evidence/e1-determinism.txt`.

### E2. Metric correctness

- Load the fixture.
- Compute `event_count`, `deposit_total`, and `unique_senders` with the
  reference implementation.
- Recompute the same metrics with a separate, minimal script that does not import
  the indexer.
- Assert exact equality.

Evidence: `reference/tests/test_metrics.py`, `report/evidence/e2-correctness.txt`.

### E3. Tamper detection

- Create three attestations from three test keys.
- Change one attestation's value and re-sign it with a valid key.
- Run quorum with threshold 2.
- Assert:
  - outcome is `CONSENSUS`;
  - the correct result is selected;
  - the tampered node appears in `dissenting_nodes`;
  - the tampered hash is not the selected hash.

Also test threshold 3: the same tampering must produce `DISPUTED`, and no
on-chain submission should occur.

Evidence: `reference/tests/test_quorum.py`, `report/evidence/e3-tamper.txt`.

### E4. On-chain registry

- Deploy `ResultRegistry` to a local EVM or Sepolia.
- Submit a result from an authorized address.
- Read it back and assert all fields.
- Submit from an unauthorized address and assert revert.
- Submit the same key twice and assert the documented update rule.

Evidence: `contracts/test/ResultRegistry.t.sol`, transaction hashes in
`report/evidence/e4-registry.txt`.

### E5. End-to-end workflow

- Start from a clean checkout.
- Run `bash scripts/reproduce.sh`.
- Run the CLI demo.
- Confirm the printed quorum result matches the fixture's expected value.
- Confirm the demo exits non-zero when the tampered node is the majority.

Evidence: `report/evidence/e5-e2e.txt` and the demo recording.

### E6. User testing

- Recruit three users outside the team.
- Give them only the README and a 10-minute task:
  "Run the demo, change the metric to `event_count`, and report the result."
- Record completion time, errors, and suggestions.
- Implement at least one fix or document why it is out of scope.

Evidence: `report/evidence/e6-user-study.md`.

## Metrics

| Metric | Definition | Target |
|---|---|---|
| Determinism | Identical hashes across five runs | 5/5 |
| Correctness | Matches independent recomputation | 100% on fixtures |
| Tamper detection | Tampered node not selected under threshold 2 | 100% |
| Dispute behavior | No selection when threshold cannot be met | 100% |
| Reproducibility | Clean run succeeds from README | 1/1 |
| User task completion | External users complete the task | 3/3 or documented blocker |
| Latency | Time to index a range in the reference fixture | Report only |

## Baselines

- **Single-node indexer**: one node computes and signs; no quorum. This is the
  baseline that VeriIndex improves on.
- **Direct RPC scan**: a separate script that scans logs directly and computes
  the same metric; used as ground truth, not as a competing product.
- **Trusted indexer (qualitative)**: The Graph/Dune-style off-chain result; not
  run locally, but discussed in the report as the status quo.

## Procedure

1. Create a clean virtual environment.
2. Install the reference package.
3. Run `pytest`.
4. Run `python -m veriindex.cli demo`.
5. Run the evaluation script and save output.
6. Deploy the contracts (local or Sepolia) and run the registry test.
7. Run the user study and record results.
8. Put all evidence under `report/evidence/`.

## What not to claim

- Do not claim cryptographic correctness or ZK-level guarantees.
- Do not claim production-scale throughput from a small fixture.
- Do not claim that quorum equals truth; it is a trust assumption.
- Do not compare latency with The Graph or Dune without running them under the
  same workload.
