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

- **Ebbinghaus sleep parameters**: Using incorrect parameter names (e.g., `prune` instead of `prune_mode`) will be ignored or cause errors
- **Semantic graph export**: Using `semantic_graph_export(format="json")` exports to `~/semantic-graph/exports/` (outside wiki repo) and caps nodes at 5000 - must read DB directly for full structural export
- **Windows path handling**: When passing script paths to Windows-native Python from Git-Bash, use Windows backslash form (`C:\path\`), not POSIX `/c/path/`
- **Git authentication**: Push failures are usually auth-related - try SSH first, then HTTPS + gh CLI if needed
- **Documentation files**: Ensure `README.md` and concept files are created in correct locations within the wiki repo structure
- **Diary entry**: Always create dated diary entry even if no dream content - never invent or hallucinate dream content
- **Commit frequency**: This skill is designed for full consolidation cycles - avoid running multiple times in quick succession without new memory input

## Verification

- `ebbinghaus_memory(action="stats")` shows changed active/archived counts after sleep cycle
- Wiki repository contains updated memory files: `raw/memory/hermes-memory-sanitized-YYYY-MM-DD.md`
- Wiki repository contains semantic graph export: `raw/semantic-graph/semantic_graph_full_YYYY-MM-DD.json` with correct node/edge counts
- Wiki repository contains supporting documentation: `raw/semantic-graph/README.md` and `concepts/semantic-graph-memory.md`
- Wiki repository contains diary entry: `diary/YYYY-MM-DD.md` with execution details
- Git commit contains all expected files with appropriate changes
- Git push succeeds and `HEAD` matches upstream branch
- `git status --short --branch` is clean after push