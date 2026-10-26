---
name: verification-gated-probes
description: Build auditable capability probes with explicit gates.
version: 1.0.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [verification, testing, probes, model-integration]
    related_skills: [software-development/test-driven-development, software-development/windows-hermes-code-verification]
---

# Verification-Gated Capability Probes

## When to Use

Use for local model, embedding endpoint, or API compatibility work where a diagnostic probe must produce auditable evidence before production integration. This is a class-level workflow, not a provider-specific recipe.

## Core contract

Separate three things:

1. **Required base checks** — compatibility conditions that determine the base verdict: endpoint health, response shape/count/index coverage, dimension, finite/nonzero vectors, normalization, repeatability, batch stability, and the primary semantic ordering check.
2. **Observations** — informative measurements such as Japanese/cross-lingual retrieval, profile comparisons, margins, and latency. Record them, but do not silently promote them to gates.
3. **Optional required checks** — checks such as soak/stress that become required only when explicitly requested.

Never use a blanket `all(checks.values())` when a check can be not-run. Use an explicit required-check list and identity comparison (`is True`) so `None` remains distinct from `False`.

## Opt-in soak pattern

Represent an unrequested soak explicitly:

```python
BASE_REQUIRED_CHECKS = (...)


def required_check_names(*, soak_requests: int) -> tuple[str, ...]:
    if soak_requests < 0:
        raise ValueError("soak_requests must be non-negative")
    return BASE_REQUIRED_CHECKS + (("soak",) if soak_requests > 0 else ())


def determine_verdict(checks, *, soak_requests: int) -> str:
    required = required_check_names(soak_requests=soak_requests)
    return "pass_text_only" if all(checks.get(name) is True for name in required) else "fail_model_compatibility"
```

Output should distinguish `not_run`, `passed`, and `failed`; JSON `null` is acceptable when the schema also records `requested: false`. Requested soak should report requested count, completed count, failures, and pass/fail.

## TDD and evidence sequence

1. Inspect current code and commit boundary; do not rewrite the previous commit when a follow-up fix is appropriate.
2. Add regression tests for zero-request non-failure, not-run serialization, successful requested soak, failed requested soak, and negative input rejection. Confirm RED, including collection failure for missing helpers, before implementation.
3. Implement the smallest change while retaining production boundaries.
4. Run focused tests, then the canonical project runner and adjacent existing retrieval/embedding tests.
5. Run lint, compile, and `git diff --check`.
6. Update the implementation log with observed results and missing evidence.
7. Commit independently with a descriptive fix message; verify HEAD, commit subject, clean status, and post-commit tests.

## Safety and readiness boundaries

- A passing text-only probe is not a multimodal or VL compatibility claim.
- Do not call a model live result observed unless a real pinned model/server run occurred.
- Keep raw vectors, raw responses, credentials, and absolute local paths out of summary JSON/logs.
- Keep Semantic Graph data canonical; vector indexes remain reproducible derived data.
- Do not start an associative adapter or production embedding backend until control/candidate live evidence and a fixed serializer/dimension profile exist.

## Common pitfalls

- `all(checks.values())` treats `None` as failure even when a check was intentionally not requested.
- Adding observational checks to `checks` makes future consumers accidentally treat them as gates.
- A test summary that reports only exit code hides pass/skip counts; prefer runner output with counts.
- A requested test path may be absent; report that fact rather than claiming it ran.
- “Pending live validation” is the correct status when no pinned real model was run; it is not a failure and not a pass.

## Support files

- See `references/llama-embedding-probe-follow-up.md` for the reusable regression matrix and evidence checklist.
