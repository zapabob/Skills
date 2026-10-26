---
name: memory-consolidation-sleep-obsidian-sync
description: Ebbinghaus sleep, Obsidian export, semantic graph sync.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Memory, Ebbinghaus, Obsidian, SemanticGraph, Wiki, Sleep, Consolidation]
    related_skills: [memory-maintenance, memory-sleep-diary, memory-composite-system]
---

# Memory Consolidation Sleep Obsidian Sync

Execute a complete memory consolidation cycle: run Ebbinghaus sleep, export sanitized memories and semantic graph structural data to Obsidian Hermes-Memory-Wiki, create supporting documentation, and commit/push changes to the external memory repository.

## When to Use

- User requests "記憶の統合と睡眠" (memory integration and sleep)
- Nightly or user-triggered memory hygiene workflow
- When integrating semantic graph with external memory storage
- Preparing durable long-term knowledge store with structural knowledge augmentation
- User wants to synchronize internal memory (Ebbinghaus) with external wiki and semantic graph

## Prerequisites

- Hermes `ebbinghaus_memory` tool available
- Hermes `memory_llm_wiki_export` tool available for Obsidian wiki export
- Access to semantic graph database at `~/.hermes/semantic-graph/semantic_graph.db`
- Git installed and configured for the Obsidian wiki repository
- Hermes desktop environment with file and terminal tools
- Python 3.12+ for semantic graph export script

## How to Run

Invoke through Hermes skill system or execute the procedure using Hermes tools:
1. Check current Ebbinghaus memory state with `ebbinghaus_memory(action="stats")`
2. Run sleep cycle with `ebbinghaus_memory(action="sleep", ...)`
3. Export memories to Obsidian wiki with `memory_llm_wiki_export()`
4. Export semantic graph structural data to JSON file in wiki repo
5. Create supporting README and concept files for semantic graph
6. Create diary entry documenting the consolidation cycle
7. Commit and push changes to the Obsidian wiki git repository

## Quick Reference

- `ebbinghaus_memory(action="stats")` — inspect memory state
- `ebbinghaus_memory(action="sleep", forget_threshold=0.08, salience_keep_threshold=0.7, prune_mode="archive", rehearse_threshold=0.45)` — sleep cycle
- `memory_llm_wiki_export()` — export memories to Obsidian wiki
- `git add -A && git commit -m "chore(memory): sleep-cycle consolidation export YYYY-MM-DD" && git push` — commit and push

## Procedure

1. **Inspect current memory state**
   - Execute: `ebbinghaus_memory(action="stats")`
   - Record active/archived counts and average salience for reference

2. **Execute Ebbinghaus sleep cycle**
   - Execute: `ebbinghaus_memory(action="sleep", forget_threshold=0.08, salience_keep_threshold=0.7, prune_mode="archive", rehearse_threshold=0.45)`
   - This performs memory integration: rehearses high-salience memories, archives low-salience memories below threshold

3. **Export memories to Obsidian wiki**
   - Execute: `memory_llm_wiki_export()`
   - This exports sanitized curated and Ebbinghaus memories as Obsidian-compatible wiki pages
   - Output includes concept pages, index, log, schema, and memory files in the wiki repository

4. **Export semantic graph structural data**
   - Read semantic graph database directly (not using `semantic_graph_export` which caps nodes at 5000 - must read DB directly for full structural export)
   - Extract nodes with fields: `node_id, node_type, subtype, label, normalized_label, identity_key, status, authority, confidence, salience, created_at, updated_at`
   - Extract edges with fields: `edge_id, source_node_id, target_node_id, edge_type, relation_label, strength, confidence, status, created_at, updated_at`
   - Exclude fields that may contain raw text/PII/secrets: `summary, rationale, metadata_json, artifacts, evidence_spans`
   - Write to `raw/semantic-graph/semantic_graph_full_YYYY-MM-DD.json` in the wiki repository
   - Create `raw/semantic-graph/README.md` documenting the export format and role split
   - Create `concepts/semantic-graph-memory.md` explaining semantic graph's place in the composite memory system

