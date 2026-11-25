# Project scope: VeriIndex

## One-sentence pitch

VeriIndex is a Lyquor application that lets a consumer request a historical
on-chain metric, has independent Lyquor nodes recompute and sign the result,
and records the quorum-backed result hash on chain so other contracts can read
a verifiable fact instead of trusting a single indexer.

## Problem

Historical on-chain analytics (volume, TVL, active users, event counts) are
usually produced by off-chain indexers. Consumers see the result but cannot
easily verify:

- who computed it;
- over which exact block range;
- whether independent nodes agree;
- whether a single compromised indexer changed the answer.

Oracles usually provide the latest value, not an auditable historical
computation. ZK coprocessors can prove computations, but at a proving cost that
is unnecessary for many analytics queries.

## Target users

1. DeFi protocols that need historical volume or TVL for rewards, risk limits,
   or dashboards.
2. On-chain AI/agent applications that need trustworthy historical inputs.
3. Auditors and analysts who need to check a reported metric.
4. Consumer contracts that want to read a result without running an indexer.

## Concrete use case

A protocol wants to know the total value deposited into `EventSource` between
blocks 5,000,000 and 5,010,000 on Sepolia. The requester submits:

```json
{
  "contract": "0x...",
  "metric": "deposit_total",
  "from_block": 5000000,
  "to_block": 5010000
}
```

Three independent Lyquor nodes fetch the same logs, compute the same canonical
result, and publish its proposal to the Lyquid oracle. The aggregate step
requires two matching proposals. The certified result hash and metadata are
stored in Lyquid network state (and optionally mirrored to `ResultRegistry`). A
consumer contract or dashboard reads the result and compares it with the
proposals.

## Existing approaches and limitations

| Approach | Strength | Limitation for this problem |
|---|---|---|
| The Graph | Rich indexing, decentralized network | Off-chain result; consumer trusts the indexer's answer |
| Dune | Flexible analytics | Centralized execution; not an on-chain verifiable fact |
| Chainlink-style oracles | On-chain delivery | Typically latest values, not arbitrary historical ranges |
| UMA optimistic oracle | Flexible disputes | Slow, human-checked; not a deterministic re-execution path |
| ZK coprocessors | Cryptographic proof | Proving cost and complexity for simple analytics |

VeriIndex does not replace these systems. It provides a narrower, auditable
pattern: deterministic re-execution by several nodes plus a quorum-backed
on-chain commitment.

## Original contribution

1. A small protocol for **historical range queries** with multi-node
   re-execution and signed results.
2. A **canonical result format** that makes independent implementations
   comparable byte-for-byte.
3. A **quorum and disagreement model** that records dissent instead of hiding it.
4. An **on-chain result registry** that stores only a hash and metadata, keeping
   cost low.
5. An evaluation that includes a deliberately lying node, not only happy paths.

## Non-goals

- No ZK proof of computation.
- No full production indexer or multi-chain support.
- No token, governance, or economic incentive design.
- No attempt to hide the fact that quorum trust is weaker than a cryptographic
  proof.
- No custom wallet or production UI.

## Success criteria

- The reference implementation reproduces the same result hash for the same
  fixture on repeated runs.
- A single lying node is detected and cannot change the quorum result.
- The on-chain registry stores and returns the result hash and metadata.
- A team-external user can follow the README and complete the demo workflow.
- The report clearly separates the team's contribution from reused components
  and states the trust assumptions and limitations.
