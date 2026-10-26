---
name: drug-research-report
description: Research drugs with citations and save a structured report.
version: 0.1.0
author: Hermes
platforms:
  - windows
  - linux
  - macos
metadata:
  hermes:
    tags:
      - Research
      - Drugs
      - Reporting
---
# Drug Research Report Skill

Conduct a verifiable, citation-heavy research workflow for drugs, chemicals, and related hazards. The skill documents the actual workflow used for ニタゼン research: search, extract, synthesize, save, and remember.

## When to Use
- User requests research on a drug, synthetic opioid, chemical hazard, or forensic substance.
- User wants a structured report with tables, references, and a saved markdown file.
- User wants the findings stored to memory and a reusable output path.

## Prerequisites
- No external credentials required. Internet access via `web_search`/`web_extract`.
- Optional: a local path for the report (defaults to `Documents`).

## How to Run
1. Invoke through Hermes tools: `web_search` → `web_extract` → `write_file` → `memory` add.
2. Use `terminal` only if a script is required.

## Quick Reference
- `web_search(query="ニタゼン", limit=10)`
- `web_extract(urls=[...])`
- `write_file(path=".../report.md", content=...)`
- `memory` action add with report path.

## Procedure
1. **Clarify scope**: Confirm the substance name in Japanese and English.
2. **Initial search**: Run `web_search` with the Japanese name and English name.
3. **Deepen with authoritative sources**: Extract Wikipedia, WSJ, BBC, FNN, official prefectural sites, UNODC.
4. **Synthesize structure**: Definition, potency table, crisis timeline, Japan situation, detection/metabolism, references.
5. **Persist**: `write_file` to `C:\Users\<user>\Documents\<SUBSTANCE>_リサーチ_<YYYY-MM-DD>.md`.
6. **Memory**: Add a concise summary to `memory` with the report path.
7. **Verification**: Read the file back with `read_file` to confirm it exists.

## Pitfalls
- Never claim statistics not sourced. If Japanese death statistics are not compiled, state "not compiled".
- Distinguish parent drug from analogs. Cite both.
- Avoid inventing potency numbers.

## Verification
`read_file(path="<report_path>", limit=5)` should show the header with date and substance.
