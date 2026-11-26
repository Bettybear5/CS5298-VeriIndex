# VeriIndex — 8-minute recording guide

Total target: **7:45–8:00**  
Structure: **5 minutes presentation + 3 minutes recorded demo**

Recording language: **English narration** (Chinese is for rehearsal/reference).

---

## Before recording

Open these windows:

1. `presentation/CS5298_VeriIndex_Presentation.pptx`
2. `report/evidence/lyquid-run-direct.json`
3. GitHub Actions run:
   `https://github.com/Bettybear5/CS5298-VeriIndex/actions/runs/45728324966`

Recommended layout:

- Left: PPT or GitHub Actions / terminal
- Right: `lyquid-run-direct.json`
- Terminal font: 20–24 pt
- Resolution: 1920×1080, 30 fps
- Close notifications, private tabs, `.env`, private keys

---

# Part A — 5-minute presentation

## 0:00–0:15 — Slide 1: Title

**Show:** Title slide.

**English narration:**

> Good morning. I'm Bettybear5. My project is VeriIndex, a verifiable historical event indexer built as a Lyquid on Lyquor. In the next five minutes I will explain the problem, the design, and the verified result. Then I will show a three-minute recorded demo.

**中文对照：**

> 早上好，我是 Bettybear5。我的项目是 VeriIndex，一个部署在 Lyquor 上的可验证历史事件索引器。接下来五分钟我会介绍问题、设计和已验证结果，然后播放三分钟预录 demo。

---

## 0:15–0:55 — Slide 2: Problem

**Show:** Slide 2, highlight the four bullets.

**English narration:**

> Historical on-chain data is public, but the aggregate is not verifiable. A protocol asks for trading volume or TVL, and receives a number from an indexer. It cannot tell whether the indexer used the requested block range, or whether independent operators agree. If one indexer is compromised, the result changes silently. This is the trust gap VeriIndex targets.

**中文对照：**

> 链上历史数据是公开的，但聚合结果不可验证。协议查询交易量或 TVL 时，只能从索引器拿到一个数字，无法确认它是否用了指定区块范围，也无法确认多个独立节点是否一致。如果单个索引器被攻破，结果会被静默改变。这就是 VeriIndex 要解决的信任缺口。

---

## 0:55–1:25 — Slide 3: Existing approaches

**Show:** Slide 3 comparison table.

**English narration:**

> The Graph and Dune are powerful, but they return an off-chain answer. Chainlink-style oracles deliver values on chain, but they are optimized for current values, not arbitrary historical ranges. ZK coprocessors can prove computation, but the proving cost is high for simple analytics. The opening is a lightweight middle ground: deterministic re-execution by independent nodes, plus a small on-chain commitment.

**中文对照：**

> The Graph 和 Dune 很强大，但返回的是链下结果。Chainlink 类 oracle 能把值送到链上，但主要面向当前值，不是任意历史区间。ZK coprocessor 能证明计算，但对简单分析来说证明成本太高。机会在于一个轻量中间方案：多个独立节点做确定性重算，再加一个小的链上承诺。

---

## 1:25–2:05 — Slide 4: Contribution

**Show:** Four contribution cards.

**English narration:**

> The contribution has four parts. First, the unit of work is a historical range query, not a latest-value feed. Second, the result has a canonical JSON form, so independent implementations can compare byte-for-byte. Third, nodes produce signed proposals and the protocol records quorum and dissent. Fourth, only a hash and metadata go on chain, so the cost is low. The verified path in this project is `index_local`, `submit_result`, and `get_result`. I will be explicit later about the oracle path that is implemented but not validated on a single node.

**中文对照：**

> 贡献有四点。第一，工作单位是历史区间查询，而不是最新值订阅。第二，结果采用 canonical JSON，独立实现可以逐字节比较。第三，节点产生签名 proposal，协议记录 quorum 和异议。第四，链上只存哈希和元数据，成本很低。本项目已验证的路径是 `index_local`、`submit_result` 和 `get_result`。后面我会明确说明 oracle 路径已实现，但在单节点下未验证。

