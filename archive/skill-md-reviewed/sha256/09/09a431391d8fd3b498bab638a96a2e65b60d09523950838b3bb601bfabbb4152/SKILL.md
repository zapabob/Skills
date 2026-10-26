---
name: notebooklm-cli-workflow
description: "Drive Google NotebookLM via the `nlm` CLI (v0.8.4+) to compile a local source pack into a notebook and generate artifacts (Audio Overview, reports, mind maps). Use when the user wants to ingest local files/PDFs/markdown into NotebookLM, build a research notebook, or generate audio/report/mindmap from sources. Covers CLI-specific quirks the bundled `nlm-skill` does not document: auth-first human login, notebook_id capture (no --quiet), per-command --language support, audio 'unknown' status polling, and source-pack granularity for better citations."
version: "1.0.0"
---

# NotebookLM CLI Workflow (nlm)

Practical, agent-run playbook for NotebookLM via the `nlm` CLI. The CLI shares the
same auth backend as the `notebooklm-mcp` MCP server, so CLI login satisfies MCP too.
For the full command catalog see the bundled `nlm-skill`; this skill captures the
CLI-only behaviors that bite agents in practice.

## When to use
- Ingest a locally-built source pack (PDF + markdown files) into NotebookLM.
- Create a research notebook from disk and generate Audio Overview / report / mind map.
- You have `nlm` on PATH but no MCP `notebooklm-mcp__*` tools in the current session.

## Hard rules
1. **Auth-first, but auth needs a human.** Run `nlm login --check` before ANY op.
   - `✓ Authentication valid!` → proceed.
   - `Authentication expired` / `ClientAuthenticationError` → STOP. The user must run
     `nlm login` in a real terminal (browser Google OAuth — an agent CANNOT complete
     it). Don't claim the work is done while auth is dead.
   - Distinguish network vs auth: `curl -sS -o /dev/null -w "%{http_code}" https://notebooklm.google.com`
     returning 302 + reachable API means it's auth, not connectivity.
2. **`nlm notebook create` has NO `--quiet`** (only `notebook list --quiet` exists).
   It prints a JSON blob with `"notebook_id"`. Capture that ID. Passing `--quiet` to
   create errors: `No such option: --quiet`.
3. **`nlm mindmap create` REJECTS `--language`** (unlike audio/report/slides/etc.).
   Language is auto-detected from sources. Passing `--language ja-JP` fails with
   `No such option: --language`. Omit it for mind maps.
4. **Audio Overview is asynchronous and propagation can lag.**
   `nlm audio create` returns an Artifact ID immediately; `nlm studio status <notebook_id> --json`
   may report `"status": "unknown"` for several minutes. Poll every ~15–20s; it normally
   flips to `completed`. Even after `completed`, the media URL may temporarily return
   404 while propagating. Retry the download with backoff (the CLI uses 5s, 10s, 20s,
   30s); treat this as transient propagation lag, not permanent failure.
5. **Local file uploads need a real host path.** `nlm source add --file <path>` and
   MCP `source_add(file)` both require the path to exist on the machine running `nlm`
   (the MCP host / the CLI host), NOT merely on a client. Use `--wait` to block until
   the source shows `ready`.

## More CLI quirks (discovered in practice)
- **`nlm audio create --length` valid values are `default`, `long`, `short` — NOT `medium`.**
  Passing `medium` errors: `Error: Unknown audio length 'medium'. Valid options: default, long, short`.
  Use `long` for a deep-dive interview-prep / brief overview.
- **`nlm quiz create` / `nlm flashcards create` `--format markdown` downloads a STUB**
  (often just a `# <Title>` line). The real content is in `--format html`. Always download
  the HTML version for quiz/flashcard artifacts; treat the markdown file as effectively empty.
- **`nlm report create` and `nlm slides create` accept `--title "..."`** (free-text, artifact
  label). Useful when stacking multiple generations in one notebook so artifacts are distinguishable.
  The title does NOT alter source-derived content, only the artifact's display name.
