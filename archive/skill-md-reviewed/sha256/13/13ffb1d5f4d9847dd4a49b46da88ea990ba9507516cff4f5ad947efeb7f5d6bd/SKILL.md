---
name: parallel-subagent-code-integration
description: "Reconcile, verify, and fix interdependent code produced by multiple parallel subagents working on a shared package. Covers tree inventory, import cross-checks, end-to-end validation harnesses, and the recurring SQLAlchemy 2.0 / Pydantic / Python binding breakages that appear when sibling agents each write part of a package."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, parallel, integration, debugging, validation]
    related_skills: [subagent-driven-development, systematic-debugging, code-review]
---

# Parallel Subagent Code Integration

## Overview

When two or more subagents implement **different parts of the same new package
in parallel** (e.g. one writes `models/`, another writes `api/` routers, a third
writes `config.py`/`database.py`), each file can be individually "correct" yet
the package as a whole fails to import or run. The breakage lives *between* the
files, not within them. This skill is the integration/reconciliation playbook for
that exact situation, and it doubles as a fast-debugging reference for the
framework-specific breakages that show up most often.

## When to Use

- You dispatched parallel subagents on one package and must combine their output.
- The package imports fail, or a router 404s / 500s, even though each agent
  reported success.
- You see cross-file errors like `ImportError`, `InvalidRequestError`,
  `OperationalError: ... already exists`, or Pydantic "Field required".
- Load this alongside `subagent-driven-development` when its two-stage review
  reports integration issues between tasks.

## The Reconciliation Playbook

1. **Inventory the whole tree before trusting anything.** `find`/`search_files`
   the target directory and `read_file` every file — including ones you didn't
   write. A sibling may have created the module your code imports
   (e.g. `api/__init__.py`, a missing `SessionUpdate` schema). Do not assume
   your own files are the only ones present. Parallel runs routinely produce
   files in every subdirectory unexpectedly.
2. **Read imports, not filenames.** For every symbol your code imports, confirm
   it exists with the expected name and type in the sibling's module. Cross-
   subagent runs produce: undefined symbols, type mismatches (a schema field
   typed `dict` vs a model column expecting `str`), and missing reciprocal ORM
   relationships.
3. **Treat the write tool's "modified by sibling subagent" warning as a guard,
   not a conflict.** It fires on parallel runs even when nothing clobbered you.
   After writing into a shared tree, **re-read the file** to confirm your
   canonical content landed — a lagging sibling or stale in-memory buffer can
   differ from what you think you wrote.
4. **Build one end-to-end validation harness and actually run it.** Importing
   the top-level package and issuing a real request (or constructing a real ORM
   object) catches cross-file breakage that per-task lint/compile misses. Pattern:
   - Create a throwaway venv with `uv venv --python <ver> .tmp-venv` then
     `uv pip install --python .tmp-venv/Scripts/python.exe <deps>` so you don't
     contaminate the project's real environments.
   - Point the DB at a temp file (`tempfile.mkstemp(suffix=".db")`) or in-memory
     SQLite; set the settings URL before `init_db()`; delete the file after.
   - Drive the app via `httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
     base_url="http://t")`. Exercise create→read→update→delete + a 404 path per
     resource. Then assert real row counts via a direct session.
   - Delete the harness script and the venv afterward.
5. **Fix the package, don't weaken the test.** If validation fails, find the
   root cause (see `references/parallel-subagent-integration-pitfalls.md`) and
   patch the real defect — usually in a sibling's file. Never edit your assertion
   to make a broken package "pass."

## Why this class exists separately

The sibling skill `subagent-driven-development` governs *dispatching* and
*two-stage review*. It does not cover the controller-side **integration/verification
of parallel outputs** in a shared tree, nor the framework-specific breakage
catalog. That gap is filled here.

## Further reading

- `references/parallel-subagent-integration-pitfalls.md` — The concrete,
  copy-paste-able failure modes (SQLAlchemy 2.0 relationship/index/circular-import
  traps, Pydantic path-vs-body field handling, and the Python `from module import
  singleton` staleness trap) with the exact fixes that worked.
