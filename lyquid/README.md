# VeriIndex Lyquid

This is the Lyquor-side crate. It targets LDK `0.8.4` and follows the same
shape as the official `price-feed` example: an oracle committee, a two-phase
proposal/aggregate flow, a certified `update` network method, and a small piece
of network state that acts as the on-chain result registry.

## What is implemented

- `src/canonical.rs`: sorted-key canonical JSON and SHA-256 result hash.
- `src/metrics.rs`: event filtering, deduplication, and five metrics.
- `src/rpc.rs`: `eth_getLogs` over the host HTTP capability, plus decoding of
  `Deposit`, `Withdraw`, and `Swap` logs from `EventSource.sol`.
- `src/types.rs`: request, proposal, finalized result, and registry record.
- `src/lib.rs`: Lyquid methods and state.

## State and methods

Network state:

- `initializer`: address allowed to configure the oracle committee.
- `veriindex_oracle`: oracle committee state.
- `results: HashMap<String, ResultRecord>`: the result registry.
- `result_count`: number of finalized results.

Instance state:

- `rpc_url`: Sepolia (or local) JSON-RPC endpoint; empty means the default.
- `min_proposals`: quorum threshold for the aggregate step.

Methods:

| Method | Kind | Purpose |
|---|---|---|
| `constructor()` | network | Set the initializer |
| `configure_committee(node_ids)` | network | Initialize the oracle committee (majority threshold) |
| `set_rpc_url(url)` | instance | Set the per-node RPC endpoint |
| `get_rpc_url()` | instance | Read the effective RPC endpoint |
| `set_min_proposals(n)` | instance | Set the quorum threshold |
| `get_min_proposals()` | instance | Read the threshold |
| `index_local(contract, metric, from, to)` | instance | Fetch/compute one proposal locally, for debugging |
| `propose(...)` | instance oracle | Produce this node's proposal |
| `aggregate(...)` | instance oracle | Group proposals, require quorum, build the certified call |
| `update(finalized)` | network certified | Write the result into network state |
| `report_result(contract, metric, from, to)` | instance | Run propose-and-certify and submit the call |
| `get_result(contract, metric, from, to)` | network view | Read the registry record as JSON |
| `has_result(...)` | network view | Check whether a key exists |
| `get_result_count()` | network view | Number of finalized results |
| `get_node_ids()` | instance view | Oracle committee node IDs (for setup/debug) |

## Integration with the official LDK

The LDK is distributed as a Git dependency and requires Docker for the devnet.
This crate was written against `lyquor-labs/ldk` version `0.8.4`.

1. Start the LDK environment from a clone of `lyquor-labs/ldk`:
   ```bash
   docker-compose up -d
   ```
2. Put this directory inside the LDK workspace, for example
   `lyquid-examples/veriindex`, or build it standalone with the same
   `rust-toolchain.toml` and `.cargo/config.toml`.
3. Build the WASM target:
   ```bash
   cargo build --release --target wasm32-unknown-unknown
   ```
4. Deploy the Lyquid with the tutorial's `shaker deploy` command. The
   constructor takes no arguments.
5. Call `configure_committee` with the node IDs returned by the devnet. The
   threshold is `floor(n/2) + 1`, matching the oracle example.
6. On each node, call `set_rpc_url` if the default public Sepolia RPC is not
   acceptable.
7. Call `report_result(contract, metric, from_block, to_block)`. Each node
   fetches logs, computes the canonical result, and proposes it. The aggregate
   step requires `min_proposals` matching hashes and writes the certified
   result.
8. Read it back with `get_result(...)` or `has_result(...)`.

## Why the oracle flow instead of a custom signature

The official LDK already provides committee configuration, proposal
aggregation, certificate verification, and certified calls. Reusing that flow
keeps the Lyquid small and makes the quorum a first-class Lyquor mechanism. The
Python reference still models per-node signatures with Ethereum test keys; it is
an independent oracle for evaluation, not the production path.

## Security notes

- The default public RPC is convenient for a demo, not a trust anchor. A
  production deployment should configure independent RPCs per node.
- A malicious majority can certify a wrong result. The design makes dissent
  visible when proposals differ, but it is not a proof.
- Reorg handling is not implemented. Add a block-hash commitment and a recheck
  window before claiming finality.
- Do not hard-code private keys or RPC credentials in the Lyquid.
