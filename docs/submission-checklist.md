# Submission checklist

## Eligibility

- [ ] Instructor approved the solo group in writing.
- [ ] Deadline confirmed on Canvas (handout says Nov 19, 12:00 PM).
- [ ] Team/group registration handled or exception documented.

## Repository

- [ ] Public GitHub repository URL added to the report.
- [ ] README explains build, run, reproduce, and verify.
- [ ] `scripts/reproduce.sh` works from a clean checkout.
- [ ] Tests pass (`pytest`; contract tests if Foundry is available).
- [ ] `.env` and private keys are not committed.
- [ ] Sepolia contract addresses and transaction hashes are recorded.
- [ ] License included.
- [ ] No copied official example presented as original work.

## Implementation

- [ ] `EventSource.sol` deployed and emits events.
- [ ] `ResultRegistry.sol` stores and returns results.
- [ ] Lyquid adapter wired to the official LDK template.
- [ ] Three independent node configurations.
- [ ] Quorum and dissent recorded.
- [ ] Tamper test demonstrates one lying node cannot change the result.
- [ ] CLI or web view shows the full workflow.

## Evaluation

- [ ] E1 determinism evidence.
- [ ] E2 correctness evidence.
- [ ] E3 tamper evidence.
- [ ] E4 registry evidence.
- [ ] E5 end-to-end evidence.
- [ ] E6 user testing with at least three external users.
- [ ] Results table and limitations in the report.

## Report

- [ ] Main content at least 6 pages (cover/references/appendices excluded).
- [ ] All required sections present.
- [ ] Architecture diagram and workflow figure.
- [ ] Pseudocode or code excerpts for key algorithms.
- [ ] GitHub URL included.
- [ ] AI Use Statement included.
- [ ] Solo contribution and instructor approval stated.
- [ ] References formatted consistently.
- [ ] PDF exported and checked for layout/typos.

## Demo

- [ ] Eight-minute recording: 5 minutes presentation + 3 minutes demo.
- [ ] Demo shows the complete workflow and observable results.
- [ ] Fallback recording available.
- [ ] All Q&A topics rehearsed.
- [ ] Demo ZIP prepared.

## Final

- [ ] Report PDF uploaded.
- [ ] Demo ZIP uploaded.
- [ ] Submission confirmed on Canvas.
- [ ] Keep a local copy of all artifacts and evidence.
