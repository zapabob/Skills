---
name: windows-electron-lifecycle-debugging
description: "Use for Windows Electron lifecycle failures."
version: 0.1.0
author: Hermes
tags: [Windows, Electron, AIRI, Lifecycle, Debugging, Verification]
platforms: [windows]
---

# Windows Electron Lifecycle Debugging

## Use when

Use for Windows Electron applications managed by a supervisor, especially AIRI, when the app reports a successful start but the window, CDP renderer, chat authority, or health state disappears shortly afterward.

This is a class-level runtime workflow, not a one-off fix for a particular error string.

## Core principle

A successful `start` response is only an initial observation. Treat the runtime as stable only after a delayed second health check proves that the process tree, CDP endpoint, renderer targets, and configuration boundary all remain live.

## Workflow

### 1. Establish the component boundary

Separate these questions before changing code:

- Is the Hermes API live and serving the expected model?
- Is the TTS service live and serving the expected voice?
- Is the Electron supervisor alive?
- Is the renderer alive and reachable through CDP?
- Is the intended renderer role/authority present?
- Can the UI send a real message and display an assistant response?

A passing API probe or provider seed is not proof of UI chat success.

### 2. Inspect the full Windows process tree

On Windows, stale `pnpm`, `cmd.exe`, Node, and Electron descendants can survive a supervisor restart. Enumerate processes by command line and identify the target application's parent/child tree. Stop only stale processes belonging to the target application. Do not terminate unrelated Electron applications, including Hermes Desktop.

Prefer a clean tree before retrying. Repeatedly starting over a stale tree creates duplicate dev servers, port conflicts, reused renderer state, and misleading health results.

### 3. Start through the canonical lifecycle

Use the Hermes AIRI lifecycle/supervisor path so provider sync, TTS sync, CDP seed, and state files are updated through one authority. Avoid ad-hoc production commands during diagnosis unless explicitly testing a separate build artifact; ad-hoc processes can bypass supervision and confuse the next health check.

### 4. Verify twice

After start, capture the immediate result, then wait briefly and query status again. Require all of the following for stable-runtime evidence:

- `running=true`
- `healthy=true`
- a live CDP port and page target
- a stable renderer target count
- Hermes `/v1/models` returns HTTP 200 and the expected model
- TTS health returns HTTP 200 and the expected provider/voice
- CDP seed/readback reports the expected provider and model

If the second check reports `running=false`, investigate orphaned parents, duplicate ports, and renderer startup/crash logs before changing provider configuration.

### 5. Verify authority and UI separately

For multi-window AIRI-like apps, check that the main authority renderer and chat/follower renderer roles are compatible. Avoid forcing navigation from the seed routine unless the application explicitly requires it; navigating a renderer during authority initialization can break synchronization.

Only claim end-to-end chat success after a real UI message is submitted and the assistant response body is observed. If only runtime health, provider readback, or backend probes pass, report those as scoped successes and label UI E2E as unverified.

### 6. Run scoped tests before broad suites

Run the changed component's focused regression tests, typecheck, lint, and build independently. Then optionally run the repository-wide suite. On Windows, classify unrelated failures such as MSYS path conversion, Proactor handle errors, symlink privilege failures, proxy-environment differences, or process interference as environment/test-harness failures unless the changed component reproduces them.

Never report the full suite as passing when it failed or timed out. Preserve the exact failing test names and error classes for follow-up.

## AIRI-specific reference

See `references/airi-hermes-runtime-verification.md` for the reusable AIRI provider/TTS/CDP checks, process cleanup pattern, and evidence-reporting template.

## Common pitfalls

- Trusting the immediate `airi_start` result without a delayed `airi_status` check.
- Killing all Electron processes instead of filtering by AIRI's vendor path.
- Starting a second dev tree while an old `pnpm dev:tamagotchi` tree still owns the port.
- Treating provider readback as proof that the chat UI can send.
- Forcing `/#/chat` navigation from a seed routine and removing the authority renderer.
- Calling a large, partially completed Windows suite a pass because most tests were green.

## Completion checklist

- [ ] Target process tree was inspected and stale target-only descendants were removed.
- [ ] Canonical lifecycle start completed.
- [ ] Delayed status check remained healthy.
- [ ] API, TTS, CDP seed/readback, and renderer target evidence were collected.
- [ ] Focused tests/typecheck/lint/build passed.
- [ ] UI E2E was either observed or explicitly marked unverified.
- [ ] Full-suite failures, if any, were reported without misattribution.
