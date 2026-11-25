# Report outline (6–10 pages main content)

The cover page, references, and appendices do not count toward the six-page
minimum. Recommended main-content length: 7–9 pages.

## 1. Problem Analysis (1.5 pages)

- Define the historical-indexing trust problem.
- Target users: DeFi protocols, on-chain AI agents, auditors, consumer contracts.
- Concrete scenario: deposit total over a block range.
- Limitations of The Graph, Dune, Chainlink, UMA, ZK coprocessors.
- Practical/commercial value: lower trust in a single indexer; auditable
  historical facts; reusable by other contracts.
- Cite Web3/indexing/oracle literature and the Lyquor materials.

## 2. Original Contribution (0.75 page)

- Historical range query, not just latest value.
- Multi-node deterministic re-execution and oracle-certified proposals.
- Canonical result format and hash.
- Quorum with explicit dissent.
- On-chain commitment with low storage cost.
- Clearly separate reused components (LDK template, OpenZeppelin-style
  patterns, Ethereum tooling) from your contribution.

## 3. Technical Design (2 pages)

- Architecture diagram.
- Service responsibilities and node hosting.
- On-chain vs off-chain state.
- Request/compute/canonicalize/sign/aggregate/record/read workflow.
- Result and proposal schemas.
- Quorum rules and failure handling.
- Threat model and trust assumptions.
- Justify design choices: hash-only storage, integer arithmetic, 2-of-3 quorum,
  no ZK, no token.

## 4. Implementation (2 pages)

- Repository layout.
- `EventSource` and `ResultRegistry` contracts and interfaces.
- Lyquid adapter: how the Rust modules map to the LDK service.
- Canonicalization algorithm and hash.
- Metric implementation.
- Attestation signing/verification.
- Quorum algorithm.
- External services: Sepolia RPC, faucet, block explorer.
- Important code excerpts and pseudocode.
- Link to the public GitHub repository.

## 5. Evaluation and Results (1.5 pages)

- Objectives and scenarios E1–E6 from `docs/evaluation-plan.md`.
- Test environment: OS, Python/Rust versions, Sepolia chain id, block range.
- Results table: determinism, correctness, tamper detection, dispute, registry,
  user task completion.
- Latency and gas numbers.
- What the results support and what they do not.
- Include raw evidence paths.

## 6. Limitations and Reflection (0.5 page)

- Quorum is not a proof; malicious majority and shared RPC are unsolved.
- Reorg handling is basic.
- Only one metric family and one chain.
- Small fixture; no production-scale benchmark.
- UI is minimal.
- Concrete next step: add reorg detection and a second independent RPC, or add
  an optimistic dispute window.

## 7. Contributions and Attribution (0.25 page)

- State: solo project, instructor approval date, all work by Bettybear5.
- List external code/resources: LDK template, Solidity/Foundry, Python packages,
  course materials, AI tools.
- Do not claim official examples as original.

## 8. AI Use Statement (0.25 page)

- Tool name and version.
- Tasks supported: text extraction, notes, code scaffolding, language editing.
- How output was reviewed: tests, manual code review, comparison with papers.
- Who is responsible: the student.

## References

Use a consistent style (IEEE or ACM). Include:

- Lyquor whitepaper/litepaper/LDK.
- The Graph, Chainlink OCR, UMA, Brevis/ZK coprocessor materials.
- At least two academic papers on oracles/indexing/verification.
- Ethereum Sepolia and Solidity documentation.

## Appendices (not counted)

- Full contract source.
- CLI transcript.
- User-study questions.
- Additional evaluation logs.
