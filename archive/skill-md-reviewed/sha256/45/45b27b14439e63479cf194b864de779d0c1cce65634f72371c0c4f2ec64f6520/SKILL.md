---
name: airi-runtime-debugging
description: Use when AIRI chat times out or its Electron runtime exits.
version: 0.1.0
author: Hermes
platforms: [Windows]
tags: [AIRI, Electron, Runtime, ChatAuthority, CDP, Windows]
---

# AIRI Runtime Debugging

Use this skill when AIRI starts but chat requests time out, the main renderer is missing, the chat authority is unavailable, or the Electron/dev process exits shortly after launch.

## Scope

This skill covers the runtime layer between AIRI Electron windows, renderer routes, `BroadcastChannel` chat synchronization, Hermes provider seeding, and Windows process supervision. It complements provider/TTS recovery; it does not replace it.

## Diagnostic sequence

1. **Establish the live state before editing.** Run the AIRI status command/tool and record only sanitized facts: `running`, `healthy`, CDP port, page URL, target count, provider/model, Hermes probe, and TTS probe. Never print API keys or tokens.
2. **Inspect CDP targets.** Query the AIRI CDP endpoint and classify targets by type and URL. A normal page list must be checked for the main `/` renderer, the `/#/chat` page, and background pages such as BeatSync. Do not infer that a healthy provider means the renderer is usable.
3. **Classify the authority failure.** The chat page normally runs as a follower and sends commands through `BroadcastChannel`; the main `/` renderer is the authority. `Timed out waiting for chat authority response` means the request path reached follower dispatch but no authority replied. Treat a missing `/` page as a routing/lifecycle defect, not as an API-key defect.
4. **Trace the creation path.** Read the Electron main-window provider registration and its dependencies. Background windows must not block creation of the main window. Verify that BeatSync loading is non-blocking and that the main window is visible. Verify the main renderer loads the root route, not `/#/chat`, when root owns authority.
5. **Check renderer initialization timing.** Provider seed must survive reload and late auth-provider hooks. Seed/read back after the renderer has initialized; do not force a route navigation during chat-sync initialization because navigation can interrupt authority setup.
6. **Use a bounded authority fallback when root can be absent.** Keep the normal root-authority/follower arrangement. If a standalone chat window sees no authority announcement after a bounded delay (currently 5 seconds), promote that chat window to authority. Clear the timer on disposal and do not make every chat window an authority unconditionally.
7. **Separate runtime exit from application errors.** If AIRI is healthy immediately after start but exits seconds later, inspect the `pnpm dev:tamagotchi` parent and Electron child process tree, stale dev parents, port ownership, and exit logs. Clean only AIRI-related processes; do not kill unrelated Hermes/Desktop processes. Restart from a clean parent tree and recheck after at least 7 seconds.
8. **Verify in layers.** Run the focused lifecycle test, AIRI typecheck, targeted ESLint, and production build. Then perform runtime health checks after a delay. Only claim chat is fixed after a real UI send produces an assistant response body; provider seed, HTTP 200, and `healthy=true` are not E2E proof.

## Required regression coverage

When adding authority fallback, test all of the following:

- root route initializes as `authority`;
- initial `#/chat` resolves as `follower`;
- no authority announcement causes exactly one fallback promotion after the delay;
- disposal clears the timer;
- unrelated windows retain their existing `client`/no-sync behavior.

## Common pitfalls

- `authorityId` is a Pinia store ref that is auto-unwrapped on the store instance; runtime code reads `chatSyncStore.authorityId`, not `.value`.
- A test mock may need to model Pinia's unwrapped shape rather than the source ref shape.
- Running the full repository test suite can interfere with live AIRI processes on Windows. Run focused AIRI tests and runtime checks separately, then restart AIRI after any process-heavy suite.
- A CDP target count alone is insufficient; inspect URL/route and delayed process survival.
- Never treat a successful build or provider health probe as proof that the chat UI works.

## Supporting reference

See `references/authority-timeout-debugging.md` for the condensed failure signature, route model, fallback behavior, and verification evidence pattern from the AIRI/Hermes integration.
