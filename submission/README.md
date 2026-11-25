# Submission package

The course asks for two separate uploads:

1. **Project report PDF** with a public GitHub repository URL.
2. **Demo recording ZIP**.

This directory contains the packaging helper. It does not fabricate the report
results or the recording.

## Before packaging

- [ ] Replace every `[TBD]` in `report/report.md`.
- [ ] Add the public GitHub URL to Section 4.1 of the report.
- [ ] Add the solo-group instructor approval date in Section 7.
- [ ] Fill in the Lyquid devnet results, Sepolia addresses, and user study.
- [ ] Record the 8-minute demo and save it as `demo/CS5298_VeriIndex_Demo.mp4`.
- [ ] Run `bash scripts/reproduce.sh` one final time.
- [ ] Make sure the GitHub repository is public and the README works from a
      clean checkout.

## Build the final report PDF

```bash
cd /home/bettybear5/CS5298-VeriIndex
python3 scripts/build_report.py --final --out report/CS5298_VeriIndex_Report.pdf
```

The script refuses to create a "final" file if `[TBD]` is still present.

## Build the demo ZIP

```bash
bash submission/package.sh
```

This creates `submission/CS5298_VeriIndex_Demo.zip` from the demo recording.
The script checks that the file exists and is not empty.

## Submit

Upload through Canvas:

- `report/CS5298_VeriIndex_Report.pdf`
- `submission/CS5298_VeriIndex_Demo.zip`

Keep a local copy of both files and the evidence directory.