- **`nlm data-table create <notebook_id> "<natural-language spec>"`** takes the spec as a
  positional quoted string (NO `--focus`). Export to Sheets with
  `nlm export to-sheets <notebook_id> <data_table_id> --title "..."` (returns a docs.google.com URL).
  Get the data_table id from `nlm studio status <notebook_id> --json` filtering `type=="data_table"`.

## Workflow (reproducible)
See `references/cli_source_pack_workflow.md` for a full worked example: build a
Japanese source pack (reportlab PDF + per-topic markdown) → create notebook → add 5
local files with `--wait` → generate audio(deep_dive,ja) + report(Briefing Doc,ja) +
mindmap → poll → download report.

## Source-pack granularity
Upload SEVERAL separate source files rather than one monolith:
`company_official.md`, `salary_reviews.md`, `org_design.md`, plus a compiled PDF.
NotebookLM cites per-source, so finer splits yield more precise, traceable answers.

## Windows / Japanese PDF tip
When building the PDF with reportlab, register the font with a NATIVE Windows path
(`C:/Windows/Fonts/YuGothR.ttc`), not an MSYS path (`/c/Windows/Fonts/...`) — reportlab
cannot resolve MSYS paths and the build fails.

## PDF text extraction fallback via PyMuPDF
When `read_file` reports a PDF-extracted `.txt` as `is_binary: true` despite `file`
reporting UTF-8 text, switch to terminal-based reading instead of retrying `read_file`:
```bash
cat "C:/path/to/extracted.txt"
```
or PowerShell equivalent. This bypasses the false binary classification and returns the
actual UTF-8 text. For the initial PDF→text extraction itself, run PyMuPDF through
`py -3` in terminal:
```bash
py -3 -c "
import fitz, os
path = r'%USERPROFILE%\Downloads\...pdf'
doc = fitz.open(path)
text = '\n'.join(page.get_text() for page in doc)
out = os.path.join(r'%USERPROFILE%\.hermes\notebooklm\output\...', name.replace('.pdf','.txt'))
with open(out,'w',encoding='utf-8') as f:
    f.write(text)
print(name, len(doc), len(text))
"
```
Use this when `execute_code` sandbox lacks `fitz` but the system Python installed via
`py -3 -m pip install pymupdf` has it. This pattern is especially reliable for
application documents (履歴書/職務経歴書/スキルシート/カバーレター PDFs).

## Note on `read_file` false binary classification
Some UTF-8/CRLF `.txt` files extracted from PDFs are misclassified as binary by
`read_file` even though `file` reports `Unicode text, UTF-8 text`. Do not loop on
`read_file` for these; use terminal `cat` or PowerShell `Get-Content` once and move on.

## July 2026 Session Troubleshooting
See `references/troubleshooting_jul2026.md` for detailed issues and fixes encountered
when running `nlm` via `uv tool install`, including:
- `pydantic_core._pydantic_core` ModuleNotFoundError fix (PYTHONPATH)
- Audio download extension requirement (`.m4a`/`.mp4`, not `.mp3`)
- Multiple artifact status polling (`unknown` → `completed`)
- Slide/video download failure workarounds
- Consumer mode notebook targeting
- File upload path requirements
- Auth flow limitations
- Rate limiting guidelines
- Source pack granularity best practice

## Module-invocation fallback when `nlm` wrapper is broken
After `pip install notebooklm-mcp-cli`, the `nlm` wrapper can still fail with:
`ModuleNotFoundError: No module named 'notebooklm_tools'`.
If `nlm login --check` errors that way, invoke the installed package directly:

```bash
py -3 -m notebooklm_tools.cli.main <command>
```

Example:
```bash
py -3 -m notebooklm_tools.cli.main login --check
py -3 -m notebooklm_tools.cli.main notebook create "Title"
py -3 -m notebooklm_tools.cli.main source add <nb> --file <path> --wait
py -3 -m notebooklm_tools.cli.main report create <nb> --format "Briefing Doc" --language ja-JP -y
```

