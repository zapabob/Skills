---
name: research-automation-runner
description: Inspect vendored research frameworks before running them.
author: Hermes Agent
license: MIT
---

# Research Automation Runner

Use this class-level skill when a repository contains a vendored autonomous research, experiment, or paper-generation framework and the user wants to run it through a subscription, OAuth route, local model, or free API tier.

## Core workflow

1. Locate the actual vendor tree, entrypoint, templates, README, dependency manifests, and provider/client code. Do not infer that the implementation exists from a skill example or wrapper filename.
2. Separate upstream/vendor source, repository launcher or adapter, credential resolver, experiment templates/overlays, and result directories.
3. Verify the entrypoint is a file and templates are present before proposing a live run. A partial vendor directory is an incomplete checkout; stop before model calls.
4. If a sync script exists, run its dry-run first. Review upstream URL/ref, vendor target, skipped paths, and overlays. Execute synchronization only after explicit authorization for the external fetch and repository update.
5. Re-verify entrypoint, templates, required experiment files, and repository verification scripts. Prefer a non-live smoke test or `--help` before a model call.
6. Resolve credentials through the repository adapter, OAuth/free-tier router, or environment overlay. Never print, store, summarize, or paste secrets. Report only provider IDs, model family, route, environment-key names, and credential presence.
7. **Isolate heavy research dependencies.** Create a dedicated ignored runtime environment under `.runtime/` rather than installing Aider/AI-Scientist dependencies into the main Hermes `.venv`; these packages can downgrade or replace core packages. On Windows/Git Bash, invoke the isolated interpreter explicitly and set `PYTHONPATH` to both the vendor tree and repository root when the vendored package is not installed.
8. Start with the smallest possible live PoC: one idea and one verified template. Avoid full paper generation until pipeline and cost behavior are confirmed. For mathematics, use chapter-scoped, input-driven prompts rather than asking the framework to invent theorems.
9. **Classify validation layers separately.** Template verification, CLI/import success, credential resolution, HTTP response integrity, experiment execution, and LaTeX/write-up generation are distinct gates. `has_credentials=true`, a successful process exit, or a JSON file alone does not prove that valid model output or a completed experiment exists. Treat HTML challenge pages and malformed/generated placeholder content as provider failures.
10. Audit generated proofs, citations, novelty claims, numerical results, and LaTeX as drafts. Check definitions, quantifiers, implication direction, local/global scope, and theorem-versus-experiment distinctions.

## AI Scientist integration notes

A Hermes checkout may use:

```text
vendor/openclaw-mirror/AI-Scientist/
scripts/ai_scientist_launcher.py
tools/ai_scientist_env.py
tools/ai_scientist_deps.py
```

The Hermes launcher and upstream `launch_scientist.py` are distinct and both must be checked. Extension files named `ai_scientist_runner.py`, `ai_scientist_lite.py`, or `ai_scientist_pulse.py` may be wrappers and do not prove that the upstream framework is synchronized.

See `references/ai-scientist-vendor-inspection.md` for repository-specific inspection details.

## Provider and subscription safety

Web subscriptions such as ChatGPT, Claude, or Gemini web are not automatically API credentials. Verify that the selected route is supported by the local client and that free-tier availability, model names, quotas, region, and billing conditions are current. Use API-compatible routing only after checking the vendor client and repository adapter.

## Verification sequence

```bash
py -3 scripts/sync_ai_scientist_vendor.py --dry-run
py -3 scripts/sync_ai_scientist_vendor.py --execute
py -3 scripts/verify_ai_scientist_templates.py --vendor
py -3 scripts/smoke_ai_scientist.py
```

Do not present `--execute` or a live model command as completed without actual output. Do not use an example template or model name until verified in the current vendor tree.
