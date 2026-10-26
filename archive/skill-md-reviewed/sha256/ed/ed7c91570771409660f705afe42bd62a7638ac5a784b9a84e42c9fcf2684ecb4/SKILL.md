---
name: spike
description: "Throwaway experiments to validate an idea before build."
version: 1.0.0
author: Hermes Agent (adapted from gsd-build/get-shit-done)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spike, prototype, experiment, feasibility, throwaway, exploration, research, planning, mvp, proof-of-concept]
    related_skills: [sketch, subagent-driven-development, plan]
---

# Spike

Use this skill when the user wants to **feel out an idea** before committing to a real build — validating feasibility, comparing approaches, or surfacing unknowns that no amount of research will answer. Spikes are disposable by design.

Load this when the user says things like "spike this out", "quick prototype", "is this possible?", or "compare A vs B".

## When NOT to use this

- Answer is in docs or code — research, don't build
- Work is production path — use the `plan` skill instead
- Idea already validated — implement directly

## Workspace

Default: `spikes/NNN-slug/` in repo root. Alternative: `.tmp/openclaw-spikes/slug/` for untracked spikes. Each spike gets a `README.md` and minimal code.

## Core method

```
decompose → research → build → verdict
```

1. **Decompose** — break into 2-5 independent feasibility questions. Order by risk (hardest first).
2. **Research** — read enough docs/source to pick a credible approach. Surface competing options.
3. **Build** — smallest runnable artifact. CLI, HTML, or endpoint. Test edge cases.
4. **Verdict** — `VALIDATED`, `PARTIAL`, or `INVALIDATED` with evidence.

## Rules

- Invalidated spikes are valuable — they rule out paths with evidence.
- Never merge spike code into production without rewriting it.
- Check external dependency health: recent release, docs, license, install friction.
- If external dependencies are evaluated, note their maintenance status.

## Attribution

Adapted from the GSD (Get Shit Done) project's `/gsd-spike` workflow — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)).

---

> Consolidated from `software-development/spike` and `openclaw-imports/spike` (2026-07-12). Name collision resolved by merging both into this umbrella.
