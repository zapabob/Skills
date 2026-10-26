---
name: memory-recall-guide
description: "Build and use the 3-layer memory pipeline."
version: 0.2.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Memory, Recall, Ebbinghaus, Semantic Graph, Obsidian]
    category: memory
---

# Memory Pipeline & Recall Guide

End-to-end memory lifecycle for Hermes on Windows: run Ebbinghaus sleep, export to Obsidian Wiki with git push, project into a Semantic Graph with BGE-M3 embeddings, automate differential sync via cron, and recall memories during conversation. Uses stdlib + `sqlite3` + `urllib` only; no extra pip packages.

## When to Use

- 「記憶の統合と睡眠して」「Obsidianへプッシュして」「グラフ同期して」
- Setting up the nightly memory pipeline (sleep → export → graph sync).
- Need to recall past context mid-conversation and `ebbinghaus_memory` alone isn't enough.
- Debugging why a memory isn't in the graph or search results.

## Prerequisites

- Ebbinghaus DB: `~/.hermes/ebbinghaus_memory.db`
- Semantic Graph DB: `~/.hermes/semantic-graph/semantic_graph.db`
- Obsidian Wiki: `%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki` (remote: `zapabob/hermes-obsidian-vault`, branch `main`)
- llama.cpp embedding server: `http://127.0.0.1:8082/v1/embeddings` (model `nsfw-bge-m3-v5-q6_k`, dim 1024)
- Hermes repo root: `%USERPROFILE%\Documents\New project\hermes-agent`
- Sync scripts in `~/.hermes/scripts/`: `sync-ebbinghaus-graph.py`, `recall_semantic_graph.py`, `memory_digest.py`

## How to Run

### Nightly pipeline (manual or cron)

1. Invoke `ebbinghaus_memory` with `action="sleep"`, `prune_mode="archive"`.
2. Invoke through `terminal`: `py -3 sync_memory.py --max-sessions 80 --max-x-events 80 --no-sleep` (from hermes-agent root).
3. Invoke through `terminal`: `py -3 ~/.hermes/scripts/sync-ebbinghaus-graph.py` (differential graph sync + embedding backfill).
4. Invoke through `terminal` from the Wiki dir: `git add -A && git commit -m "chore(memory): ..." && git push origin main`.

### Recall during conversation

1. `ebbinghaus_memory(action="recall", query="...", min_score=0.3)` — instant, salience-based.
2. If insufficient, invoke through `terminal`: `py -3 ~/.hermes/scripts/recall_semantic_graph.py "query" --top 5 --mode hybrid`.
3. For long-term knowledge, invoke `search_files` on the Wiki `concepts/` or `diary/` dirs.

## Quick Reference

| Action | Command |
|---|---|
| Sleep | `ebbinghaus_memory(action="sleep", prune_mode="archive")` |
| Wiki export | `py -3 sync_memory.py --no-sleep` (from hermes-agent root) |
| Graph sync | `py -3 ~/.hermes/scripts/sync-ebbinghaus-graph.py` |
| Wiki push | `git add -A && git commit -m "..." && git push origin main` |
| Hybrid search | `py -3 ~/.hermes/scripts/recall_semantic_graph.py "q" --top 5` |
| Daily digest | `py -3 ~/.hermes/scripts/memory_digest.py --days 1` |
| Cron create | `cronjob(action="create", schedule="0 5 * * *", script="sync-ebbinghaus-graph.py", no_agent=True)` |

## Procedure

### 1. Ebbinghaus Sleep

```
ebbinghaus_memory(action="sleep", prune_mode="archive",
  rehearse_threshold=0.6, forget_threshold=0.1, salience_keep_threshold=0.8)
```

Typical result: ~1000 reviewed, ~11 rehearsed, ~1 archived, ~2568 active.

### 2. Obsidian Wiki Export

Invoke through `terminal` from `%USERPROFILE%\Documents\New project\hermes-agent`:

