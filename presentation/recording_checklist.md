# Recording checklist — VeriIndex 8-minute demo

## 1. Files to open before recording

- [ ] `presentation/CS5298_VeriIndex_Presentation.pptx`
- [ ] `presentation/demo_recording_guide.md` (for narration timing)
- [ ] `presentation/demo_assets/lyquid-run-direct.json`
- [ ] GitHub Actions run (optional):
      `https://github.com/Bettybear5/CS5298-VeriIndex/actions/runs/45728324966`

## 2. Screen layout

Recommended:

- Left: PPT or terminal
- Right: JSON evidence
- Terminal font: 20–24 pt
- Resolution: 1920×1080
- Frame rate: 30 fps
- Close notifications, chat, private tabs
- Hide `.env`, private keys, tokens

## 3. Recording settings

- [ ] Microphone tested for 10 seconds
- [ ] System audio muted unless needed
- [ ] Cursor visible but not shaking
- [ ] No private browser bookmarks on screen
- [ ] Recording timer visible

## 4. Exact values to show

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

## 5. 8-minute structure

| Time | Content |
|---|---|
| 0:00–5:00 | Slides 1–9 |
| 5:00–5:15 | Transition to demo |
| 5:15–5:45 | Deployment |
| 5:45–6:30 | `index_local` + 44 events / value |
| 6:30–7:10 | `submit_result` + count/has |
| 7:10–7:45 | Full `get_result` JSON |
| 7:45–8:00 | Limitation + close |

## 6. If local Docker is unavailable

Do not fake a live run. Use either:

1. GitHub Actions run page `45728324966`
2. Recorded evidence replay:

```bash
cd /home/bettybear5/CS5298-VeriIndex
bash presentation/show_demo_evidence.sh
```

Say explicitly:

> This is the recorded output of the submitted implementation on the single-node Lyquor devnet.

## 7. Do not show / do not claim

- [ ] Do not claim the oracle `update` path is verified
- [ ] Do not show `RESULT_NOT_FOUND`
- [ ] Do not use the old `value=0` result
- [ ] Do not show private keys, `.env`, tokens
- [ ] Do not run `report_result` in the 3-minute demo

## 8. Export and submission

- [ ] Export MP4, H.264, 1920×1080, 30 fps
- [ ] Total length ≤ 8:00
- [ ] Demo section ≤ 3:00
- [ ] Save as `demo/CS5298_VeriIndex_Demo.mp4`
- [ ] Run `bash submission/package.sh`
- [ ] Upload `report/CS5298_VeriIndex_Report.pdf`
- [ ] Upload `submission/CS5298_VeriIndex_Demo.zip`
