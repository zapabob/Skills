---
name: hakua-memory-dev
description: Extend hakua-memory Python package for agent memory systems.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
platforms: [linux, macos, windows]
metadata.hermes.tags:
  - Python
  - Memory
  - RAG
  - SQLite
  - Embedding
  - Obsidian
metadata.hermes.related_skills:
  - hermes-agent
  - python-sqlite-script-safety
---

# Hakua Memory Dev Skill

Build, test, and extend the `hakua-memory` Python package — a self-contained composite memory library combining Ebbinghaus forgetting-curve memory, semantic graph, RAG (Retrieval-Augmented Generation), embedding retrieval, and Obsidian export behind one `CompositeMemory` API.

## When to Use

- "Add a new feature to hakua-memory"
- "Fix a bug in the RAG module"
- "Extend the ACL system"
- "Add Obsidian templates"
- "Publish hakua-memory to PyPI"
- "Add tests for hakua-memory"

## Prerequisites

- Python 3.11–3.13 (`py -3` on Windows)
- `uv` or `pip` for dependency management
- The repo lives at `%USERPROFILE%\Documents\New project\hakua-memory`

## How to Run

```bash
cd "%USERPROFILE%/Documents/New project/hakua-memory"
py -3 -m pip install -e ".[dev]"
py -3 scripts/test_comprehensive.py
```

## Quick Reference

| Task | Command |
|------|---------|
| Install (dev) | `py -3 -m pip install -e ".[dev]"` |
| Run all tests | `py -3 scripts/test_comprehensive.py` |
| Build package | `py -3 -m build` |
| Upload to PyPI | `py -3 -m twine upload dist/*` |
| Run single test | `py -3 scripts/test_acl.py` |
| Check lint | `py -3 -m ruff check src` |

## Procedure

### 1. Project Structure

```
hakua-memory/
├── pyproject.toml          # Package metadata + optional deps
├── src/hakua_memory/
│   ├── __init__.py         # Exports CompositeMemory
│   ├── composite.py        # Single entrypoint API
│   ├── config.py           # HakuaMemoryConfig with YAML
│   ├── ebbinghaus/         # Ebbinghaus memory store
│   ├── semantic_graph/     # Semantic graph + embedding
│   │   └── embedding/      # fake, llama-cpp, OpenAI backends
│   ├── rag/                # RAG module
│   │   ├── models.py       # Document, Chunk, Citation, AclEntry, AclCheckResult
│   │   ├── schema.py       # SQLite DDL (FTS5, ACL, chunks, citations)
│   │   ├── store.py        # DocumentStore (versioning, ACL, CJK search)
│   │   ├── chunking.py     # Page/slide/section-aware chunking
│   │   ├── ingestion.py    # PDF/DOCX/PPTX/Markdown ingestion
│   │   ├── retrieval.py    # RAG search + citation rendering
│   │   ├── meeting.py      # Decisions/tasks/action items extraction
│   │   └── contradiction.py# Cross-document contradiction detection
│   └── obsidian/
│       └── templates.py    # ObsidianTemplateRenderer + Mermaid
└── scripts/
    ├── test_comprehensive.py
    ├── test_rag_e2e.py
    ├── test_acl.py
    ├── test_config.py
    ├── test_embedding_backend.py
    └── test_obsidian_templates.py
```

### 2. Core API (`CompositeMemory`)

```python
from pathlib import Path
from hakua_memory import CompositeMemory

cm = CompositeMemory(Path(".memory"))

# Ebbinghaus
cm.remember("fact", tags=["tag"])
cm.recall("query")

# Semantic Graph
cm.add_node({"node_id": "n1", "node_type": "Claim", "label": "...", "status": "asserted"})
cm.search("query")

# RAG
cm.ingest_markdown("# Title\ncontent", title="Doc", author="Alice")
cm.search_documents("query", top_k=5)
cm.grant_access(doc_id, "alice", "read")
cm.check_access(doc_id, "alice")  # → {"can_read": True, ...}
cm.extract_meeting_items(doc_id)
cm.detect_contradictions()

# Stats
cm.stats()  # → {"ebbinghaus": {...}, "semantic_graph": {...}, "rag": {...}}
```

### 3. ACL 3-Level Permissions

```python
from hakua_memory.rag.models import AclEntry, AclCheckResult, ACL_READ, ACL_WRITE, ACL_DELETE

# Grant
cm.grant_access(doc_id, "alice", "read")
cm.grant_access(doc_id, "bob", "write", department="Engineering")

# Check
result = cm.check_access(doc_id, "alice")
# {"can_read": True, "can_write": False, "can_delete": False, "permissions": ["read"]}

# Revoke
cm.revoke_access(doc_id, "alice", "read")

# Department-scoped
cm.check_access_department(doc_id, "Engineering")
```

### 4. Config (`HakuaMemoryConfig`)

```yaml
# ~/.hakua-memory/config.yaml
embedding:
  backend: fake  # fake | llama-cpp | openai
  dimensions: 1024
  model_path: ""  # required for llama-cpp

obsidian:
  vault_path: ~/Obsidian/Hakua
  export_diary: true
  export_forgetting_curve: true

rag:
  chunk_size: 1000
  chunk_overlap: 200
  top_k: 8
  citation_format: markdown
```

### 5. Testing

```bash
# All-in-one comprehensive test (no embedding required)
py -3 scripts/test_comprehensive.py

# Individual module tests
py -3 scripts/test_rag_e2e.py
py -3 scripts/test_acl.py
py -3 scripts/test_config.py
py -3 scripts/test_embedding_backend.py
py -3 scripts/test_obsidian_templates.py
```

### 6. Build & Publish

```bash
# Clean build
rm -rf dist build src/*.egg-info
py -3 -m build

# Verify
py -3 -m pip install dist/hakua_memory-*-py3-none-any.whl --quiet

# Upload (requires ~/.pypirc with API token)
py -3 -m twine upload dist/*
```

### 7. Adding a New Module

1. Create `src/hakua_memory/<module>/__init__.py`
2. Define dataclass models in `models.py`
3. Add SQLite DDL to `schema.py`'s `ALL_DDL` list
4. Create a `store.py` with CRUD methods
5. Export from `__init__.py`
6. Add methods to `CompositeMemory` in `composite.py`
7. Add test in `scripts/test_<module>.py`
8. Run comprehensive test

## Pitfalls

- **Windows file lock**: SQLite connections must be closed before deleting temp dirs. Always call `cm.close()` in test `finally` blocks.
- **FTS + CJK**: SQLite FTS5 doesn't tokenize CJK well. `search_chunks_fts()` falls back to LIKE for multi-term queries.
- **`project.license`**: PyPI deprecated TOML table license. Use `license = {text = "Apache-2.0"}` (not bare string).
- **Hermes dependency**: Don't import from `hermes_constants` or `hermes_logging` in hakua-memory code — keep it independent.
- **Embedding fallback**: All search must work WITHOUT an embedding backend. Use `DeterministicFakeEmbeddingConfig` for tests.
- **`pyproject.toml` commas**: No trailing comma in `dependencies` array — causes PEP 508 validation error on build.

## Verification

```bash
py -3 scripts/test_comprehensive.py && echo "ALL TESTS PASSED"
```
