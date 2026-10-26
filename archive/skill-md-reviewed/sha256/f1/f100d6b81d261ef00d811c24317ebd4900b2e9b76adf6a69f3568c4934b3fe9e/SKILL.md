---
name: recruiter-job-board-sync
description: Use for weekly job-board NEW/UPDATE scans and diff scripts.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [recruiting, jobs, kanban, diff, snapshot]
    category: job-recruiter
---

# Recruiter Job-Board Sync Skill

Weekly NEW / UPDATE / REMOVED diff for tracked job boards. Replaces naive
"parse cache and flag unseen rows" logic, which silently reports every parsed
row as new when the seen-store is empty or namespaced wrong.

This skill does NOT post, apply, or message anyone. It only produces a diff.

## When to Use

- A weekly/periodic recruiter sync card asks for "new postings", "description
  updates", or "closed/removed" counts.
- A previous run's numbers look implausible (tens of NEW every single week).
- You are asked to fix or trust a job-scraping/diff script.

## Prerequisites

- Python 3 on PATH.
- Network access to the tracked boards (HTTP GET only).
- Installed scanner: `%USERPROFILE%/Documents/ops/job-recruiter/scanner/`
  (`scan_jobs.py`, `selftest_scan.py`, `baseline/`, `snapshots/`).

## Quick Reference

```
python %USERPROFILE%/Documents/ops/job-recruiter/scanner/scan_jobs.py cycle
python %USERPROFILE%/Documents/ops/job-recruiter/scanner/selftest_scan.py
```

`cycle` = fetch -> parse -> report -> promote baseline.
Actions: `fetch`, `parse`, `diff`, `report`, `cycle`, `promote`.

## Procedure

1. **Run the self-test first.** `selftest_scan.py` mutates a throwaway copy of
   the baseline and asserts add/remove/update are detected. If it does not
   print `ALL CHECKS PASSED`, the diff is not trustworthy — stop and fix it.
2. **Run `cycle`.** First ever run prints `state: baseline_established` and
   0/0/0 for every source. That is correct, not a failure: there is no prior
   snapshot to compare against. Report it as "baseline established", and do
   NOT invent new-posting numbers from it.
3. **Read `added` / `updated` / `removed` per source.** These are keyed by the
   site's own stable id (URL slug), never by a slugified title.
4. **Sanity-check the magnitude.** Tens of NEW on a board that rarely posts
   means the parser regressed or the baseline was reset — investigate before
   reporting.
5. **Write the report** to
   `%USERPROFILE%/Documents/ops/job-recruiter/reports/YYYY-MM-DD-recruiter.md`
   with: counts per source, root cause if anything was wrong, artifacts, and an
   explicit "no external posting/application performed" line.
6. **Reuse the existing kanban card.** Do not create a duplicate for the same
   sync period. Add a `kanban_comment` with the counts and the report path.

## Pitfalls

- **Never compare parsed rows against a shared/foreign seen-store.** A store
  holding only `gmail:*` and unrelated `web` URLs makes every row new by
  construction. Keep per-source snapshots.
- **Never build diff keys from titles.** Japanese titles slugify into
  non-existent URLs, and HTML entities (`&amp;`) leak through.
- **Herp.careers changed URL scheme.** The old
  `https://herp.careers/v1/tier4/jobs/{4-digit}` now returns HTTP 400. Current
  canonical form is `https://herp.careers/v1/tier4/{opaque-slug}` (e.g.
  `-ZLzb5ZwQO7t`). Digits in a Herp *title* (`1008_Planning and Control
  Engineer`) are legacy labels, not ids.
- **HRMOS list cards leak non-job rows**: street addresses
  (`東京都港区浜松町2丁目3-1 …`), counters (`全 62 件中 62 件 を表示しています`),
  bare numbers, and employment-type labels (`正社員`). Filter them.
- **A 0/0/0 diff can be real or a bug.** Always run the self-test before
  reporting zeros, otherwise you cannot distinguish "nothing changed" from
  "the diff never fires".
- **A missing snapshot is not a zero diff.** It must surface as
  `no_snapshot`; silently counting it as 0 hides a broken fetch.
- Grepping a 300KB single-line HTML file for a long pattern can hang past the
  terminal timeout — parse with Python instead.
- On this host, the Security Center blocks `cd DIR && python foo.py` and
  `python -c`. Run `python "C:/abs/path/script.py"` as a standalone command.

## Verification

Done only when all of these are true:

1. `selftest_scan.py` prints `ALL CHECKS PASSED`.
2. The live run reports a per-source `state` of `baseline_established` or
   `compared` — never `no_snapshot` for a board you intended to scan.
3. Noise probes find zero matches: no `"title": "62"`, no `東京都` headings, no
   `件中` counters in the snapshot JSON.
4. The report states the three counts, names the artifacts, and states that no
   external application/posting was performed.