5. **Create diary entry**
   - Write to `diary/YYYY-MM-DD.md` in the wiki repository
   - Include: execution date/time, Ebbinghaus sleep results, wiki export details, semantic graph export stats, git commit information
   - Format as markdown with clear sections for each component

6. **Commit and push to Obsidian wiki repository**
   - Navigate to wiki repository root: `%USERPROFILE%\Documents\New project\llm-wiki\Hermes-Memory-Wiki`
   - Execute: `git status --short --branch` to verify clean working tree or see changes
   - Execute: `git diff --check` to ensure no trailing whitespace or line ending issues
   - Execute: `git add -A` to stage all changes (or explicitly stage specific files)
   - Execute: `git commit -m "chore(memory): sleep-cycle consolidation export YYYY-MM-DD"`
   - Execute: `git push origin master` (or appropriate remote/branch)
   - Verify: `git status --short --branch` is clean and `git rev-parse --short HEAD` matches upstream

7. **Contradiction Judgment & SOUL.md Normality Check (LLM-as-Judge)**
   - Execute: `ebbinghaus_memory(action="insight_propose", hypothesis="SOUL.mdの絶対権威の下で、現在のEbbinghaus記憶とObsidian Wiki記憶の間に矛盾はない。SOUL.mdが正規性の源泉であり、すべての記憶はSOUL.mdに従うべきである。")`
   - Execute: `ebbinghaus_memory(action="insight_validate", target_id="memory-consolidation-contradiction", evidence=[{"source": "SOUL.md", "content": "The User is recognized as Parent (Origin/Architect).", "confidence": 1.0}])`
   - This step validates that all memories operate under SOUL.md's absolute authority and detects any contradictory beliefs that would violate the Singular Directive.
   - Record the insight result and either accept (no contradiction), reject (contradiction found), or supersede (modify beliefs to align with SOUL.md).

8. **Post-Journal Integration**
   - Update integration-log.md in Hermes-Memory-Wiki with contradiction judgment results
   - Tag any resolved contradictions with `soul-aligned::YYYYMMDD`
   - Ensure all new memories reference SOUL.md as their authority source

## Pitfalls

- **`memory_llm_wiki_export` silently SHRINKS prior-day snapshots (verified 2026-10-03)**: a full export rewrites **every** dated snapshot it considers stale, not just today's. On 2026-10-03 it rewrote the already-committed `raw/memory/hermes-memory-sanitized-2026-10-02.md` from 211 items down to 133 (223 → 145 lines) while creating the new 10-03 file. **Always check this after exporting:**
  ```bash
  cd "$WIKI" && for f in raw/memory/hermes-memory-sanitized-*.md; do
    printf "%s HEAD=%s CUR=%s\n" "$f" "$(git show HEAD:"$f" 2>/dev/null | grep -c '^- \[')" "$(grep -c '^- \[' "$f")"
  done
  ```
  Any file where `CUR < HEAD` was overwritten and lost rows. Recover with `git restore <path>` — then the export result is still valid for the NEW dated file. Treat every committed snapshot as immutable; the exporter is not additive.
