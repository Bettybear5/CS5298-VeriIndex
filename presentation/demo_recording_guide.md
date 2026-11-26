# VeriIndex — 3-minute demo recording guide

This file is the shot list for the **last 3 minutes** of the 8-minute presentation.
The first 5 minutes use `CS5298_VeriIndex_Presentation.pptx`.

Recording language: **English narration**  
Chinese is included for rehearsal/reference.

---

## Before recording

Open these windows:

- Terminal in `/tmp/opencode/ldk`
- `report/evidence/lyquid-run-direct.json`
- Optional: GitHub Actions run  
  `https://github.com/Bettybear5/CS5298-VeriIndex/actions/runs/45728324966`

Set terminal font to 20–24 pt.  
Resolution: 1920×1080, 30 fps.  
Do not show private keys, `.env`, tokens, or personal accounts.

### If local Docker is unavailable

Do not fake the demo. Record the successful CI evidence instead:

```bash
cd /home/bettybear5/CS5298-VeriIndex
cat report/evidence/lyquid-run-direct.json
```

Show the GitHub Actions run page and explain:

> This is the recorded output of the submitted implementation on the single-node Lyquor devnet.

---

# Timeline

| Time | Screen | What to show |
|---|---|---|
| 0:00–0:15 | PPT slide 10 / terminal | Transition to demo |
| 0:15–0:45 | Terminal | Deploy Lyquid |
| 0:45–1:25 | Terminal | Index real Sepolia WETH9 events |
| 1:25–1:55 | Terminal | Submit result |
| 1:55–2:20 | Terminal | `get_result_count` + `has_result` |
| 2:20–2:50 | JSON file / terminal | Full `get_result` |
| 2:50–3:00 | JSON / PPT | Limitation and close |

---

## 0:00–0:15 — Transition

**Show:** PPT slide 10 or switch to the terminal.

**English narration:**

> I will now switch to the recorded demo. It uses the successful single-node Lyquor run from the submitted implementation.

**中文对照：**

> 现在切换到预录 demo。它使用已提交实现在单节点 Lyquor 上的成功运行结果。

---

## 0:15–0:45 — Deploy the Lyquid

### Setup

```bash
export PROJECT=/home/bettybear5/CS5298-VeriIndex
export LDK=/tmp/opencode/ldk
export NODE_HTTP=http://127.0.0.1:10087/api
export NODE_WS=ws://127.0.0.1:10087/ws
export PK=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

`PK` is the public Anvil test key. Use it only on the local devnet.

### Start devnet

```bash
cd "$LDK"
docker compose -f docker/single/docker-compose.yaml up -d
docker compose -f docker/single/docker-compose.yaml logs -f setup-devnet
```

Wait for the `Contract:` line, then press `Ctrl-C`.

### Copy and deploy

```bash
rm -rf "$LDK/veriindex"
cp -r "$PROJECT/lyquid" "$LDK/veriindex"

docker run --rm --network host \
  -v "$LDK:/ldk" -w /ldk \
  ghcr.io/lyquor-labs/lyquor-tools:v0.8.4 \
  shaker deploy /ldk/veriindex/Cargo.toml \
  --endpoint "$NODE_WS" \
  --private-key "$PK" \
  --output json \
  | tee /tmp/deploy.json

export LYQUID_ID=$(jq -r '.lyquid_id' /tmp/deploy.json)
export CONTRACT=$(jq -r '.contract' /tmp/deploy.json)

echo "$LYQUID_ID"
echo "$CONTRACT"
```

**Expected output:**

```text
Lyquid-ahjg4huwvban3bvhxue7rcbaw4mnltwyolhqa
0x0165878a594ca255338adfa4d48449f69242eb8f
```

**English narration:**

> The Lyquid is deployed to a single-node Lyquor devnet. The output gives the Lyquid ID and the sequencer contract.

**中文对照：**

> Lyquid 已部署到单节点 Lyquor devnet。输出给出 Lyquid ID 和 sequencer 合约地址。

---

## 0:45–1:25 — Index real Sepolia events

### Set RPC and quorum

```bash
cast call --rpc-url "$NODE_HTTP" "$CONTRACT" \
  "set_rpc_url(string) returns (bool)" \
  "https://ethereum-sepolia-rpc.publicnode.com"

cast call --rpc-url "$NODE_HTTP" "$CONTRACT" \
  "set_min_proposals(uint16) returns (bool)" 1
```

### Run `index_local`

```bash
cast call --rpc-url "$NODE_HTTP" "$CONTRACT" \
  "index_local(string,string,uint64,uint64) returns (string)" \
  0xfff9976782d46cc05630d1f6ebab18b2324d6b14 \
  deposit_total \
  12212875 \
  12212975 \
  | tee /tmp/index-local.json
```

**Expected output (short):**

```text
"{\"canonical_hash\":\"0x2d4638...\",\"proposal\":{...\"event_count\":44,\"value\":\"69023557792913378\"...}}"
```

**English narration:**

> This is a real Sepolia WETH9 range. The Lyquid fetches the logs, decodes 44 Deposit events, and computes a total deposited value of 69,023,557,792,913,378 wei. It then produces a canonical result and its hash.

**中文对照：**

> 这是 Sepolia 上真实的 WETH9 区间。Lyquid 拉取日志，解码出 44 个 Deposit 事件，计算总存入值为 69,023,557,792,913,378 wei，然后生成 canonical 结果和哈希。

### Parse the result

```bash
eval "$(python3 - /tmp/index-local.json <<'PY'
import json, sys
text = open(sys.argv[1], encoding="utf-8").read().strip()
data = json.loads(text)
if isinstance(data, str):
    data = json.loads(data)
