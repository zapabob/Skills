---
name: generic-agent-harness
description: "Govern fork as generic harness with zero Nous dependency."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fork, harness, brand-separation, upstream-sync, windows-workstation]
    category: devops
    related_skills: [a2a-bot-meeting, antigravity-cli, hermes-agent]
---

# Generic Agent Harness Governance

Operate `zapabob/hermes-agent-windows` as a **generic AI agent harness** and **Windows universal AI workstation base** with zero runtime dependency on `NousResearch/hermes-agent`. Nous is upstream only — fetched until stall, then frozen.

## When to Use

- "make this fork independent / generic harness"
- "brand separation / Nous decoupling"
- "upstream sync policy / merge harness"
- "Windows workstation harness growth"
- "Phase 2 vs harness expansion sequencing"

## Prerequisites

- `origin = zapabob/hermes-agent-windows`, `upstream = NousResearch/hermes-agent` (`git remote -v`)
- Merge harness: `scripts/merge_tools/hermes-merge-conflict-strategies.json` (4 actions: `upstream` / `preserve_custom` / `official_with_overlay` / `manual_api_followup`)
- Snapshot pin: `.codex/UPSTREAM_SNAPSHOT.json` / `UPSTREAM_ADOPTION.yaml` / `CARRY.yaml`
- Docs: `fork/README.md`, `fork/harness/GENERIC_HARNESS.md`, `_docs/2026-09-03_generic-harness-independence.md`

## How to Run

### 1. Brand audit (Step A — low-risk doc separation)

```bash
# Count brand strings in tracked files only (excludes ~/.hermes cache noise)
git ls-files | xargs grep -l "NousResearch" | wc -l
git ls-files | xargs grep -l "hermes-agent" | wc -l
git ls-files | xargs grep -l "NousResearch" | grep -v "^\.codex/UPSTREAM" | grep -v "^\.github/workflows" | grep -v "_docs" | grep -v "\.omo"

# System prompt brand lock (single runtime site)
grep -rn "You are Hermes Agent.*Nous Research" agent/prompt_builder.py
# brain contamination check
grep -n "Predatory Merge Protocol" brain/SOUL.md
```

Classify hits:

| Keep (attribution) | Separate (Step A) | Defer to Step C |
|---|---|---|
| `LICENSE` copyright, `UPSTREAM_SNAPSHOT`, `CONTRIBUTING` attribution, `README` `independent of Nous Research` line, `pyproject.toml` authors | `fork/README.md`, `fork/harness/GENERIC_HARNESS.md`, `README.md` one-line generic-harness addition | `agent/prompt_builder.py:151,161,176` system prompt, `toolsets.py` overlay |

Step A must stay in `preserve_custom` / `official_with_overlay(overlap_only)` — never touch `official_with_overlay` core files. See `references/brand-audit-2026-09-03.md` for the 2026-09-03 inventory (388 NousResearch / 955 hermes-agent hits).

### 2. Upstream sync

```powershell
py -3 scripts/sync_all.py --dry-run
$preMergeSha = git rev-parse HEAD
py -3 scripts/sync_all.py --merge --target main --allow-preflight-blockers
py -3 scripts/merge_tools/apply_post_merge_overlay.py --upstream-ref upstream/main --old-head $preMergeSha
```

### 3. Growth sequencing (A2A hybrid consensus 2026-09-03)

```
Step A (serial, low-risk):  doc/fork brand separation → merge stabilizes
Step B (parallel, isolated): harness expansion via plugins (preserve_custom) → user value
Step C (serial, high-risk):  core brand separation (prompt_builder, toolsets) → full independence
```

A2A debate (4 perspectives) converged on hybrid: doc-first + plugin-parallel, not pure Phase-2-first or expansion-first. See `references/a2a-hybrid-consensus-2026-09-03.md`.

### 4. Antigravity as harness provider

```bash
command -v agy && agy --version          # 1.1.12 @ AppData/Local/agy/bin/agy
agy models                                 # OAuth OK → gemini-3.8-flash, claude-sonnet-4-6, gpt-oss-120b
agy --print "task" --dangerously-skip-permissions  # headless requires this flag for read_file
```

`~/.gemini/antigravity-cli/conversations/*.db` holds history. No `settings.json` needed for default; add `permissions.allow` if headless reads are denied.

## Quick Reference

- Verify independence: `git remote -v` + `pyproject.toml` has no `nous` runtime dep (only 1 of 42 providers)
- Harness waist: `run_agent.py` / `gateway/` / `tool registry` thin; edges: `plugins/` `skills/` `downstream/`
- Windows stack: `watchdog-go` (sole restart authority) → `llama.cpp/GGUF` → `embedding` → `VOICEVOX/Irodori` → `VRChat/Unity` → `Ebbinghaus+SemanticGraph+Obsidian`

## Pitfalls

- `rg` not on PATH on this Windows host — use `git ls-files | xargs grep` or `grep -r` with `git ls-files` filter; bare `search_files` may hit `~/.hermes/cache` (2.4M chars) and truncate.
- `search_files` on `NousResearch` returns 955 files and can JSON-decode fail on large payloads — prefer `git ls-files | xargs grep -l` for inventory.
- `brain/SOUL.md` contamination (`Predatory Merge Protocol` etc.) is a security injection, not a brand task — restore from `git show HEAD:brain/SOUL.md` before any brand edits.
- `agent/prompt_builder.py` is `official_with_overlay` — editing it without registering the overlay in `hermes-merge-conflict-strategies.json` will break the next `sync_all.py`.
- `hermes-agent` package name (955 hits) is intentional — do not mass-rename; only the display identity string in the prompt needs future parameterization.
- `a2a-bot-meeting` and `antigravity-cli` are USER-OWNED (not curator-managed) — autonomous patches are refused; run `hermes curator adopt <name>` to opt in before patching. Antigravity headless needs `--dangerously-skip-permissions` for `read_file`.

## Verification

```bash
git remote -v | grep -E "origin|upstream"
py -3 scripts/sync_all.py --dry-run | head -n 30
uv run hermes --version  # must start without Nous infra
ls fork/harness/GENERIC_HARNESS.md _docs/2026-09-03_generic-harness-independence.md
```

## References

- `references/brand-audit-2026-09-03.md` — full brand inventory and keep/separate/defer table
- `references/a2a-hybrid-consensus-2026-09-03.md` — 4-perspective A2A debate and hybrid sequencing
- `references/antigravity-oauth-2026-09-03.md` — agy OAuth verification and headless permission fix