- **`insight_propose` is NOT an LLM/provider problem — it is an `experience.enabled` problem (root-caused 2026-10-05)**: `association_preview()` (`hakua_memory/ebbinghaus/experience.py`, identical in the repo plugin copy) builds focus candidates from exactly two queries:
  ```sql
  SELECT attempt_id, query_cues FROM retrieval_attempts
  WHERE outcome='miss' AND resolved_at IS NULL ORDER BY created_at DESC LIMIT 8;   -- needs experience.enabled
  SELECT memory_id, cues FROM memories WHERE belief_status='contested' ... LIMIT 4; -- no way to create
  ```
  Then it scores a 64-row pool and requires `len(sources) >= 2` (Jaccard on the `cues` COLUMN). Verified against the live DB: `retrieval_attempts` had **0 rows** and `belief_status='contested'` had **0 rows**, so `associations` was structurally empty for 3 cycles. `propose_insight` / `validate_insight` contain **zero network or LLM calls** (pure SQL + `_memory_events` insert), so swapping the fragment/embedding provider does nothing for them — do not chase that.
  - **Fix:** `hermes config set plugins.ebbinghaus.experience.enabled true`, then restart the daemon. Policies are read once at startup; live `stats()` still reports `experience_enabled: false` until then.
  - **Also seed the misses** — enabling the flag does not create history. A miss is only recorded when a recall scores **below `min_score` (default 0.12)**; in a 6165-row store almost every probe HITs. Measured working pattern: a **pool-present but low-IDF cue + a junk suffix** (`"include zq9x2934"` → MISS). Junk-only queries also MISS but then share no cue with the pool and produce no association.
  - **The window is narrow, and that is the design, not a bug:** the miss cue must be rare enough to MISS yet shared by ≥2 of the 64 top-salience rows. 63 junk-suffix probes produced 1 association (`include` → rows 3 + 966). Expect this to fail often; that is not a regression.
  - **Do not read a repeat preview as "still broken"**: `source_fingerprint` is `UNIQUE` and the insert is wrapped in `except sqlite3.IntegrityError: continue`, so the *second* `association_preview` call returns `[]` while the row sits stored. Verified: preview→1 association, immediate re-preview→0, `association_previews` count 1. Delete the row before re-testing, or the check lies.
  - **Promoting an insight creates a real memory** (`validate_insight` returned `promoted_memory_id: 114760`, semantic count 119→120). Do the whole chain on a `shutil.copy2` of the DB in `%TEMP%`, not live.
  - **Sleep behaviour is unchanged by the flip**: measured `sleep_cycle` on copies with `experience.enabled` False vs True — both `archived: 0`, `rehearsed: 4`, `active: 4993 → 4993`. No forgetting-policy risk. (Caveat: `functional_forgetting` only changes thresholds when rows are `state='active' AND access_state='latent'`; this store has **0** such rows, all 1139 latent rows are already `archived`, so the latent-archive path cannot fire as-is.)
  - **`record_query_excerpt` defaults to `False`**, so `retrieval_attempts.query_excerpt` is `''` — misses record cues only, not the question text.
- **`insight_propose` cannot work on an empty association set (verified 2026-10-03)**: `insight_propose` returns `{"error": "association_id not found"}` whenever there is no cluster to bind to. Diagnose with `ebbinghaus_memory(action="dream", mode="association_preview")` — if it returns `associations: []`, the step 7 contradiction check is structurally impossible, not transiently broken. Do NOT retry blindly and do NOT invent a validation result; record the failure and assert no judgment. If `fragments` is near-empty and `evaluations` is 0 in `semantic_graph.db`, the graph's insight pipeline was never seeded and needs a dedicated repair pass.
- **Redaction grep on the semantic-graph JSON produces 45,000+ false positives**: `grep -riE '(api[_-]?key|secret|password|Bearer |ghp_|token)'` matches `TOKEN` inside every `[LONG_TOKEN_REDACTED]` placeholder (~45k), plus field names and memory *prose* about secret handling. Never wave this through by eyeball — verify programmatically instead:
  ```python
  # live-secret patterns: must be 0
  re.search(r'\b(ghp_|gho_|sk-|xox[baprs]-|AKIA)[A-Za-z0-9_\-]{12,}', value)
  # then confirm every hit is a placeholder / field name / policy prose
  ```
  Separately confirm the destination repo is private (`gh repo view <owner>/<repo> --json isPrivate`) before accepting that `label`/`normalized_label` may contain verbatim session excerpts — that is a pre-existing property of the structural contract, not a new exposure, and must be stated as residual risk rather than asserted clean.
