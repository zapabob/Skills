---
name: provenance-aware-retrieval
description: Use when adding dense retrieval to RAG or graph systems.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [rag, retrieval, embeddings, provenance, semantic-graph]
    related_skills: [systematic-debugging, software-development/test-driven-development]
---

# Provenance-Aware Retrieval

## When to Use

Use this skill when adding or evaluating dense embeddings, hybrid lexical+dense retrieval, provenance-aware graph expansion, local embedding HTTP adapters, or retrieval safety gates in a RAG or memory system.

Use this class-level skill when extending lexical RAG, memory stores, or semantic graphs with dense embeddings. Preserve the existing lexical path and treat dense retrieval as optional recall augmentation, never as a truth or trust mechanism.

## Invariants

- Embedding similarity is a candidate generator only. It must never promote `accepted`, merge nodes, confirm `same_as`, supersede nodes, change authority or confidence, overwrite confirmed memory, or rewrite answers.
- Typed graph relations, evidence, status, authority, scope, and user confirmation remain the source of truth.
- Canonical embedding text contains only `node_type`, `subtype`, `label`, `summary`, and `identity_key`. Exclude status, authority, confidence, salience, run/session identifiers, timestamps, metadata, evidence, secrets, raw transcripts, absolute paths, and rejected/superseded bodies.
- Backend failure is lexical fail-open: do not fail the LLM turn or mutate SQLite. Bound warnings and use cooldowns.

## Implementation sequence

1. Start from current merged mainline, never an obsolete feature-branch head.
2. Freeze a machine-readable lexical baseline before changing production retrieval.
3. Add a backend protocol and deterministic fake backend without changing runtime behavior.
4. Add sanitized canonical query/document serialization and stable SHA-256 source hashing.
5. Add transactional storage and validated vector encoding before wiring dense candidates.
6. Fuse lexical, identifier, and dense rankings with deterministic RRF; preserve stable tie-breakers.
7. Apply status, authority, confidence, type, and run-scope filters before fusion where possible and again after fusion/expansion.
8. Add bounded one-hop expansion only for provenance-relevant edge types; direct seeds outrank expansions.
9. Prove disabled and failed-backend results preserve lexical rows and the bounded `data_only` context.
10. Add the production backend, operator controls, rebuild tooling, and live A/B evaluation last.

## Evaluation

Track category-level Recall@8 and MRR@8, latency p50/p95, context size, rejected/superseded leakage, cross-run leakage, secret-bearing recall, state mutation, negative wrong-memory hit rate, and negative context-injection rate. Never accept aggregate improvement while identifier, correction/history, or safety categories regress. Leakage and mutation counters must remain zero. Record baseline limitations honestly instead of redefining metrics.

## Local embedding backend

For fully local deployment, use a dedicated operator-managed `LlamaCppEmbeddingBackend` backed by `llama-server --embedding`, not a generic remote service. Use `POST /v1/embeddings` only, bind loopback by default, and let Hermes connect without auto-starting the server. For Qwen3-Embedding-0.6B, establish F16 at native 1024 dimensions first; evaluate Q8_0 or 512-dimensional truncation only through later benchmarks. Query serialization receives the model instruction; documents do not.

Validate HTTP status, JSON shape, response count, complete unique indices, dimensions, finite values, nonzero norm, response size, timeout, and cooldown. Reorder by response index. Do not infer identity from response `model`; use configured model, GGUF revision, dimensions, and serializer version.

## Sanitization and stale vectors

Reuse the shared sanitizer, but enforce field bounds after sanitization and normalization. Persistence redaction may turn benign long tokens into `[LONG_TOKEN_REDACTED]`; use a slightly larger sanitizer budget and truncate after normalization. Invalidate stale vectors both on semantic-field updates and by source-hash mismatch at query time. Never use Python's salted `hash()` for stable identity.

## Verification

Keep protocol, serializer, migration, vector math, RRF, filters, expansion, fallback, HTTP adapter, and CLI in logical commits. Use RED → GREEN → regression verification. On Windows Git Bash, use:

```bash
SHORT=$(cygpath -d "$PWD/.venv/Scripts/python.exe")
HERMES_PYTHON="$SHORT" HERMES_TEST_WORKERS=1 bash scripts/run_tests.sh <tests> -q
```

Before each commit run canonical tests, static checks, `git diff --check`, and secret/path scans. After committing, rerun the targeted set and prove intended production-boundary files are unchanged. Record commands, exit codes, skipped live checks, risks, and working-tree status in the implementation log. Do not claim production readiness without full-suite, restart, provider, and live-backend evidence.

## References

- `references/hybrid-retrieval-llama-cpp.md`: benchmark, RRF, filtering, serializer, adapter, and Windows verification details.
- `references/llama-server-embedding.md`: llama-server/Qwen3 request, response validation, identity, and security cheatsheet.
