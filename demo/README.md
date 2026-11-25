# Demo recording checklist

Target length: 8 minutes (5 minutes presentation + 3 minutes demo).

## Before recording

- [ ] Terminal font size readable at 1080p.
- [ ] `bash scripts/reproduce.sh` passes.
- [ ] Sepolia contracts deployed and addresses copied.
- [ ] Three node configs are visible in the terminal or a config file.
- [ ] Demo fixture is fixed and does not depend on live RPC.
- [ ] Fallback recording exists.
- [ ] No private keys, `.env` values, or account identifiers on screen.

## Shot list

1. Title slide: problem, target users, one-sentence contribution.
2. Architecture slide: on-chain vs off-chain, request → quorum → registry.
3. Contract slide: `ResultRegistry.submitResult` and `getResult`.
4. Evaluation slide: determinism, correctness, tamper detection table.
5. Terminal: run `python3 -m veriindex.cli demo`.
6. Terminal: show the three attestations, the lying node, and `CONSENSUS`.
7. Terminal: show threshold 3 producing `DISPUTED`.
8. Browser/terminal: show the on-chain registry record and the matching hash.
9. Closing slide: limitations and next step.

## Q&A notes

- 2-of-3 is a demo choice, not a security proof.
- The full result stays off chain; the chain stores the hash.
- A malicious majority is out of scope.
- Reorg handling is a next step.
- The reference implementation is an oracle for evaluation, not the production
  Lyquid.