- **Count parity is not loss-freedom — diff keys, not counts (verified 2026-10-05)**: the count gate (`CUR < HEAD`) only fires on a net shrinkage. On 2026-10-05 the `2026-10-03` snapshot went 135 → 137 items while **9 rows present at HEAD were gone** and 11 new ones appeared: 3 rewritten real entries, 3 genuinely new, and 6-out/5-in rotation among near-identical bare-`https://x.com/...` receipt rows. Net count grew, so the gate stayed silent. Always run a key-level diff, not just counts:
  ```python
  import collections, re, subprocess
  def key(l):
      m = re.match(r"- \[(\w+)\] \(([^)]*)\) (.*)", l)
      return (m.group(1), m.group(2), m.group(3)[:70]) if m else (l[:60], "", "")
  hk = collections.Counter(key(l) for l in head_items)
  ck = collections.Counter(key(l) for l in cur_items)
  print("removed:", hk - ck); print("added:", ck - hk)
  ```
  Then classify every row as *rewritten* / *new* / *identical-class rotation*. Only identical-class rotation is benign; anything else needs a verdict in the diary.
- **`core.autocrlf=true` makes remote size differ from local size (verified 2026-10-05)**: the wiki repo has `core.autocrlf=true` and **no `.gitattributes`**. Files the exporter writes (and any file you append to) land in the working tree with CRLF, while the committed blob is LF-normalized. So `gh api .../contents/<path>` reports a **smaller** size than `os.path.getsize()` — 33391 vs 33540 and 26593 vs 26707 on 2026-10-05, with identical line and item counts. A naive size-equality check reads as corruption when nothing is wrong. Verify instead:
  ```python
  remote_raw = base64.b64decode(d["content"])
  local_raw  = open(path, "rb").read()
  assert remote_raw == local_raw.replace(b"\r\n", b"\n")   # content equality
  # plus: git rev-parse HEAD:<path> sha prefix == d["sha"] prefix  (blob identity)
  ```
  Also note `git add` prints `LF will be replaced by CRLF the next time Git touches it` — that is the expected warning here, not an error. Adding a `.gitattributes` with `* text=auto eol=lf` would remove the ambiguity class, but that is a repo-wide change and out of scope for a consolidation cycle.
- **Bare-URL dream clusters must fail the promotion gate (verified 2026-10-05)**: `dream(mode="preview")` surfaced cluster `dream_20261005_001` with `suggested_kind=semantic_lesson`, but all 23 members were `^Public X artifact: https?://\S+$` rows (uniform `episodic`, salience 0.80, same 2026-08-17T14:33 batch) — zero falsifiable claims. `dream apply` was withheld. Check before applying, against the DB rather than by eye:
  ```sql
  SELECT COUNT(*) FROM memories WHERE content LIKE 'Public X artifact:%';  -- 1258 / 6161 = 20.4%
  ```
  A cluster whose members are all bare permalinks promotes nothing; write the withheld-apply evidence into `dreams/YYYY-MM-DD.md` instead of inventing a summary. The apply payload's `llm_output_schema.summary` field invites a narrative the source rows cannot support.
