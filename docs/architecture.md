# Architecture

## Components

| Component | Responsibility | State |
|---|---|---|
| `EventSource.sol` | Emits `Deposit`, `Withdraw`, `Swap` events for indexing | On chain (Sepolia) |
| Lyquid indexer | Fetch logs for a range, compute a metric, canonicalize, hash, sign | Off chain, per node |
| Oracle aggregate | Group proposals by result hash and produce a certified quorum result | Off chain |
| `ResultRegistry.sol` | Store result hash, metric id, block range, quorum, timestamp | On chain |
| CLI / web view | Submit a request, show per-node results, show quorum and on-chain read | Off chain |

## State placement

**On chain (Lyquid network state; optional Sepolia anchor)**

- `result_hash` (hex string in network state; bytes32 in `ResultRegistry`):
  SHA-256 of the canonical result JSON.
- `metric`/`metricId`: metric name in network state; keccak256 id in the
  Solidity registry.
- `from_block`, `to_block` (uint64).
- `quorum` (u16/uint8): number of matching proposals required.
- `timestamp` (uint64).
- `signers` (network state) or `submitter` (Sepolia registry).

**Off chain**

- Raw event logs and RPC responses.
- Per-node canonical result and oracle proposal.
- Dissenting node ids and their hashes.
- Human-readable report and evaluation artifacts.

The chain does not store the full result JSON. A consumer that needs the value
can fetch it from any node and check that its hash matches the on-chain record.

## End-to-end workflow

1. **Request.** The requester provides `contract`, `metric`, `fromBlock`,
   `toBlock`, and the quorum threshold.
2. **Fetch.** Each node fetches logs for the range from its configured RPC.
3. **Compute.** Each node computes the metric with deterministic integer
   arithmetic. No floating point is allowed in the canonical result.
4. **Canonicalize.** The result object is serialized with sorted keys, no
   insignificant whitespace, lowercase addresses, decimal strings for integers,
   and null for absent values.
5. **Hash and propose.** Each node computes `sha256(canonical_json)` and submits
   the result as an oracle proposal.
6. **Aggregate.** The Lyquid oracle groups proposals by result hash, requires
   `threshold` matching proposals, and certifies the result.
7. **Record.** The certified `update` call writes the result into Lyquid network
   state; optionally an external submitter mirrors it to
   `ResultRegistry.submitResult(...)` on Sepolia.
8. **Read.** A consumer contract or the CLI reads the network-state record (or
   the Sepolia mirror) and compares the stored hash with the proposals.

## Result schema

```json
{
  "schema_version": 1,
  "chain_id": 11155111,
  "contract": "0xabc...",
  "metric": "deposit_total",
  "from_block": 5000000,
  "to_block": 5010000,
  "event_count": 42,
  "value": "1234500000000000000"
}
```

Rules:

- `value` is a decimal string, never a float.
- `contract` is lowercase hex with `0x`.
- `metric` is a stable identifier, not free text.
- `event_count` counts matching events after range filtering.
- The canonical form is UTF-8, keys sorted lexicographically, separators
  `(",", ":")`, and no trailing newline.

`resultHash = sha256(canonical_json)`.

## Proposal schema

Lyquid oracle proposal:

```json
{
  "node_id": "node-a",
  "request": { "contract": "0x...", "metric": "deposit_total", "from_block": 5000000, "to_block": 5010000 },
  "result": { "...": "..." },
  "result_hash": "hex..."
}
```

The reference implementation adds a `signature` field signed with an Ethereum
test key using `eth-account`, so the Python evaluation can verify proposals
without the Lyquid runtime. The production path uses the official LDK oracle,
which authenticates and certifies proposals natively.

## Quorum rules

- `threshold` is an integer in `[1, number_of_nodes]`; the demo uses `2` of `3`.
- Group proposals by `result_hash` after the oracle validates the inputs.
- If a group has at least `threshold` members, the outcome is `CONSENSUS`.
- If no group reaches the threshold, the outcome is `DISPUTED`.
- If fewer than `threshold` valid proposals are available, the outcome is
  `INSUFFICIENT`.
- The outcome always includes `agreeing_nodes` and `dissenting_nodes`.

## Threat model and trust assumptions

**Adversary**

- May control one indexer node and return a wrong value.
- May control the RPC endpoint used by one node and return incomplete logs.
- May try to replay a proposal for a different block range.
- May try to front-run or censor the on-chain result submission.

**Trusted**

- The oracle committee configuration and the registry owner/authorized
  submitters are trusted for this prototype.
- At least `threshold` nodes are independent and honest.
- The canonicalization and hashing rules are implemented identically by honest
  nodes.
- The consumer checks the on-chain hash against the off-chain result.

**Not solved**

- A malicious majority can collude.
- A single RPC provider can lie to all nodes that use it.
- Reorgs can invalidate a result after it is recorded.
- The registry does not prove that the computation was performed; it only
  records that a quorum signed it.
- No economic stake or slashing.

## Failure handling

| Failure | Detection | Output |
|---|---|---|
| One node returns wrong value | Result hash mismatch | `DISPUTED` / dissent recorded; quorum still succeeds if threshold reached |
| One node RPC fails | Missing proposal | `INSUFFICIENT` if below threshold |
| All nodes disagree | No group reaches threshold | `DISPUTED`; do not submit on chain |
| Invalid proposal | Oracle validation fails | Ignore proposal; record reason |
| Registry submission fails | Transaction revert | No on-chain record; keep off-chain evidence |
| Block range reorg | Compare block hash before/after | Mark result stale; re-run |

## Contract interface

`EventSource`:

```solidity
event Deposit(address indexed from, uint256 amount);
event Withdraw(address indexed from, uint256 amount);
event Swap(address indexed from, address indexed tokenIn, address indexed tokenOut, uint256 amountIn, uint256 amountOut);

function deposit() external payable;
function withdraw(uint256 amount) external;
function recordSwap(address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut) external;
```

`ResultRegistry`:

```solidity
function submitResult(
    bytes32 resultHash,
    bytes32 metricId,
    uint64 fromBlock,
    uint64 toBlock,
    uint8 quorum
) external;

function getResult(bytes32 metricId, uint64 fromBlock, uint64 toBlock)
    external view returns (Result memory);
```

`Result` contains `resultHash`, `metricId`, `fromBlock`, `toBlock`, `quorum`,
`timestamp`, `submitter`, and `exists`.

## Why this design fits Lyquor

- The expensive part (scanning logs and computing metrics) is off chain.
- The result is small enough to commit on chain cheaply.
- Different nodes can host the same Lyquid and independently recompute.
- The on-chain consumer only needs the hash and metadata, not the raw history.
- Selective hosting lets the indexer service attract nodes that want to run it.
