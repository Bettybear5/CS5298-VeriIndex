#!/usr/bin/env python3
"""Render report/report.md to a PDF with a clean academic layout."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "report" / "report.md"
DEFAULT_OUTPUT = ROOT / "report" / "CS5298_VeriIndex_Report_DRAFT.pdf"

CSS = """
@page {
  size: A4;
  margin: 22mm 20mm 20mm 20mm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #444; }
  @top-center {
    content: "DRAFT — contains TBD placeholders; do not submit";
    font-size: 8pt;
    color: #b00020;
  }
}
@page :first { @top-center { content: ""; } }
body {
  font-family: "Liberation Serif", "Times New Roman", serif;
  font-size: 10.8pt;
  line-height: 1.45;
  color: #111;
  text-align: justify;
  hyphens: auto;
}
h1 { font-size: 20pt; line-height: 1.2; margin: 0 0 6pt 0; text-align: center; }
h2 { font-size: 13.5pt; margin: 16pt 0 6pt 0; border-bottom: 0.6pt solid #999; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt 0; }
p { margin: 0 0 6pt 0; }
ul, ol { margin: 4pt 0 8pt 0; padding-left: 22pt; }
li { margin-bottom: 2pt; }
code { font-family: "Liberation Mono", monospace; font-size: 9pt; background: #f3f3f3; padding: 0 2pt; }
pre { background: #f6f6f6; border: 0.5pt solid #ddd; padding: 7pt; font-size: 8.8pt; line-height: 1.25; overflow-wrap: break-word; white-space: pre-wrap; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0 10pt 0; font-size: 9.2pt; }
th, td { border: 0.5pt solid #777; padding: 3pt 4pt; vertical-align: top; text-align: left; }
th { background: #ececec; }
blockquote { margin: 8pt 0; padding: 7pt 10pt; background: #fff4e5; border-left: 3pt solid #d97706; }
a { color: #123c8c; text-decoration: none; }
strong { font-weight: bold; }
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--final", action="store_true", help="omit the DRAFT banner")
    args = parser.parse_args(argv)

    text = args.source.read_text(encoding="utf-8")
    if args.final and "[TBD]" in text:
        print("refusing to build a final PDF: report still contains [TBD]", file=sys.stderr)
        return 2
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
    )
    css = CSS.replace(
        'content: "DRAFT — contains TBD placeholders; do not submit";',
        'content: "";',
    ) if args.final else CSS

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<style>{css}</style></head><body>{body}</body></html>"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
