---
name: windows-test-failure-lanes
description: Use when tests, CI reproduction, type checks, pytest, Vitest, tsgo, builds, or smoke checks fail on Windows and the failure may involve timeout, encoding, shell, path, cache, or environment drift.
---

# Windows Test Failure Lanes

## Overview

Use this skill to keep Windows-specific test failures honest. First decide whether the failure is product behavior, test harness drift, Windows shell/runtime behavior, stale generated output, or local environment state. Then rerun the smallest lane that proves the claim.

## Lane Selection

| Symptom | First Check | Typical Rerun |
| --- | --- | --- |
| Pytest timeout or signal issue | timeout plugin and host signal support | `uv run --isolated --extra dev --no-editable pytest --timeout-method=thread <tests>` |
| Repo-level pytest addopts break local run | `pytest.ini`/`pyproject` addopts vs current host | rerun the same targeted tests with `-o addopts=` and then restore normal lane scope |
| Python UTF-8/mojibake failure | file reads and console encoding | set `PYTHONUTF8=1`, then rerun the affected tests |
| `pytest-randomly` seed crash | setup/teardown failure before assertions | rerun with `-p no:randomly -p no:cacheprovider` |
| Vitest stalls or no output | worker count and watchdog timeout | set repo-specific worker/no-output env vars and run one file |
| TypeScript batch errors | active tsconfig lane and reported files | run the exact `tsconfig` lane with incremental disabled when supported |
| Build rewrites broad generated files | runtime entrypoint and generated output ownership | prefer no-emit checks, or restore unrelated generated churn |
| Local CLI works in one shell only | PATH, shim, WSL/Windows split | prove each path separately and report boundaries |

## Workflow

1. Capture the exact command, shell, cwd, env knobs, and first failing error.
2. Read package scripts, CI YAML, test config, and helper scripts that define the lane.
3. Separate harness/setup failures from product-code assertions.
4. Prefer targeted local reproduction over broad suites:
   - one test file
   - one tsconfig
   - one build target
   - one parser or smoke command
5. Apply the smallest fix or rerun adjustment that matches the failure class.
6. Record both:
   - the verification lane that passed
   - the broader lane not run or still noisy, with reason

## Closeout Evidence

- command line and relevant env variables
- pass/fail result summary
- changed files, if any
- reason a broad CI lane was not used as the regression signal
- residual risk when the local lane does not fully mirror CI

## Common Mistakes

- Debugging production code when the test never reached an assertion.
- Treating Windows encoding or signal behavior as a repo regression without proof.
- Broadening a narrow fix until unrelated red lanes dominate the task.
- Claiming Windows and WSL behavior are equivalent without validating both.
