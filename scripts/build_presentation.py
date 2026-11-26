#!/usr/bin/env python3
"""Build the 8-minute CS5298 VeriIndex presentation and speaker script."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "presentation"
PPTX = OUT / "CS5298_VeriIndex_Presentation.pptx"
SCRIPT = OUT / "speech_script.md"

NAVY = RGBColor(11, 31, 58)
NAVY_2 = RGBColor(18, 48, 84)
TEAL = RGBColor(0, 166, 166)
ORANGE = RGBColor(230, 126, 34)
LIGHT = RGBColor(245, 247, 250)
GREY = RGBColor(90, 100, 115)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(176, 0, 32)
GREEN = RGBColor(22, 120, 80)

FONT = "Calibri"


def slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def box(s, x, y, w, h, text, size=18, color=NAVY, bold=False, align=PP_ALIGN.LEFT,
        fill=None, line=None, font=FONT, margin=0.08):
    shape = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.size = Pt(size)
    p.font.name = font
    p.font.bold = bold
    p.font.color.rgb = color
    if fill is not None:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is not None:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    return shape


def rounded(s, x, y, w, h, text, size=16, color=NAVY, fill=LIGHT, line=None,
             bold=False, align=PP_ALIGN.CENTER):
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(1.25)
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.size = Pt(size)
    p.font.name = FONT
    p.font.bold = bold
    p.font.color.rgb = color
    return shp


def arrow(s, x, y, w, h, fill=TEAL):
    shp = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    return shp


def line(s, x1, y1, x2, y2, color=TEAL, width=1.5, dash=False):
    from pptx.enum.shapes import MSO_CONNECTOR
    conn = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(width)
    if dash:
        conn.line.dash_style = 4
    return conn


def header(s, kicker, title, subtitle=None):
    box(s, 0.65, 0.35, 12.0, 0.35, kicker.upper(), size=11, color=TEAL, bold=True)
    box(s, 0.65, 0.68, 12.0, 0.65, title, size=30, color=NAVY, bold=True)
    if subtitle:
        box(s, 0.65, 1.32, 12.0, 0.38, subtitle, size=14, color=GREY)
    line(s, 0.65, 1.82, 12.68, 1.82, color=RGBColor(215, 220, 228), width=1)


def footer(s, n, total=10):
    box(s, 0.65, 7.08, 8.0, 0.24, "CS5298  ·  VeriIndex  ·  Bettybear5", size=9, color=GREY)
    box(s, 11.9, 7.08, 0.8, 0.24, f"{n}/{total}", size=9, color=GREY, align=PP_ALIGN.RIGHT)


def bullets(s, items, x=0.75, y=2.05, w=11.8, size=17, color=NAVY, gap=0.42):
    yy = y
    for item in items:
        box(s, x, yy, w, 0.35, f"•  {item}", size=size, color=color)
        yy += gap


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1. Title
    s = slide(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
    box(s, 0.8, 0.9, 11.7, 0.4, "CS5298 FINAL PROJECT", size=12, color=TEAL, bold=True)
    box(s, 0.8, 1.55, 11.8, 1.0, "VeriIndex", size=54, color=WHITE, bold=True)
    box(s, 0.8, 2.55, 11.8, 0.9, "A Verifiable Historical Event Indexer on Lyquor", size=26, color=WHITE)
    box(s, 0.8, 3.75, 11.8, 0.45, "Bettybear5  ·  Department of Computer Science, City University of Hong Kong",
        size=14, color=RGBColor(200, 215, 230))
    box(s, 0.8, 6.55, 11.8, 0.35, "git: github.com/Bettybear5/CS5298-VeriIndex", size=11,
        color=RGBColor(160, 185, 205))
    notes(s, "Good morning. I'm Bettybear5. My project is VeriIndex, a verifiable historical event indexer built as a Lyquid on Lyquor. In the next five minutes I will explain the problem, the design, and the verified result. Then I will show a three-minute recorded demo.")

    # 2. Problem
    s = slide(prs)
    header(s, "Problem", "Historical on-chain data is still trusted data",
           "Consumers see a number, not who computed it or over which range.")
    bullets(s, [
        "DeFi, AI agents, auditors and consumer contracts need historical aggregates.",
        "Today they rely on off-chain indexers: The Graph, Dune, or custom pipelines.",
        "The consumer cannot easily verify the block range, the computation, or node agreement.",
        "One compromised indexer can silently change the answer.",
    ], y=2.15, size=17, gap=0.52)
    rounded(s, 9.55, 4.9, 2.95, 1.05, "Trusted\nindexer", size=14, color=WHITE, fill=NAVY, bold=True)
    box(s, 9.55, 6.03, 2.95, 0.35, "No compact audit trail", size=10, color=GREY, align=PP_ALIGN.CENTER)
    footer(s, 2)
    notes(s, "Historical on-chain data is public, but the aggregate is not verifiable. A protocol asks for trading volume or TVL, and receives a number from an indexer. It cannot tell whether the indexer used the requested block range, or whether independent operators agree. If one indexer is compromised, the result changes silently. This is the trust gap VeriIndex targets.")

    # 3. Existing approaches
    s = slide(prs)
    header(s, "Gap", "Existing options optimize for something else")
    table = s.shapes.add_table(4, 3, Inches(0.7), Inches(2.05), Inches(11.9), Inches(3.7)).table
    table.columns[0].width = Inches(3.0)
    table.columns[1].width = Inches(4.4)
    table.columns[2].width = Inches(4.5)
    data = [
        ("Approach", "Strength", "Limitation for this problem"),
        ("The Graph / Dune", "Rich indexing", "Off-chain result; consumer trusts the answer"),
        ("Chainlink-style oracles", "On-chain delivery", "Usually latest values, not arbitrary history"),
        ("ZK coprocessors", "Cryptographic proof", "Proving cost is high for simple analytics"),
    ]
    for r, row in enumerate(data):
        for c, text in enumerate(row):
            cell = table.cell(r, c)
            cell.text = text
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12 if r else 12.5)
                p.font.name = FONT
                p.font.bold = (r == 0)
                p.font.color.rgb = WHITE if r == 0 else NAVY
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if r == 0 else (LIGHT if r % 2 else WHITE)
    rounded(s, 0.7, 6.05, 11.9, 0.55, "Opportunity: deterministic re-execution + a small on-chain commitment",
            size=14, color=WHITE, fill=TEAL, bold=True)
    footer(s, 3)
    notes(s, "The Graph and Dune are powerful, but they return an off-chain answer. Chainlink-style oracles deliver values on chain, but they are optimized for current values, not arbitrary historical ranges. ZK coprocessors can prove computation, but the proving cost is high for simple analytics. The opening is a lightweight middle ground: deterministic re-execution by independent nodes, plus a small on-chain commitment.")

    # 4. Contribution
    s = slide(prs)
    header(s, "Contribution", "VeriIndex: a small auditable protocol",
           "Historical range query -> canonical result -> signed attestations -> registry")
    cards = [
        ("1", "Range queries", "contract + metric +\nfromBlock..toBlock"),
        ("2", "Canonical result", "sorted JSON, exact hash,\ndecimal strings"),
        ("3", "Multi-node evidence", "independent proposals,\nquorum and dissent"),
        ("4", "Cheap registry", "hash + metadata on chain,\nfull history off chain"),
    ]
    x = 0.65
    for num, title, body in cards:
        rounded(s, x, 2.15, 2.95, 2.2, "", fill=LIGHT, line=RGBColor(220, 225, 232))
        box(s, x + 0.18, 2.32, 0.55, 0.45, num, size=22, color=TEAL, bold=True)
        box(s, x + 0.18, 2.85, 2.6, 0.35, title, size=15, color=NAVY, bold=True)
        box(s, x + 0.18, 3.25, 2.6, 0.75, body, size=11, color=GREY)
        x += 3.08
    box(s, 0.75, 4.85, 11.8, 0.4, "Verified path:  index_local  ->  submit_result  ->  get_result",
        size=18, color=NAVY, bold=True)
    box(s, 0.75, 5.35, 11.8, 0.8, "The oracle two-phase update path is implemented, but this talk only claims what was actually executed.",
        size=13, color=GREY)
    footer(s, 4)
    notes(s, "The contribution has four parts. First, the unit of work is a historical range query, not a latest-value feed. Second, the result has a canonical JSON form, so independent implementations can compare byte-for-byte. Third, nodes produce signed proposals and the protocol records quorum and dissent. Fourth, only a hash and metadata go on chain, so the cost is low. The verified path in this project is index_local, submit_result, and get_result. I will be explicit later about the oracle path that is implemented but not validated on a single node.")

    # 5. Architecture
    s = slide(prs)
    header(s, "Design", "Architecture: on-chain commitment, off-chain work")
    rounded(s, 0.55, 2.25, 2.35, 1.15, "Requester\nCLI / web", size=14, fill=LIGHT, line=RGBColor(210, 218, 228))
    rounded(s, 3.35, 1.85, 4.5, 2.35, "", size=12, fill=RGBColor(235, 245, 246), line=TEAL)
    box(s, 3.55, 2.0, 4.1, 0.32, "Lyquid indexer", size=15, color=TEAL, bold=True, align=PP_ALIGN.CENTER)
    for i, label in enumerate(["node A", "node B", "node C"]):
        rounded(s, 3.65 + i * 1.32, 2.55, 1.15, 0.62, label, size=10, fill=WHITE, line=RGBColor(180, 210, 210))
    box(s, 3.65, 3.35, 3.85, 0.62, "fetch logs · compute · canonicalize · sign", size=10, color=GREY)
    rounded(s, 8.55, 1.25, 4.15, 1.0, "Sepolia RPC\nEventSource logs", size=13, fill=LIGHT, line=RGBColor(210, 218, 228))
    rounded(s, 8.55, 3.45, 4.15, 1.0, "Lyquid network state\nresult hash + metadata", size=13, fill=RGBColor(235, 245, 246), line=TEAL)
    rounded(s, 8.55, 5.0, 4.15, 0.78, "Optional ResultRegistry.sol\nSepolia mirror", size=11, fill=LIGHT, line=RGBColor(210, 218, 228))
    arrow(s, 2.95, 2.62, 0.32, 0.35)
    line(s, 7.85, 1.75, 8.5, 1.75, color=TEAL)
    line(s, 7.85, 3.95, 8.5, 3.95, color=TEAL)
    box(s, 6.9, 1.5, 1.8, 0.3, "eth_getLogs", size=9, color=GREY, align=PP_ALIGN.CENTER)
    box(s, 6.7, 4.05, 2.1, 0.3, "quorum result", size=9, color=GREY, align=PP_ALIGN.CENTER)
    box(s, 0.65, 5.35, 7.2, 0.9, "Trust boundary: the registry stores only the hash; the full result and evidence stay off chain. A consumer checks the hash against a result fetched from any node.",
        size=12, color=GREY)
    footer(s, 5)
    notes(s, "This is the architecture. The requester asks for a contract, a metric, and a block range. The Lyquid indexer fetches logs from Sepolia, computes the metric, canonicalizes the result, and hashes it. Independent nodes can produce proposals. The quorum result is committed to Lyquid network state. Optionally, the same hash can be mirrored to a small Sepolia registry for external consumers. The important boundary is that the chain stores only a compact commitment, not the full history.")

    # 6. Workflow
    s = slide(prs)
    header(s, "Workflow", "From a range query to a readable record")
    steps = [
        ("1", "Request", "contract, metric,\nfromBlock, toBlock"),
        ("2", "Fetch", "eth_getLogs\nover the range"),
        ("3", "Compute", "integer metric,\nno floats"),
        ("4", "Canonicalize", "sorted keys,\nSHA-256"),
        ("5", "Attest", "sign result hash\n(quorum design)"),
        ("6", "Record / read", "network state\nJSON result"),
    ]
    for i, (num, title, body) in enumerate(steps):
        col = i % 3
        row = i // 3
        x = 0.7 + col * 4.05
        y = 2.15 + row * 1.75
        rounded(s, x, y, 3.55, 1.35, "", fill=LIGHT, line=RGBColor(220, 225, 232))
        box(s, x + 0.15, y + 0.12, 0.35, 0.3, num, size=15, color=TEAL, bold=True)
        box(s, x + 0.5, y + 0.12, 2.8, 0.3, title, size=14, color=NAVY, bold=True)
        box(s, x + 0.5, y + 0.5, 2.9, 0.65, body, size=10.5, color=GREY)
    rounded(s, 0.7, 5.8, 5.9, 0.62, "resultHash = SHA-256(canonical_json)", size=13, color=WHITE, fill=NAVY, bold=True, align=PP_ALIGN.CENTER)
    rounded(s, 6.85, 5.8, 5.8, 0.62, "Timestamp = chain_pos().block(), not wall clock", size=11, color=NAVY, fill=LIGHT, align=PP_ALIGN.CENTER)
    footer(s, 6)
    notes(s, "The workflow is deliberately simple. The requester supplies a range. Each node fetches logs, computes an integer metric, and produces a canonical JSON object. The result hash is SHA-256 over that canonical form. In the multi-node design, nodes sign the hash and a quorum is formed. The registry stores the hash and metadata, and a consumer reads the JSON back. The timestamp is the Lyquor block number, not wall-clock time, which is deterministic.")

    # 7. Implementation
    s = slide(prs)
    header(s, "Implementation", "Three small, testable pieces")
    cols = [
        ("Python reference", "Deterministic oracle", ["5 metrics", "canonical JSON + SHA-256", "tamper / quorum tests", "CLI demo"]),
        ("Rust Lyquid", "LDK 0.8.4", ["oracle two-phase code", "eth_getLogs via host HTTP", "network-state registry", "direct submit path verified"]),
        ("Solidity", "Sepolia-facing", ["EventSource events", "ResultRegistry", "authorized submitters", "Foundry tests"]),
    ]
    x = 0.7
    for title, sub, items in cols:
        rounded(s, x, 2.1, 3.75, 4.1, "", fill=LIGHT, line=RGBColor(220, 225, 232))
        box(s, x + 0.2, 2.3, 3.35, 0.35, title, size=16, color=NAVY, bold=True)
        box(s, x + 0.2, 2.7, 3.35, 0.3, sub, size=11, color=TEAL, bold=True)
        yy = 3.15
        for item in items:
            box(s, x + 0.2, yy, 3.3, 0.35, f"•  {item}", size=11, color=GREY)
            yy += 0.55
        x += 3.95
    footer(s, 7)
    notes(s, "Implementation is split into three pieces. The Python reference is the deterministic oracle for evaluation. The Rust Lyquid targets LDK 0.8.4 and contains the oracle code and the registry. The Solidity contracts are the Sepolia-facing event source and an optional result registry. This separation lets me test the protocol logic independently from the Lyquid deployment.")

    # 8. Evaluation
    s = slide(prs)
    header(s, "Results", "What was actually verified")
    table = s.shapes.add_table(6, 3, Inches(0.7), Inches(2.0), Inches(7.5), Inches(3.6)).table
    table.columns[0].width = Inches(3.3)
    table.columns[1].width = Inches(2.1)
    table.columns[2].width = Inches(2.1)
    rows = [
        ("Check", "Result", "Status"),
        ("Reference tests", "16 passed", "PASS"),
        ("Determinism", "5/5 hashes", "PASS"),
        ("Tamper 2-of-3", "CONSENSUS", "PASS"),
        ("Tamper 3-of-3", "DISPUTED", "PASS"),
        ("Single-node Lyquid", "count=1, has=true", "PASS"),
    ]
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            cell = table.cell(r, c)
            cell.text = text
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11 if r else 11.5)
                p.font.name = FONT
                p.font.bold = (r == 0 or c == 2)
                p.font.color.rgb = WHITE if r == 0 else (GREEN if c == 2 and r > 0 else NAVY)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if r == 0 else (WHITE if r % 2 else LIGHT)
    rounded(s, 8.55, 2.0, 4.1, 3.55, "", fill=RGBColor(245, 250, 250), line=TEAL)
    box(s, 8.75, 2.15, 3.7, 0.3, "Single-node run", size=14, color=TEAL, bold=True)
    box(s, 8.75, 2.55, 3.7, 2.8,
        "value = 69023557792913378\nevent_count = 44\nquorum = 1\ntimestamp = 12\nindexed = WETH9\n0xfff99767...4d6b14\n\nresult_hash =\n0x2d463896...589011\n\nsubmit tx =\n0x3e5a13c3...580c4b",
        size=9.0, color=NAVY)
    box(s, 0.7, 5.95, 11.9, 0.55, "The oracle update path is implemented but not claimed as verified on a single-node committee.",
        size=12, color=RED, bold=True)
    footer(s, 8)
    notes(s, "The reference implementation passes sixteen tests, including determinism, correctness against an independent recomputation, and tamper detection. The 2-of-3 case reaches consensus while recording the lying node as dissent. The 3-of-3 case is disputed. On the Lyquid side, the clean single-node run returned count one, has-result true, and a JSON record with hash 0x2d4638, value 69023557792913378, quorum one, and block timestamp twelve. The oracle update path did not complete on a single node, and I do not claim it as verified.")

    # 9. Limitations and conclusion
    s = slide(prs)
    header(s, "Limitations", "What this project does not prove")
    box(s, 0.7, 1.95, 5.8, 0.35, "Verified", size=17, color=GREEN, bold=True)
    box(s, 0.7, 2.35, 5.8, 1.5,
        "• Lyquid deployment and direct registry path\n• Canonicalization, hashing, quorum logic\n• Tamper and determinism evaluation",
        size=12, color=NAVY)
    box(s, 6.8, 1.95, 5.8, 0.35, "Not yet verified", size=17, color=RED, bold=True)
    box(s, 6.8, 2.35, 5.8, 1.7,
        "• Oracle two-phase update on single node\n• External user study\n• Multi-node committee and independent RPC\n• Reorg handling and production scale",
        size=12, color=NAVY)
    rounded(s, 0.7, 4.35, 11.9, 1.45, "", fill=NAVY)
    box(s, 0.95, 4.55, 11.4, 0.35, "Conclusion", size=13, color=TEAL, bold=True)
    box(s, 0.95, 4.9, 11.4, 0.7, "VeriIndex turns a historical query into a small, auditable fact — and the direct path already produces a real, readable Lyquid record.",
        size=15, color=WHITE, bold=True)
    footer(s, 9)
    notes(s, "The honest limitation is scope. I verified deployment, the direct registry path, canonicalization, hashing, and the tamper evaluation. I did not validate the oracle update path on a single node, I did not complete an external user study, and I did not run multiple independent nodes. The conclusion is that VeriIndex turns a historical query into a small auditable fact, and the direct path already produces a real readable Lyquid record. Multi-node oracle validation is the next step.")

    # 10. Demo
    s = slide(prs)
    header(s, "Demo", "Three-minute recorded demo",
           "Direct path only: index_local -> submit_result -> get_result")
    rounded(s, 0.65, 2.0, 12.0, 4.35, "", fill=RGBColor(16, 20, 28), line=RGBColor(40, 50, 65))
    box(s, 0.9, 2.15, 11.5, 0.3, "terminal  ·  single-node Lyquor devnet", size=10, color=RGBColor(140, 160, 180))
    lines = [
        "$ shaker deploy /ldk/veriindex/Cargo.toml",
        "  -> Lyquid-ahjg...  contract 0x0165...8f",
        "",
        "$ cast call ... index_local(contract, deposit_total, from, to)",
        "  # Sepolia WETH9, blocks 12212875..12212975",
        "  -> proposal { value: 69023557792913378, event_count: 44, result_hash: 0x2d4638... }",
        "",
        "$ cast send ... submit_result(...)",
        "  -> tx 0x3e5a13c3...580c4b",
        "",
        "$ cast call ... get_result_count()  -> 1",
        "$ cast call ... has_result(...)      -> true",
        "$ cast call ... get_result(...)      -> JSON record",
    ]
    yy = 2.55
    for ln in lines:
        color = RGBColor(150, 230, 180) if ln.startswith("  ->") else RGBColor(220, 228, 238)
        box(s, 0.9, yy, 11.5, 0.24, ln, size=10.5, color=color, font="Consolas")
        yy += 0.29
    box(s, 0.7, 6.55, 11.9, 0.35, "Recorded demo; the oracle update path is intentionally not shown as a success.",
        size=11, color=GREY)
    footer(s, 10)
    notes(s, "I will now switch to the recorded demo. It starts the single-node Lyquor devnet and deploys VeriIndex. The deploy output gives the Lyquid ID and the sequencer contract. It then calls index_local over a fixed Sepolia WETH9 range, 12212875 to 12212975. The proposal contains the canonical result and its hash. Next, submit_result writes the record into Lyquid network state. The transaction hash is 0x3e5a13. Finally, get_result_count returns one, has_result returns true, and get_result returns the JSON record with value 69023557792913378, quorum one, and block timestamp twelve. The oracle update path is not shown as a success because it did not complete on a single-node committee.")

    OUT.mkdir(parents=True, exist_ok=True)
    prs.save(PPTX)

    script = """# VeriIndex — 8-minute presentation script