---

## 2:05–2:50 — Slide 5: Architecture

**Show:** Architecture diagram.

**English narration:**

> This is the architecture. The requester asks for a contract, a metric, and a block range. The Lyquid indexer fetches logs from Sepolia, computes the metric, canonicalizes the result, and hashes it. Independent nodes can produce proposals. The quorum result is committed to Lyquid network state. Optionally, the same hash can be mirrored to a small Sepolia registry for external consumers. The important boundary is that the chain stores only a compact commitment, not the full history.

**中文对照：**

> 这是架构。请求方提交合约、指标和区块范围。Lyquid indexer 从 Sepolia 拉日志、计算指标、canonicalize 并哈希。多个独立节点可以产生 proposal。quorum 结果写入 Lyquid network state。可选地，同一个哈希可以镜像到 Sepolia 的小型 registry 供外部消费者使用。关键边界是：链上只存紧凑承诺，不存完整历史。

---

## 2:50–3:25 — Slide 6: Workflow

**Show:** Six workflow cards.

**English narration:**

> The workflow is deliberately simple. The requester supplies a range. Each node fetches logs, computes an integer metric, and produces a canonical JSON object. The result hash is SHA-256 over that canonical form. In the multi-node design, nodes sign the hash and a quorum is formed. The registry stores the hash and metadata, and a consumer reads the JSON back. The timestamp is the Lyquor block number, not wall-clock time, which is deterministic.

**中文对照：**

> workflow 刻意保持简单。请求方给出区间。每个节点拉日志、计算整数指标、生成 canonical JSON。结果哈希是 canonical 形式的 SHA-256。在多节点设计中，节点签名，形成 quorum。registry 存哈希和元数据，消费者读回 JSON。timestamp 使用 Lyquor 区块号而不是真实时间，以保证确定性。

---

## 3:25–3:55 — Slide 7: Implementation

**Show:** Three implementation columns.

**English narration:**

> Implementation is split into three pieces. The Python reference is the deterministic oracle for evaluation. The Rust Lyquid targets LDK 0.8.4 and contains the oracle code and the registry. The Solidity contracts are the Sepolia-facing event source and an optional result registry. This separation lets me test the protocol logic independently from the Lyquid deployment.

**中文对照：**

> 实现分为三部分。Python reference 是评估用的确定性 oracle。Rust Lyquid 基于 LDK 0.8.4，包含 oracle 代码和 registry。Solidity 合约是面向 Sepolia 的事件源和可选的结果 registry。这个拆分让我可以独立测试协议逻辑和 Lyquid 部署。

---

## 3:55–4:30 — Slide 8: Results

**Show:** Results table and single-node JSON box.

**English narration:**

> The reference implementation passes sixteen tests, including determinism, correctness against an independent recomputation, and tamper detection. The 2-of-3 case reaches consensus while recording the lying node as dissent. The 3-of-3 case is disputed. On the Lyquid side, the clean single-node run indexed 44 real Sepolia WETH9 Deposit events, with total value 69,023,557,792,913,378 wei. `get_result_count` is one, `has_result` is true, and the result hash is `0x2d4638`. The oracle update path did not complete on a single node, and I do not claim it as verified.

**中文对照：**

> reference implementation 通过 16 个测试，包括确定性、与独立重算的一致性和篡改检测。2-of-3 能达成共识并把作恶节点记为异议；3-of-3 会进入 disputed。在 Lyquid 侧，干净的单节点运行索引了 Sepolia 上真实的 WETH9 44 个 Deposit 事件，总值为 69,023,557,792,913,378 wei。`get_result_count` 为 1，`has_result` 为 true，结果哈希是 `0x2d4638`。oracle update 路径在单节点下未完成，我不声称它已验证。

---

## 4:30–5:00 — Slide 9: Limitations and conclusion

**Show:** Verified / Not yet verified columns and conclusion bar.

**English narration:**

