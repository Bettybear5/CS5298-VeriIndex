# LDK runbook: build, deploy, and run VeriIndex

This is the concrete procedure for step 2 (Lyquid integration). It assumes the
official LDK repository is available. The crate lives in `lyquid/` and targets
LDK `0.8.4`.

## Prerequisites

- Docker Engine + Docker Compose v2
- Git
- Network access to GHCR and GitHub
- A Sepolia RPC URL (or the default public RPC baked into the crate)

The official Docker images are pulled from GHCR. The multi-node stack does not
include a tools container, so install `lyquor`/`shaker` on the host with the LDK
`shakenup.sh` helper and install Foundry for `cast`.

## 1. Clone the LDK

```bash
git clone https://github.com/lyquor-labs/ldk.git
cd ldk
```

## 2. Put the VeriIndex crate into the LDK checkout

```bash
cp -r /home/bettybear5/CS5298-VeriIndex/lyquid ./veriindex
```

The crate has its own `[workspace]`, so it does not need to be added to the
LDK root workspace members.

## 3. Start the 4-node Docker devnet

Use the multi-node topology so the oracle committee has four nodes and a
meaningful quorum.

```bash
docker compose -f docker/multi/docker-compose.yaml up -d
docker compose -f docker/multi/docker-compose.yaml logs -f setup-devnet
```

Wait until `setup-devnet` finishes and the four node APIs are reachable:

- `ws://127.0.0.1:10087/ws`
- `ws://127.0.0.1:11087/ws`
- `ws://127.0.0.1:12087/ws`
- `ws://127.0.0.1:13087/ws`

Health check:

```bash
curl --data '{}' \
  --header 'content-type: application/json' \
  -s http://127.0.0.1:10087/lyquor.node.v1.NodeService/GetNodeInfo
```

## 4. Install the host tools and deploy VeriIndex

The multi-node Docker stack runs only the nodes. Install `lyquor` and `shaker`
on the host with the LDK helper, and install Foundry for `cast`:

```bash
cd /path/to/ldk
./shakenup.sh          # installs lyquor and shaker
# Foundry (for cast):
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

From the LDK checkout, with `veriindex/` copied in step 2:

```bash
shaker deploy \
  --endpoint ws://127.0.0.1:10087/ws \
  --reference http://127.0.0.1:8000/lyquids \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  --debug --output json \
  ./veriindex/Cargo.toml
```

Build errors appear here; if you want an isolated build first, run:

```bash
cd veriindex
cargo build --release --target wasm32-unknown-unknown
cd ..
```

The constructor takes no arguments. Save the returned `lyquid_id` and
`contract`:

```bash
export LYQUID_ID='Lyquid-...'
export LYQUID_CONTRACT='0x...'
export LYQUID_TARGET="$(shaker to-hex "$LYQUID_ID")"
```

If `shaker` asks for input, the constructor has no parameters; pass an empty
input or omit `--input`.

## 5. Configure the oracle committee

The fastest path is to reuse the official example helpers, which fetch the four
node IDs and call the internal oracle lifecycle methods. From the LDK checkout
on the host:

```bash
cd /path/to/ldk/lyquid-examples
source scripts/lib/demo.sh

# The Docker multi stack exposes the same ports as the native multi localnet.
DEMO_TOPOLOGY=multi
export LYQUID_CONTRACT
export LYQUID_TARGET

demo_send "configure_committee(bytes32[])" "$(demo_node_ids_array)"
demo_activate_oracle veriindex_oracle
demo_wait_for_committee 4
```

What this does:

1. `configure_committee(bytes32[])` initializes the committee with all four
   node IDs and a majority threshold (`floor(4/2)+1 = 3`).
2. `demo_activate_oracle veriindex_oracle` advances and finalizes the oracle
   epoch for the `veriindex_oracle` topic.
3. `demo_wait_for_committee 4` waits until every node observes the committee.

Check:

```bash
cast call --rpc-url ws://127.0.0.1:10087/ws \
  "$LYQUID_CONTRACT" "get_node_ids() returns (string[])"
```

## 6. Configure each node

Each node needs the RPC endpoint it will use for `eth_getLogs`. Set it on all
four nodes (replace the URL with your own Sepolia RPC if needed):

```bash
PK=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
for WS in ws://127.0.0.1:10087/ws ws://127.0.0.1:11087/ws \
          ws://127.0.0.1:12087/ws ws://127.0.0.1:13087/ws; do
  cast send --private-key "$PK" --rpc-url "$WS" \
    "$LYQUID_CONTRACT" "set_rpc_url(string)" \
    "https://ethereum-sepolia-rpc.publicnode.com"
done
```

Set the quorum threshold on the node that will trigger aggregation:

```bash
cast send --private-key "$PK" --rpc-url ws://127.0.0.1:10087/ws \
  "$LYQUID_CONTRACT" "set_min_proposals(uint16)" 3
```

## 7. Run one indexing round

Use the Sepolia address of `EventSource` and a block range that contains
events:

```bash
cast send --private-key "$PK" --rpc-url ws://127.0.0.1:10087/ws \
  "$LYQUID_CONTRACT" "report_result(string,string,uint64,uint64)" \
  "0xAbC0000000000000000000000000000000000001" \
  "deposit_total" 5000000 5010000
```

This node starts the oracle proposal flow. Each committee member runs
`propose`, fetches logs from its configured RPC, computes the canonical result,
and returns a proposal. The aggregate step requires three matching hashes and
writes a certified result.

## 8. Read the result

```bash
cast call --rpc-url ws://127.0.0.1:10087/ws \
  "$LYQUID_CONTRACT" "get_result(string,string,uint64,uint64) returns (string)" \
  "0xAbC0000000000000000000000000000000000001" \
  "deposit_total" 5000000 5010000

cast call --rpc-url ws://127.0.0.1:10087/ws \
  "$LYQUID_CONTRACT" "has_result(string,string,uint64,uint64) returns (bool)" \
  "0xAbC0000000000000000000000000000000000001" \
  "deposit_total" 5000000 5010000
```

The returned JSON contains `result_hash`, `value`, `event_count`, `quorum`,
`timestamp`, and `signers`.

Debug a single node without the oracle:

```bash
cast call --rpc-url ws://127.0.0.1:10087/ws \
  "$LYQUID_CONTRACT" "index_local(string,string,uint64,uint64) returns (string)" \
  "0xAbC0000000000000000000000000000000000001" \
  "deposit_total" 5000000 5010000
```

## 9. Record evidence

Save the following into `report/evidence/`:

- deploy output with `lyquid_id` and `contract`
- `get_node_ids` output
- `configure_committee` transaction
- one `report_result` transaction
- `get_result` JSON
- node logs showing the proposals and the certified update

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `cargo build` cannot find `lyquid` | Git/SSH access or wrong LDK version | Use HTTPS Git URL (already set) and LDK `0.8.4` |
| `configure_committee` reverts | Caller is not `initializer` | Call from the deployer/owner address |
| Oracle epoch does not advance | Committee not staged | Re-run `demo_activate_oracle veriindex_oracle` |
| `report_result` returns false | No quorum or RPC failure | Check each node's `get_rpc_url`, logs, and `get_node_ids` |
| `RESULT_NOT_FOUND` | No certified result yet | Wait for the oracle epoch and check logs |
| RPC 429/403 | Public RPC rate limit | Set a dedicated Sepolia RPC with `set_rpc_url` |

## Stop and reset

```bash
docker compose -f docker/multi/docker-compose.yaml down
# remove persisted state:
docker compose -f docker/multi/docker-compose.yaml down -v
```
