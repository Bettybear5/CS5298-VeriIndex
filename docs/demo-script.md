# Eight-minute demo script

Record the demo in advance. Keep the terminal and browser at a readable zoom.
Have a fallback recording in case the live run fails.

## 0:00–1:00 Problem and users

- Historical on-chain metrics are served by trusted indexers.
- Consumers cannot tell who computed a value or whether independent nodes agree.
- Target users: DeFi protocols, on-chain AI agents, auditors, consumer contracts.

## 1:00–2:00 Existing limitations and contribution

- The Graph/Dune: rich but off-chain trust.
- Chainlink: latest values, not arbitrary historical ranges.
- ZK: strong but costly for simple analytics.
- Contribution: deterministic multi-node re-execution + oracle-certified
  proposals + quorum-backed network-state hash.

## 2:00–3:30 Architecture

- Show the diagram from `docs/architecture.md`.
- Explain on-chain vs off-chain state.
- Explain the request → fetch → compute → canonicalize → sign → quorum → record
  → read flow.
- State the trust assumption: 2-of-3 independent nodes, not a proof.

## 3:30–5:00 Implementation and results

- Show the repo layout.
- Show `ResultRegistry.sol` interface.
- Show the canonicalization rule and hash.
- Show the tamper test result: one lying node, quorum still selects the correct
  result and records the dissenter.
- Show correctness and latency table.

## 5:00–8:00 Prerecorded demo

1. Start the local devnet and three nodes.
2. Deploy `EventSource` and `ResultRegistry` (or show the already deployed
   Sepolia addresses).
3. Emit a few `Deposit`/`Swap` events.
4. Run the CLI request for `deposit_total`.
5. Show three oracle proposals with matching hashes.
6. Run the same request with one tampered node.
7. Show `CONSENSUS`, correct value, and the dissenting node.
8. Submit the result to `ResultRegistry`.
9. Read the result from the registry.
10. Show the dashboard/CLI reading the on-chain commitment.

## Q&A preparation

Be ready to answer:

- Why 2-of-3 and not 1-of-3?
- What happens if the majority colludes?
- How do you handle reorgs?
- Why hash only, and where is the full result stored?
- What is Lyquor-specific here versus a normal off-chain service?
- What would you do with more time?