Total target: **7:45–8:00**.  
Structure: **5 minutes presentation + 3 minutes recorded demo**.

## 0:00–0:15 — Title

Good morning. I'm Bettybear5. My project is **VeriIndex**, a verifiable historical event indexer built as a Lyquid on Lyquor. In the next five minutes I will explain the problem, the design, and the verified result. Then I will show a three-minute recorded demo.

## 0:15–0:55 — The problem

Historical on-chain data is public, but the aggregate is not verifiable. A protocol asks for trading volume or TVL, and receives a number from an indexer. It cannot tell whether the indexer used the requested block range, or whether independent operators agree. If one indexer is compromised, the result changes silently. This is the trust gap VeriIndex targets.

## 0:55–1:25 — Existing approaches

The Graph and Dune are powerful, but they return an off-chain answer. Chainlink-style oracles deliver values on chain, but they are optimized for current values, not arbitrary historical ranges. ZK coprocessors can prove computation, but the proving cost is high for simple analytics. The opening is a lightweight middle ground: deterministic re-execution by independent nodes, plus a small on-chain commitment.

## 1:25–2:05 — Contribution

The contribution has four parts. First, the unit of work is a historical range query, not a latest-value feed. Second, the result has a canonical JSON form, so independent implementations can compare byte-for-byte. Third, nodes produce signed proposals and the protocol records quorum and dissent. Fourth, only a hash and metadata go on chain, so the cost is low. The verified path in this project is `index_local`, `submit_result`, and `get_result`. I will be explicit later about the oracle path that is implemented but not validated on a single node.