> The honest limitation is scope. I verified deployment, the direct registry path, canonicalization, hashing, and the tamper evaluation. I did not validate the oracle update path on a single node, I did not complete an external user study, and I did not run multiple independent nodes. The conclusion is that VeriIndex turns a historical query into a small auditable fact, and the direct path already produces a real readable Lyquid record. Multi-node oracle validation is the next step.

**中文对照：**

> 需要诚实说明范围限制。我验证了部署、直接注册路径、canonicalization、哈希和篡改评估。没有在单节点上验证 oracle update 路径，没有完成外部用户测试，也没有运行多个独立节点。结论是：VeriIndex 把历史查询变成一个小型可审计事实，direct path 已经产生真实可读的 Lyquid 记录。多节点 oracle 验证是下一步。

---

# Part B — 3-minute demo

## 0:00–0:15 — Transition

**Show:** PPT slide 10 or switch to terminal/GitHub Actions.

**English narration:**

> I will now switch to the recorded demo. It uses the successful single-node Lyquor run from the submitted implementation.

**中文对照：**

> 现在切换到预录 demo。它使用已提交实现在单节点 Lyquor 上的成功运行结果。

---

## 0:15–0:45 — Deployment

**Show:** `deploy.json`, or GitHub Actions deploy step.

**Expected output:**

```json
{
  "contract": "0x0165878a594ca255338adfa4d48449f69242eb8f",
  "lyquid_id": "Lyquid-ahjg4huwvban3bvhxue7rcbaw4mnltwyolhqa",
  "os_version": "0.8"
}
```

**English narration:**

> The Lyquid is deployed to a single-node Lyquor devnet. The output gives the Lyquid ID and the sequencer contract.

**中文对照：**

> Lyquid 已部署到单节点 Lyquor devnet。输出给出 Lyquid ID 和 sequencer 合约地址。

---

## 0:45–1:25 — Real event indexing

**Show:** `report/evidence/lyquid-run-direct.json` or `index-local.json`.

**Highlight:**

```text
indexed contract: 0xfff9976782d46cc05630d1f6ebab18b2324d6b14  (Sepolia WETH9)
range: 12212875..12212975
event_count: 44
value: 69023557792913378
result_hash: 0x2d463896132e0b66b993824f73a6c6c55cd53067750fe3bb4f00d8cace589011
```

**English narration:**

> This is a real Sepolia WETH9 range. The Lyquid fetches the logs, decodes 44 Deposit events, and computes a total deposited value of 69,023,557,792,913,378 wei. It then produces a canonical result and its hash.

**中文对照：**

> 这是 Sepolia 上真实的 WETH9 区间。Lyquid 拉取日志，解码出 44 个 Deposit 事件，计算总存入值为 69,023,557,792,913,378 wei，然后生成 canonical 结果和哈希。

---

## 1:25–1:55 — Registry write

**Show:** `submit.log` or `submit_tx` field.

**Highlight:**

```text
submit tx: 0x3e5a13c38ab6a37021e53cefed6faacfdacfdc505c862c84ba46623c30580c4b
```

**English narration:**

> `submit_result` writes the result hash and metadata into Lyquid network state. The transaction succeeds.

**中文对照：**

> `submit_result` 把结果哈希和元数据写入 Lyquid network state，交易执行成功。

---

## 1:55–2:20 — Read count and existence

**Show:** `get_result_count` and `has_result`.

**Expected output:**

```text
get_result_count: 1
has_result: true
```

**English narration:**

> After the write, `get_result_count` returns one, and `has_result` is true for the same key.

**中文对照：**

> 写入之后，`get_result_count` 返回 1，`has_result` 对同一个 key 返回 true。

---

## 2:20–2:50 — Full `get_result` JSON

**Show:** `report/evidence/lyquid-run-direct.json`.

**Highlight the full record:**

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

**Show:** Keep the JSON visible or return to PPT slide 10.

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

# Export and package

1. Export MP4, H.264, 1920×1080, 30 fps.
2. Keep total length **≤ 8:00**.
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