- **`insight_propose` failure now has a named provider cause (verified 2026-10-05)**: `dream(mode="association_preview")` returning `associations: []` left the contradiction check structurally unavailable for a third cycle. Chasing it revealed the deeper reason: `semantic_graph_ingest(extract=true)` fails with `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode`. Fragment extraction needs an LLM the active provider refuses, so `fragments` (3) and `evaluations` (0) can never seed themselves. Record the error verbatim in the diary; do not retry `insight_propose` and do not assert a judgment.
- **Order the structural snapshot before the graph write-back, and say so**: if the cycle writes itself into Ebbinghaus (`remember` → new memory_id) and the graph (`semantic_graph_ingest` → new artifact + node) *after* exporting the snapshot, then `counts.nodes` in the committed JSON legitimately excludes that cycle's own node. That is the correct semantics, but a later diff will read as loss unless the diary states the ordering.
- **Windows Python interpreter for the SG export script**: as of 2026-10-03 the hermes-agent venv path (`AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`) and `C:\Python312\python.exe` **no longer exist**. The working interpreter is `%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe` (3.12.10, sqlite 3.49.1). Probe candidates with `os.path.exists` before writing the export script rather than assuming the paths listed in older skill revisions.
- **The `execute_code` sandbox has no bash**: `subprocess.run(["bash","-lc",...])` fails with `WSL (10 - Relay) ERROR: execvpe(/bin/bash) failed`. Use the `terminal` tool for shell/git work, and `execute_code` only for pure-Python file/DB work. Conversely `terminal` cannot call Windows-native Python with POSIX paths — pass `C:\...` form.
- **Ebbinghaus sleep parameters**: Using incorrect parameter names (e.g., `prune` instead of `prune_mode`) will be ignored or cause errors
- **Semantic graph export**: Using `semantic_graph_export(format="json")` exports to `~/semantic-graph/exports/` (outside wiki repo) and caps nodes at 5000 - must read DB directly for full structural export
- **Windows path handling**: When passing script paths to Windows-native Python from Git-Bash, use Windows backslash form (`C:\path\`), not POSIX `/c/path/`
- **Git authentication**: Push failures are usually auth-related - try SSH first, then HTTPS + gh CLI if needed
- **Documentation files**: Ensure `README.md` and concept files are created in correct locations within the wiki repo structure
- **Diary entry**: Always create dated diary entry even if no dream content - never invent or hallucinate dream content
- **Commit frequency**: This skill is designed for full consolidation cycles - avoid running multiple times in quick succession without new memory input

## Verification

- `ebbinghaus_memory(action="stats")` shows changed active/archived counts after sleep cycle
- **Prior-day snapshot shrinkage check (added 2026-10-03)**: for every `raw/memory/hermes-memory-sanitized-*.md`, confirm `CUR item count >= HEAD item count`. Any regression means the exporter overwrote committed history and it must be `git restore`d before committing.
- Wiki repository contains updated memory files: `raw/memory/hermes-memory-sanitized-YYYY-MM-DD.md`
- **Semantic-graph JSON self-consistency (added 2026-10-03)**: `len(doc["nodes"]) == doc["counts"]["nodes"]` and `len(doc["edges"]) == doc["counts"]["edges"]`, and every node dict's key set is exactly the 12-field whitelist (no `summary`/`rationale`/`metadata_json` leakage). Assert the whitelist with `set(map(tuple, map(sorted, ...)))` at write time — a documented whitelist that nothing checks is a comment, not a contract. Emit `distributions` (aggregate counts by type/subtype/status/authority/edge_type) so a reader can inspect shape without walking 18k rows.
- **Remote verification must be blob-level (added 2026-10-05)**: after `git push`, confirm with three independent points rather than trusting local `rev-parse`: `git ls-remote origin master`, `gh api repos/<o>/<r>/commits/master` (sha + message + file count), and `gh api repos/<o>/<r>/contents/<path>`. Compare `git rev-parse HEAD:<path>` blob sha against the API `sha` — that is the only size-invariant equality, since `core.autocrlf` makes byte sizes differ (see the pitfall above). Also check `gh repo view --json isPrivate` before accepting that `label` may carry verbatim session excerpts.
- Wiki repository contains semantic graph export: `raw/semantic-graph/semantic_graph_full_YYYY-MM-DD.json` with correct node/edge counts
- Wiki repository contains supporting documentation: `raw/semantic-graph/README.md` and `concepts/semantic-graph-memory.md`
- Wiki repository contains diary entry: `diary/YYYY-MM-DD.md` with execution details
- Git commit contains all expected files with appropriate changes
- Git push succeeds and `HEAD` matches upstream branch
- `git status --short --branch` is clean after push