## 2:05–2:50 — Architecture

This is the architecture. The requester asks for a contract, a metric, and a block range. The Lyquid indexer fetches logs from Sepolia, computes the metric, canonicalizes the result, and hashes it. Independent nodes can produce proposals. The quorum result is committed to Lyquid network state. Optionally, the same hash can be mirrored to a small Sepolia registry for external consumers. The important boundary is that the chain stores only a compact commitment, not the full history.

## 2:50–3:25 — Workflow

The workflow is deliberately simple. The requester supplies a range. Each node fetches logs, computes an integer metric, and produces a canonical JSON object. The result hash is SHA-256 over that canonical form. In the multi-node design, nodes sign the hash and a quorum is formed. The registry stores the hash and metadata, and a consumer reads the JSON back. The timestamp is the Lyquor block number, not wall-clock time, which is deterministic.

## 3:25–3:55 — Implementation

Implementation is split into three pieces. The Python reference is the deterministic oracle for evaluation. The Rust Lyquid targets LDK 0.8.4 and contains the oracle code and the registry. The Solidity contracts are the Sepolia-facing event source and an optional result registry. This separation lets me test the protocol logic independently from the Lyquid deployment.

## 3:55–4:30 — Results

The reference implementation passes sixteen tests, including determinism, correctness against an independent recomputation, and tamper detection. The 2-of-3 case reaches consensus while recording the lying node as dissent. The 3-of-3 case is disputed. On the Lyquid side, the clean single-node run returned count one, has-result true, and a JSON record with hash `0x2d4638`, value 69023557792913378, quorum one, and block timestamp twelve. The oracle update path did not complete on a single node, and I do not claim it as verified.