If you previously relied on `uv tool install` and see `pydantic_core._pydantic_core` import\nerrors, reinstall with `py -3 -m pip install notebooklm-mcp-cli` and use the module path above.\nThe `PYTHONPATH` uv-tool workaround is no longer needed once the package is installed into\nthe same Python that runs `py -3`.

## NotebookLM MCP tool calling in Hermes
Some Hermes sessions expose `notebooklm-mcp` tools through the MCP gateway instead of the `nlm` CLI. If a direct `tool_call` returns `'<tool> is not a deferrable tool'`, do not keep retrying `tool_call`. Switch to the CLI invocation path above or to the local MCP server config under `~/.hermes/config.yaml`. This avoids an infinite retry loop when a tool is available but not deferred.

## Research fallback when `web_extract` is blocked
When `web_extract` returns a 402 billing error, do not retry the same call. Use:\n- `browser_navigate` + `browser_snapshot` for JS-heavy pages\n- `curl` + text extraction for static pages\nThis keeps notebook source collection moving when the fast path is rate-limited.

## OpenManus fallback behavior\nOpenManus plugin tools are preferred for bounded delegated research, but if this session does not expose them, fall back to direct `web_search` + `web_extract`/`browser_navigate` research instead of blocking the workflow.

## Continue-by-default execution style\nWhen the user replies with only "続けて", continue the next concrete end-to-end step without asking. Only stop for true blockers or irreversible actions; otherwise execute, verify, and report real results.

## Audio download extension
`nlm download audio` requires `.m4a` or `.mp4` suffix (NotebookLM delivers AAC in MP4).
Using `.mp3` errors with: `NotebookLM delivers AAC audio in an MP4 container; cannot honor '.mp3' suffix.`

## Multiple artifacts of same type
`nlm studio status` can return multiple artifacts of the same type (audio, video, slide_deck).
Check `status: "completed"` before downloading — `status: "unknown"` means still generating.
Poll every ~15–20s until it flips to `completed` (usually 1–5 min for audio).

## Slide deck / video download failures
`nlm download slide-deck` and `nlm download video` can fail with `Download failed` on
some artifact IDs even when status shows `completed`. Try the latest artifact ID of
that type from `studio status --json`. Video downloads are large (50MB+) — allow
timeout ≥ 180s.

## Auth can expire mid-session
Even after `login --check` succeeds, a later command can fail with `Authentication expired`.
When that happens, stop and ask the user to run `py -3 -m notebooklm_tools.cli.main login`
in a real terminal. After they confirm, retry the notebook workflow from the beginning;
do not assume previously captured notebook/source IDs are still valid after auth recovery.

## Artifact download pattern
Most artifact downloads follow:
```bash
py -3 -m notebooklm_tools.cli.main download <type> <notebook_id> --id <artifact_id> -o <output_path>
```
Common `<type>` values: `report`, `audio`, `mind-map`, `quiz`, `flashcards`, `data-table`,
`infographic`, `slide-deck`, `video`. Output suffixes should match the artifact type:
`.md` for reports, `.m4a`/`.mp4` for audio, `.html` for mind maps/infographics/quiz/flashcards/data tables.
If a download fails with `Download failed` while `status` is `completed`, fetch the latest
artifact ID of that type from `studio status --json` and retry with that ID.

## Studio status JSON
The notebook ID is a positional argument; do not use `--notebook-id`:
`py -3 -m notebooklm_tools.cli.main studio status <notebook_id> --json`
Use this command to list all studio artifacts with their IDs, types, and statuses.
statuses. Filter or scan for the desired `type` and a `completed` `status` before downloading.
`status: "unknown"` means NotebookLM is still generating; poll every ~15–20s.

## Notebook selection for consumer sync
When syncing via consumer CLI (no Enterprise creds), the plugin auto-falls back to
consumer mode. The target notebook ID can be:
- `NOTEBOOKLM_MCP_NOTEBOOK_ID` env var
- `--notebook-id` argument
- auto-create with `--create` / `create_notebook=true`

If multiple notebooks exist, explicitly set the target to avoid uploading to the wrong one.
