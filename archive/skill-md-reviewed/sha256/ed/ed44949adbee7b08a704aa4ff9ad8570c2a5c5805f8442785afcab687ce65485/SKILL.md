---
name: embedding-model-quantization
description: Convert and benchmark GGUF embedding quantizations.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mlops, gguf, embeddings, llama.cpp, quantization, windows]
    related_skills: [mlops/inference/llama-cpp, embedding-model-validation, local-llm-server]
---

# Embedding Model GGUF Quantization & Pareto Selection

## Use when
Use for HuggingFace sentence-transformer/embedding conversion to GGUF, quantization candidate generation, local `llama-server --embedding` validation, or evidence-based quality/size/latency selection.

## Workflow
1. Pin the Hugging Face repo revision from its API. Record architecture, parameter count, dimensions, context length, tokenizer/pooling files, and the revision separately from every GGUF SHA-256.
2. Inspect the local `llama.cpp` fork/build and preserve unrelated dirty changes. Keep model files and transient benchmark JSON outside the repository.
3. Convert once to an F16 base, then quantize all candidates from that same file. For encoder-only sentence-transformer/XLM-R/BGE models, use `--sentence-transformers-dense-modules`.
4. Compare F16, Q8_0, Q6_K, and Q5_K_M when practical. Use `--dry-run` where supported. Hash and size each candidate.
5. Validate each candidate in isolation with `llama-server --embedding --embd-normalize 2`. Wait through loading-period 503s until `/health` is HTTP 200 and `{"status":"ok"}`. Check `/v1/models` metadata and probe `/v1/embeddings` for runtime dimension, finite values, and norm.
6. Run the same benchmark for every candidate using a fresh SQLite database, identical fixture/parameters/serializer/RRF/safety gates, and identity bound to repo, revision, candidate SHA, filename, provider/profile, and dimensions.
7. Select by Pareto evidence across retrieval quality/no-regression groups, leak/mutation gates, file size, load time, end-to-end latency, and measured VRAM. Treat missing VRAM as missing evidence. Keep a size/latency fallback when useful.
8. Leave the selected server running only when explicitly requested. Otherwise stop it and verify no listening socket remains. Keep production adapter/default-retrieval promotion separate from isolated evaluation.

## Windows and subprocess pitfalls
- Use Python 3.12 for pinned converter environments when the required Torch version has no Python 3.13 Windows wheel.
- Prefer a Python orchestrator for candidate loops: foreground shell `&` may be rejected, and Bash `kill` may leave the real Windows listener alive. Use `cmd.exe /c "taskkill /F /IM llama-server.exe"`, then verify with `netstat -ano | grep ':8084' | grep LISTEN`.
- Inline non-ASCII JSON can become invalid UTF-8 under Windows/MSYS. Use an ASCII probe or write UTF-8 JSON to a file and send it with `curl --data-binary @probe.json`.
- Set environment variables before importing module-level benchmark constants; propagate `PYTHONPATH` explicitly to subprocesses.
- Preserve CRLF implementation logs with byte-level append when needed; whole-file rewrites create noisy diffs.

## Evidence contract
Record exact source/build revisions, commands, artifact hashes/sizes, runtime dimensions, health/model/probe evidence, group Recall/MRR, negative behavior, context length, latency, load time, safety gates, missing measurements, and residual risk. Never promote a candidate solely because it loads or wins one fixture.

## Derived-model publication gate
Treat the GGUF repository as a derived artefact, not a replacement for the source model. Before upload, confirm a separate destination in the uploader's namespace and link the source model from the README/model card. Never overwrite the source repository by default. Treat any Hugging Face token pasted into chat as exposed: do not copy it into commands, files, environment variables, or logs. Require fresh supported authentication with `hf auth login`, verify the account with `hf auth whoami`, upload only the validated staging directory, then verify the remote file list and README. Do not report publication complete from local staging evidence alone.

## Support files
- `references/hf-to-gguf-embedding-quantization-windows.md` — Windows recipe, pitfalls, and observed evidence patterns.
- `templates/llama_quant_candidate_harness.py` — reusable server-start, health-poll, probe, benchmark, and hard-cleanup loop.
