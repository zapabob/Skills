---
name: embedding-model-validation
description: Validate local embedding model servers for hybrid retrieval.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
category: mlops
metadata:
  hermes:
    tags: [embedding, llama.cpp, retrieval, hybrid-search, semantic-graph, probe, validation]
    category: mlops
---

# Embedding Model Validation

Use when standing up or qualifying a local embedding model (llama.cpp GGUF or OpenAI-compatible `/v1/embeddings`) as a candidate retrieval backend for a Semantic Graph / vector-index hybrid system.

## When to Use

- Probe a GGUF embedding model for `/v1/embeddings` compatibility.
- Discover actual dimension, pooling behavior, normalization, repeat stability, and batch behavior.
- Separate transport/shape compatibility from semantic usability and production readiness.

## Workflow

1. Pin repository, revision/commit, exact GGUF filename, SHA-256, server build/version, pooling, normalization, and expected dimension.
2. Verify the selected binary supports HTTPS/HF before using `-hf`; acquisition/build failure is not model incompatibility.
3. Launch on loopback with explicit embedding mode, pooling, and normalization. Wait for both `model loaded` and `listening`; `/health` may return 503 while loading.
4. Probe `/health` → `/v1/models` → `/v1/embeddings`.
5. Validate flat-vector shape, unique indices `0..N-1`, non-empty vectors, stable dimension, finite values, nonzero vectors, and unit norm.
6. Measure repeat cosine and max delta separately. Do not silently loosen a failed threshold to manufacture PASS; quantized VL models may be ranking-compatible without bit-exact repeatability.
7. Validate batch sizes and semantic ordering with declared margins. Keep Japanese/cross-lingual and instruction-profile checks observational unless explicitly promoted to gates.
8. Run soak only when requested. With zero requests emit `checks.soak=null`, `requested=false`, `passed=null`; not-run is not failure.
9. Bind evidence to an exact commit and clean worktree. Keep local tests, remote CI, live-provider evidence, review state, and production readiness separate.
10. Stop the server and save a redacted summary without raw vectors, credentials, tokens, private source text, or unnecessary local paths.

## Verdict separation

- `pass_text_only`: all base checks pass; soak is not requested or passes.
- `fail_model_compatibility`: a required base check or requested soak fails.
- A model may be transport/shape/semantic compatible while failing a strict repeatability gate; report the decomposition rather than hiding it.

## Invariants

Embedding remains a candidate generator; Semantic Graph is canonical. Do not create a production embedding adapter until live control and candidate probes pass. Record model revision and checksum, but not private cache paths or real local usernames.

## References

- `references/llama-cpp-embedding-probe.md` — launch recipe, Windows build caveats, probe checks, soak semantics, and quantized-VL repeatability findings.
