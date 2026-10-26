---
name: ebbinghaus-contradiction-scan
description: Scan Ebbinghaus memory for contradictions and drift.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Memory, Ebbinghaus, Contradiction, DataIntegrity, RAG]
    related_skills: [memory-composite-system, memory-maintenance, memory-sleep-diary]
---

# Ebbinghaus Contradiction Scan

Read-only integrity scan of `~/.hermes/ebbinghaus_memory.db`: contradiction
chains, supersede-graph resolution, mojibake/foreign-script leaks, and duplicate
drift.

## When to Use

- A cron job reports "contradiction detection" and you need it to actually work.
- Auditing whether corrections (`supersedes` / `corrected_by`) resolve properly.
- Chasing the recurring "初版に文字化けが混入" mojibake-correction chains.
- Checking duplicate inflation before a sleep cycle.

## The Trap (why the naive script fails)

`hakua_memory.rag.contradiction.detect_contradictions` does **not** scan
Ebbinghaus memories. It takes a RAG `DocumentStore`, and the live RAG DB at
`~/.hermes/ebbinghaus_memory/rag.db` holds **0 documents and 0 chunks** — so any
call returns `[]` no matter what you feed it. To use it on memory text you must
project memories into a temporary `DocumentStore` yourself.

Additional failure modes hit on the way:

- `CompositeMemory` has no `ebbbinghaus` attribute. It is `ebbinghaus`.
- `Contradiction` exposes `contradiction_id` / `document_a_title` /
  `document_b_title` / `quote_a` / `quote_b` — **not** `has_contradiction`
  or `sources`.
- `document_ids` must be RAG document IDs, not memory IDs.
- `store.insert_chunks` fails with `sqlite3.IntegrityError: FOREIGN KEY
  constraint failed` unless the parent documents are inserted first.
- Always `store.close()` before the temp dir is cleaned up, or Windows raises
  `PermissionError: [WinError 32]` on `rag.db`.
- `HERMES_HOME` may point at a sibling profile (e.g. `profiles/job-recruiter`,
  0 memories). Verify the DB actually holds the data before trusting it.
- `NEGATION_PATTERNS` matches `ない|ません|しません`, which is nearly universal
  in Japanese. Raw hit counts are noise; always triage.

## How to Run

```bash
python tools/contradiction_scan.py --limit 4981     # full active set, ~55s
python tools/contradiction_scan.py --limit 200      # quick pass
python tools/contradiction_scan.py --no-stage-b     # authoritative state only
```

Supporting probes (all read-only):

```bash
python tools/scan_chains_detail.py    # full text of every supersede pair
python tools/scan_chain_tips.py       # walk chains to tip; verify tip is active
python tools/scan_neardupe.py         # >=0.8 containment near-duplicate pairs
python tools/scan_final_verify.py     # spurious-edge + mojibake-integrity check
```

## Procedure

1. Open the DB **read-only**: `sqlite3.connect("file:" + path.as_posix() + "?mode=ro", uri=True)`.
   Never scan through `CompositeMemory` — it creates `semantic.db` / `rag.db`
   side files in the memory dir.
2. **Stage A (authoritative).** Read `memory_relations` (`supersedes` +
   `corrected_by`) joined to `memories`, plus `belief_status='superseded'` rows.
   This is the contradiction state the store already tracks — no heuristics.
3. **Chain resolution.** `supersedes_memory_id` points *backwards* to the older
   memory, so build `newer_of = {older: newer}` and walk to the tip. Verify the
   tip is `state='active'` / `belief_status='current'`. Note that
   `memory_relations` stores **both** directions, so rows double if you do not
   dedupe on `(source, target)`.
4. **Stage B (heuristic).** Project the top-N active memories by salience into a
   temp `DocumentStore` (insert documents → then chunks), run
   `detect_contradictions(store, min_confidence=0.6)`, then triage each hit.
5. **Triage rule.** Keep a hit only if the two quotes share a Latin entity token
   *and* differ on a *strict* negation (`ではない/ではありません/禁止/不可/
   cannot/prohibited`) — or share a numeric-with-unit token *and* differ on
   strict negation. Everything else is `ない/ません` regex noise.
6. **Leak audit.** Scan active memories for Cyrillic / Arabic / Hangul
   (`[\u0400-\u04FF\u0600-\u06FF\u0700-\u074F\uac00-\ud7af]`). Japanese and Latin
   are legitimate; those three are not.

## Pitfalls

- Do not treat a supersede `reason` string as self-validating. Check that the
  reason actually describes *both* endpoints. The `114609 -> 2` edge claims a
  "repeated identical zero-result run" but its endpoints are an unrelated
  `lm_twitterer` log and a user preference about forgetting curves.
- Chains interleave and share nodes (`114616 -> 114617 -> 114698 -> 114699 ->
  114700`). Deduping by pair alone leaves 7 edges for 4 logical chains.
- Mojibake fixes create long chains where only the *tip* is active. The tip is
  the version to trust; the archived intermediates are the corrupted originals.
- A retracted claim can legitimately remain inside an active memory's *quoted
  history* ("当初「X」と診断したが、…と確定した"). Only flag it if the active
  memory still asserts it without the retraction.

## Verification

- `chains_count` matches the number of distinct logical chains after walking to
  tips, and every tip reports `active/current`.
- `orphan_superseded_count == 0` (no `superseded` rows without a relation edge).
- `raw_hit_count` is small relative to `candidates_scanned`, and every hit in
  `plausible` survives a manual read of both quotes.
- Baseline for the default profile: 4981 active / 1144 archived, 7
  `supersedes` + 7 `corrected_by`, exact duplicates ~0.02%, ~23 near-duplicate
  pairs per 1500 sampled.

## Baseline (2026-10-03, default profile)

| Metric | Value |
| --- | --- |
| Active / archived | 4981 / 1144 |
| Logical chains | 4 (tip `59923`, `114609`, `114697`, `114700`) |
| Orphan superseded | 0 |
| Stage B raw hits (4981 scanned) | 41 (negation 37, direct_contrast 3, date_mismatch 1) |
| Stage B plausible | 7 |
| Exact duplicates | 1 group (2 rows) |
| Foreign-script leaks in active | 1 (`memory-114484`, Hangul `중`) |