## 4:30–5:00 — Limitations and conclusion

The honest limitation is scope. I verified deployment, the direct registry path, canonicalization, hashing, and the tamper evaluation. I did not validate the oracle update path on a single node, I did not complete an external user study, and I did not run multiple independent nodes. The conclusion is that VeriIndex turns a historical query into a small auditable fact, and the direct path already produces a real readable Lyquid record. Multi-node oracle validation is the next step.

## 5:00–8:00 — Recorded demo

I will now switch to the recorded demo. It starts the single-node Lyquor devnet and deploys VeriIndex. The deploy output gives the Lyquid ID and the sequencer contract. It then calls `index_local` over a fixed Sepolia WETH9 range, 12212875 to 12212975. The proposal contains the canonical result and its hash. Next, `submit_result` writes the record into Lyquid network state. The transaction hash is `0x3e5a13`. Finally, `get_result_count` returns one, `has_result` returns true, and `get_result` returns the JSON record with value 69023557792913378, quorum one, and block timestamp twelve. The oracle update path is not shown as a success because it did not complete on a single-node committee.

## Q&A preparation

- **Why 2-of-3?** It is the demo quorum for the reference; the live single-node run uses one node.
- **What does the chain store?** Only the result hash and metadata; the full result stays off chain.
- **Is quorum a proof?** No. A malicious majority can collude; the design makes dissent visible, not impossible.
- **Why is the timestamp a block number?** `systime` is only valid in instance functions; network-state writes use `chain_pos().block()`.
- **Why is the oracle path not shown?** It is implemented, but the single-node proposal aggregation did not produce a certified update. The direct registry path is the verified result.
"""
    SCRIPT.write_text(script, encoding="utf-8")
    print(f"wrote {PPTX}")
    print(f"wrote {SCRIPT}")


if __name__ == "__main__":
    build()
