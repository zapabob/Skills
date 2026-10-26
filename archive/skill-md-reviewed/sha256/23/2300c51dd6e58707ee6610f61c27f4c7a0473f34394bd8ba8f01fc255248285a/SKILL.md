---
name: notebooklm-source-pack
description: "Compile sources into NotebookLM markdown and PDF packs."
version: 0.1.0
author: Hermes
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [NotebookLM, PDF, Research-Compilation, ReportLab, Sources]
    category: productivity
    related_skills: [pdf, docx, hyperframes, company-deepresearch]
---

# NotebookLM Source Pack

Turn a conversation, research thread, or company brief into a **NotebookLM-ready source pack**: several focused markdown files plus one unified Japanese PDF, zipped to the desktop.

**What it does**: Gathers real source material (web research + browser scrape + local files), structures it into numbered source files, renders a clean Japanese PDF, and packages everything into a zip.

**What it does NOT do**: Summarize for a human reader only — the output is optimized as *NotebookLM sources* (multiple documents with clear provenance headers).

**Dependencies**: Python `reportlab` + a CJK font. On Windows use `C:/Windows/Fonts/YuGothR.ttc`. Cross-platform fallback: `pip install reportlab`.

## When to Use

- "NotebookLM にこのスレッドをまとめたい"
- "Make a source pack for NotebookLM from this research"
- "Compile these findings into uploadable sources"
- Any task ending in "→ NotebookLM" or "→ 資料化して zip"

## Prerequisites

- `pip install reportlab` (weasyprint/pandoc often absent; reportlab is reliable)
- CJK font present: Windows `C:/Windows/Fonts/YuGothR.ttc` (bold: `YuGothB.ttc`); macOS `/System/Library/Fonts/Hiragino`; Linux `fonts-noto-cjk`
- `web_extract` requires xAI credentials — **do NOT rely on it**; use `web_search` + `browser_navigate` instead (see Pitfalls)

## How to Run

```bash
# 1. Gather: web_search for facts, browser_navigate to scrape pages (NOT web_extract)
# 2. Write numbered source files under notebooklm_sources/
# 3. Build PDF with the bundled script (scripts/build_pdf.py)
# 4. Zip everything to desktop
```

## Quick Reference

| Step | Tool | Output |
|------|------|--------|
| Research | `web_search`, `browser_navigate` | facts + snapshot text |
| Sources | `write_file` | `notebooklm_sources/01_*.md` ... |
| PDF | `terminal` (python + reportlab) | `*.pdf` (6+ pages) |
| Package | `terminal` (zipfile) | `Desktop/*.zip` |

## Procedure

1. **Gather real data**. `web_search` first (fast facts: salary, outlines). Then `browser_navigate` to the official site / press release and read the AX snapshot for tables.
2. **Write 2–4 source files** under `notebooklm_sources/` named `01_company_official.md`, `02_openwork_salary.md`, `03_design.md`. Each starts with a provenance header (`> 出典: URL (取得日)`).
3. **Build the PDF** using the bundled script `scripts/build_pdf.py` (run via the `terminal` tool): `python scripts/build_pdf.py out.pdf notebooklm_sources/*.md`. It parses the markdown (headings, tables, lists) and renders with the CJK font. Override `FONT`/`FONT_B` for non-Windows OS.
4. **Zip to desktop**: `zipfile` with the PDF + thread md + `notebooklm_sources/` folder. Save to `C:/Users/<user>/Desktop/`.
5. **Verify**: `zip.testzip()` returns `None`; PDF opens with `pypdf` (`len(pages) >= 1`).

## Pitfalls

- **`web_extract` fails with "No xAI credentials found"** → fall back to `browser_navigate` + read the snapshot. Never block on web_extract.
- **reportlab cannot resolve MSYS paths** (`/c/Windows/Fonts/...` throws `FileNotFoundError`). Use native path `C:/Windows/Fonts/YuGothR.ttc`.
- **Font must be registered with `subfontIndex=0`** for `.ttc` collections or glyphs render blank.
- **Tables in markdown**: parse `|` rows; skip the `|---|` separator line; set `colWidths` to fit A4.
- **Don't over-truncate numbers**: keep exact figures (e.g. 資本金36.0億円, 社員211名) — NotebookLM answers from them.
- **Provenance**: every source file must cite its URL + fetch date so NotebookLM citations are trustworthy.
- **Concurrent modification → false `testzip()` BROKEN**: if a sibling subagent or another process is still writing the source `.md` files while you build the zip, `z.testzip()` may report `BROKEN: <file>` even though the file is valid on disk. Symptom: `z.read()` of the "broken" member succeeds and returns correct bytes. Fix: re-run the zip build after all writes settle, then verify again (should report `OK`).
- **Reconcile the thread-summary before packaging**: if a `-thread.md` summary predates the verified source files, fix every number in it to match the verified sources (e.g. 6,000社/200万名, 資本金36.0億円, 平均年収545万円, 社員211名). Never ship a pack where the summary and the sources disagree — NotebookLM answers from all of them and inconsistency poisons citations.
- **Heredoc `&` false-positive**: the `terminal` foreground parser can reject a command as "uses '&' backgrounding" when a `python - <<'PY' … PY` heredoc contains a `&` (e.g. `zlib.crc32(data) & 0xffffffff`). Workaround: put the script in a `.py` file and run `python script.py` instead of inlining via heredoc.

## Verification

```bash
python -c "import zipfile; z=zipfile.ZipFile('C:/Users/<user>/Desktop/notebooklm_pack.zip'); print('integrity', 'OK' if z.testzip() is None else 'BROKEN')"
python -c "from pypdf import PdfReader; print('pdf pages', len(PdfReader('notebooklm_pack.pdf').pages))"
```
