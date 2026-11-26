# VeriIndex — 8-minute presentation script

Total target: **7:45–8:00**.  
Structure: **5 minutes presentation + 3 minutes recorded demo**.

## 0:00–0:15 — Title

Good morning. I'm Bettybear5. My project is **VeriIndex**, a verifiable historical event indexer built as a Lyquid on Lyquor. In the next five minutes I will explain the problem, the design, and the verified result. Then I will show a three-minute recorded demo.

## 0:15–0:55 — The problem

Historical on-chain data is public, but the aggregate is not verifiable. A protocol asks for trading volume or TVL, and receives a number from an indexer. It cannot tell whether the indexer used the requested block range, or whether independent operators agree. If one indexer is compromised, the result changes silently. This is the trust gap VeriIndex targets.

## 0:55–1:25 — Existing approaches

The Graph and Dune are powerful, but they return an off-chain answer. Chainlink-style oracles deliver values on chain, but they are optimized for current values, not arbitrary historical ranges. ZK coprocessors can prove computation, but the proving cost is high for simple analytics. The opening is a lightweight middle ground: deterministic re-execution by independent nodes, plus a small on-chain commitment.

## 1:25–2:05 — Contribution

The contribution has four parts. First, the unit of work is a historical range query, not a latest-value feed. Second, the result has a canonical JSON form, so independent implementations can compare byte-for-byte. Third, nodes produce signed proposals and the protocol records quorum and dissent. Fourth, only a hash and metadata go on chain, so the cost is low. The verified path in this project is `index_local`, `submit_result`, and `get_result`. I will be explicit later about the oracle path that is implemented but not validated on a single node.

## 2:05–2:50 — Architecture

This is the architecture. The requester asks for a contract, a metric, and a block range. The Lyquid indexer fetches logs from Sepolia, computes the metric, canonicalizes the result, and hashes it. Independent nodes can produce proposals. The quorum result is committed to Lyquid network state. Optionally, the same hash can be mirrored to a small Sepolia registry for external consumers. The important boundary is that the chain stores only a compact commitment, not the full history.

## 2:50–3:25 — Workflow

The workflow is deliberately simple. The requester supplies a range. Each node fetches logs, computes an integer metric, and produces a canonical JSON object. The result hash is SHA-256 over that canonical form. In the multi-node design, nodes sign the hash and a quorum is formed. The registry stores the hash and metadata, and a consumer reads the JSON back. The timestamp is the Lyquor block number, not wall-clock time, which is deterministic.

## 3:25–3:55 — Implementation

Implementation is split into three pieces. The Python reference is the deterministic oracle for evaluation. The Rust Lyquid targets LDK 0.8.4 and contains the oracle code and the registry. The Solidity contracts are the Sepolia-facing event source and an optional result registry. This separation lets me test the protocol logic independently from the Lyquid deployment.

## 3:55–4:30 — Results

The reference implementation passes sixteen tests, including determinism, correctness against an independent recomputation, and tamper detection. The 2-of-3 case reaches consensus while recording the lying node as dissent. The 3-of-3 case is disputed. On the Lyquid side, the clean single-node run returned count one, has-result true, and a JSON record with hash `0x7bfd1c`, value zero, quorum one, and block timestamp twelve. The oracle update path did not complete on a single node, and I do not claim it as verified.

## 4:30–5:00 — Limitations and conclusion

The honest limitation is scope. I verified deployment, the direct registry path, canonicalization, hashing, and the tamper evaluation. I did not validate the oracle update path on a single node, I did not complete an external user study, and I did not run multiple independent nodes. The conclusion is that VeriIndex turns a historical query into a small auditable fact, and the direct path already produces a real readable Lyquid record. Multi-node oracle validation is the next step.

## 5:00–8:00 — Recorded demo

I will now switch to the recorded demo. It starts the single-node Lyquor devnet and deploys VeriIndex. The deploy output gives the Lyquid ID and the sequencer contract. It then calls `index_local` over a recent Sepolia range. The proposal contains the canonical result and its hash. Next, `submit_result` writes the record into Lyquid network state. The transaction hash is `0x109ed3`. Finally, `get_result_count` returns one, `has_result` returns true, and `get_result` returns the JSON record with value zero, quorum one, and block timestamp twelve. The oracle update path is not shown as a success because it did not complete on a single-node committee.

## Q&A preparation

- **Why 2-of-3?** It is the demo quorum for the reference; the live single-node run uses one node.
- **What does the chain store?** Only the result hash and metadata; the full result stays off chain.
- **Is quorum a proof?** No. A malicious majority can collude; the design makes dissent visible, not impossible.
- **Why is the timestamp a block number?** `systime` is only valid in instance functions; network-state writes use `chain_pos().block()`.
- **Why is the oracle path not shown?** It is implemented, but the single-node proposal aggregation did not produce a certified update. The direct registry path is the verified result.