proposal = data["proposal"]
result = proposal["result"]
print(f"VALUE={result['value']!r}")
print(f"EVENT_COUNT={result['event_count']!r}")
print(f"RESULT_HASH={proposal['result_hash']!r}")
PY
)"

echo "$VALUE"
echo "$EVENT_COUNT"
echo "$RESULT_HASH"
```

**Expected:**

```text
69023557792913378
44
0x2d463896132e0b66b993824f73a6c6c55cd53067750fe3bb4f00d8cace589011
```

---

## 1:25–1:55 — Submit the result

```bash
cast send --private-key "$PK" --rpc-url "$NODE_HTTP" \
  "$CONTRACT" \
  "submit_result(string,string,uint64,uint64,string,string,uint64,uint16)" \
  0xfff9976782d46cc05630d1f6ebab18b2324d6b14 \
  deposit_total \
  12212875 \
  12212975 \
  "$RESULT_HASH" \
  "$VALUE" \
  "$EVENT_COUNT" \
  1 \
  | tee /tmp/submit.log
```

**Expected:**

```text
status               1 (success)
transactionHash      0x3e5a13c38ab6a37021e53cefed6faacfdacfdc505c862c84ba46623c30580c4b
```

**English narration:**

> `submit_result` writes the result hash and metadata into Lyquid network state. The transaction succeeds.

**中文对照：**

> `submit_result` 把结果哈希和元数据写入 Lyquid network state，交易执行成功。

---

## 1:55–2:20 — Read count and existence

```bash
cast call --rpc-url "$NODE_HTTP" "$CONTRACT" \
  "get_result_count() returns (uint64)"

cast call --rpc-url "$NODE_HTTP" "$CONTRACT" \
  "has_result(string,string,uint64,uint64) returns (bool)" \
  0xfff9976782d46cc05630d1f6ebab18b2324d6b14 \
  deposit_total \
  12212875 \
  12212975
```

**Expected:**

```text
1
true
```

**English narration:**

> After the write, `get_result_count` returns one, and `has_result` is true for the same key.

**中文对照：**

> 写入之后，`get_result_count` 返回 1，`has_result` 对同一个 key 返回 true。

---

## 2:20–2:50 — Read the full JSON

```bash
cast call --rpc-url "$NODE_HTTP" "$CONTRACT" \
  "get_result(string,string,uint64,uint64) returns (string)" \
  0xfff9976782d46cc05630d1f6ebab18b2324d6b14 \
  deposit_total \
  12212875 \
  12212975 \
  | tee /tmp/result.json
```

**Expected:**

```json
{
  "result_hash": "0x2d463896132e0b66b993824f73a6c6c55cd53067750fe3bb4f00d8cace589011",
  "contract": "0xfff9976782d46cc05630d1f6ebab18b2324d6b14",
  "metric": "deposit_total",
  "from_block": 12212875,
  "to_block": 12212975,
  "event_count": 44,
  "value": "69023557792913378",
  "quorum": 1,
  "timestamp": 12,
  "signers": []
}
```

**English narration:**

> This is the full record read back from the Lyquid. The timestamp is the Lyquor block number, not wall-clock time. The direct registry path is verified.

**中文对照：**

> 这是从 Lyquid 读回的完整记录。timestamp 是 Lyquor 区块号，不是真实时间。direct registry 路径已经验证。

---

## 2:50–3:00 — Close

```bash
cd "$LDK"
docker compose -f docker/single/docker-compose.yaml down
```

**English narration:**

> The oracle two-phase update path is implemented but not validated on a single-node committee. The next steps are multi-node oracle validation and an external user study. Thank you.

**中文对照：**

> oracle 两阶段 update 路径已经实现，但在单节点 committee 下尚未验证。下一步是多节点 oracle 验证和外部用户测试。谢谢。

---

# Values to show

```text
lyquid_id: Lyquid-ahjg4huwvban3bvhxue7rcbaw4mnltwyolhqa
Lyquid contract: 0x0165878a594ca255338adfa4d48449f69242eb8f
indexed contract: 0xfff9976782d46cc05630d1f6ebab18b2324d6b14
range: 12212875..12212975
event_count: 44
value: 69023557792913378
result_hash: 0x2d463896132e0b66b993824f73a6c6c55cd53067750fe3bb4f00d8cace589011
submit_tx: 0x3e5a13c38ab6a37021e53cefed6faacfdacfdc505c862c84ba46623c30580c4b
get_result_count: 1
has_result: true
timestamp: 12
```

# Do not show / do not claim

- Do not claim the oracle `update` path is verified.
- Do not show `RESULT_NOT_FOUND`.
- Do not use the old `value=0` result.
- Do not show private keys, `.env`, tokens, or account credentials.
- Do not run `report_result` in this 3-minute demo.

# Export and submit

1. Export MP4, H.264, 1920×1080, 30 fps.
2. Keep total length ≤ 8:00, with demo ≤ 3:00.
3. Save as:
   ```text
   demo/CS5298_VeriIndex_Demo.mp4
   ```
4. Build the ZIP:
   ```bash
   cd /home/bettybear5/CS5298-VeriIndex
   bash submission/package.sh
   ```
5. Upload:
   - `report/CS5298_VeriIndex_Report.pdf`
   - `submission/CS5298_VeriIndex_Demo.zip`