```bash
py -3 sync_memory.py --max-sessions 80 --max-x-events 80 --no-sleep
```

Output goes to `%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki` (NOT the legacy `llm-wiki` path). Confirm via stdout `wiki_root` field.

### 3. Create Daily Diary

Use `write_file` to write `diary/YYYY-MM-DD.md` in the Wiki dir with: highlights, sleep stats, graph stats, embedding stats, what was done, what to follow up.

### 4. Semantic Graph Differential Sync

Invoke through `terminal`:

```bash
py -3 %USERPROFILE%/.hermes/scripts/sync-ebbinghaus-graph.py
```

The script:
- Queries `state='active'` memories from Ebbinghaus DB.
- Skips IDs already in `memory_node_links` table (differential).
- Inserts node + link + state_cache rows into Graph DB.
- Generates BGE-M3 embeddings for new nodes via llama.cpp.
- Typical: 0 new on re-run (idempotent), 2568 active total.

### 5. Commit & Push Wiki

Invoke through `terminal` from `%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki`:

```bash
git add -A
git diff --cached --check
git commit -m "chore(memory): Ebbinghaus sleep + session-memory export $(date +%F)"
git push origin main
```

Verify with `git status --branch --short` (expect `## main...origin/main` clean).

### 6. Automate via Cron

Create a `no_agent` cron job so it runs without token cost:

```
cronjob(action="create",
  name="Semantic Graph diff sync",
  schedule="0 5 * * *",
  script="sync-ebbinghaus-graph.py",
  no_agent=True,
  deliver="local")
```

Script must be in `~/.hermes/scripts/` and referenced by filename only (not absolute path).

### 7. Create Search Script

Write `~/.hermes/scripts/recall_semantic_graph.py` with three modes:
- `--mode embedding`: cosine similarity over BGE-M3 vectors (3-5s)
- `--mode fts`: SQLite FTS5 keyword search (instant)
- `--mode hybrid` (default): Reciprocal Rank Fusion of both

### 8. Recall During Conversation

Decision tree:

| Query type | First choice | Fallback |
|---|---|---|
| User preferences | `ebbinghaus_memory(action="recall")` | `search_files` on Wiki `concepts/` |
| Past events | `recall_semantic_graph.py --mode hybrid` | Wiki `diary/` |
| Technical memory | `recall_semantic_graph.py --mode hybrid` | Wiki `concepts/` |
| Recent (24h) | `ebbinghaus_memory` (salience=high) | `memory_digest.py --days 1` |
| Long-term knowledge | `search_files` on Wiki | — |

Rules: summarize results (don't paste long text); if 0 hits, don't guess — try next method.

## Pitfalls

- **Embedding search takes 4-5s.** For instant recall, use `ebbinghaus_memory(action="recall")` first.
- **Graph DB updates only at 05:00.** Fresh memories from today won't be in the graph yet.
- **Obsidian app locks files.** If `git commit` fails, close Obsidian or do local-only commit.
- **llama.cpp must be running** for embedding generation. If down, new nodes get no vectors.
- **~31 nodes typically fail embedding** (orphaned/too short). Normal, not a blocker.
- **Wiki push target is `ObsidianVault` repo** on branch `main`, NOT the legacy `New project/llm-wiki` path.
- **`sync_memory.py` needs the hermes-agent venv** — use `py -3` from the repo root, not bare `python`.
- **Cron script paths must be relative** — use just the filename, not an absolute path.

## Verification

```bash
py -3 -c "
import sqlite3
c = sqlite3.connect('%USERPROFILE%/.hermes/semantic-graph/semantic_graph.db')
print('Nodes:', c.execute('SELECT COUNT(*) FROM nodes').fetchone()[0])
print('Embeddings:', c.execute('SELECT COUNT(*) FROM node_embeddings').fetchone()[0])
print('Links:', c.execute('SELECT COUNT(*) FROM memory_node_links').fetchone()[0])
"
```

Expect: Nodes ~3800+, Embeddings ~3800+, Links ~2600+.
