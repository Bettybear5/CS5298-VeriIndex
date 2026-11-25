# AI use log

Record each AI-assisted task. The report's AI Use Statement should summarize
this log.

| Date | Tool | Task | Output reviewed by | Validation |
|---|---|---|---|---|
| 2026-11-25 | opencode | Extracted the assignment PDF text and outlined requirements | Bettybear5 | Checked against the PDF |
| 2026-11-25 | opencode | Drafted project scope, architecture, and evaluation plan | Bettybear5 | Reviewed for accuracy; no invented Lyquor API |
| 2026-11-25 | opencode | Scaffolded reference implementation and tests | Bettybear5 | Ran `pytest` and the CLI demo |
| 2026-11-25 | opencode | Integrated the Lyquid crate with the official LDK oracle pattern and RPC fetching | Bettybear5 | Reviewed against the LDK price-feed example; compile/deploy still required in Docker |
| TBD | opencode | Language editing of the report | Bettybear5 | Manual verification of claims and numbers |

## Rules

- Do not submit generated text without checking it against the code and papers.
- Do not claim results that were not produced by a run.
- Do not include real credentials or private keys in prompts or outputs.
- Mark placeholders clearly and fill them before submission.
