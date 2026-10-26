---
name: x-psychology-transformer-gnn-workflow
description: "Train a small Transformer + GNN on recent X post features to derive psychological axes and cluster the user's posting style."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [x, twitter, social-media, pytorch, transformer, gnn, psychology, clustering]
---

# X Psychology Transformer + GNN Workflow

Use this skill when the user wants to turn recent X posts into a small deep-learning analysis that treats feature scores as psychological signals and then uses a Transformer + GNN to cluster or interpret the posting style.

## Purpose
- model the user's posting style as latent psychological axes
- keep the analysis lightweight enough to run on a consumer GPU such as RTX 3060
- ground the analysis in real public post artifacts rather than invented examples
- produce a reproducible report and a file-backed result

## Inputs
- recent public X post history, usually from `~/.hermes/lm-twitterer/activity.jsonl`
- a compact feature scoring scheme such as:
  - utility
  - proof
  - contrast
  - self-relevance
  - fork-differentiation
  - execution-first

## Recommended interpretation axes
Map the above into a small psychological space such as:
- **agency**: willingness to act, ship, and execute
- **epistemic grounding**: reliance on evidence, repo status, results, or proofs
- **opposition**: contrast, tension, hype-vs-reality framing
- **self_reference**: how much the post connects to the reader or the speaker's self-positioning

## Workflow

### 1) Collect data
Load the latest public posts from the activity log. Keep only real public posts; avoid drafts, secrets, or private artifacts.

### 2) Convert posts to feature vectors
Turn each post into a fixed-length vector of feature scores. Use a simple heuristic scoring layer first; the workflow is meant to be lightweight and reproducible.

### 3) Derive psychological targets
Create small latent targets from the features. Keep the mapping transparent and explainable.

### 4) Train a Transformer
Use a Transformer encoder over the feature tokens for per-post representation learning.

### 5) Train a GNN
Build a similarity graph over posts and run a tiny GCN/GCN-like model over the learned embeddings.

### 6) Cluster and interpret
Cluster the learned embeddings and summarize each cluster with:
- mean feature profile
- mean psychological profile
- representative post
- a plain-language interpretation

### 7) Save a report
Write a JSON report and a Markdown implementation log in the repo `_docs` folder.

## Operational notes
- Prefer CPU only for tiny smoke tests; use CUDA when available for the real run.
- For Windows mother-ship PCs, check `nvidia-smi` and then verify `torch.cuda.is_available()` inside the project venv.
- If the project venv lacks `pip`, bootstrap it with `python -m ensurepip --upgrade` before installing wheels.
- If `scikit-learn` or other analysis deps are missing in the venv, install them explicitly rather than assuming the base environment has them.
- Keep the dataset small enough to run quickly on a consumer GPU.

## Output format
Return:
- device / CUDA status
- number of posts used
- transformer loss
- GNN loss
- cluster summaries
- one short psychological interpretation

## Pitfalls
- Do not claim clinical or diagnostic meaning from the axes.
- Do not use private or secret data as training input.
- Do not overfit the interpretation to a tiny sample; label it as exploratory.
- If the GPU is visible to the OS but not to PyTorch, install a CUDA-enabled PyTorch wheel in the active venv and rerun.

## Relationship to other skills
Pairs well with:
- `x-post-feature-scoring-workflow`
- `hermes-x-posting-workflows`
- `ebbinghaus-memory`

Use this skill as the analysis layer when the user wants to go beyond scorecards into a small learned model.
