---
name: hermes-plugin-integration
description: Use when integrating external software as a Hermes plugin.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, plugins, integration, lifecycle, testing]
    category: software-development
    related_skills: [hermes-agent, hermes-desktop-plugins]
---

# Hermes Plugin Integration Skill

Use this skill to wrap an external program or service as a Hermes plugin while preserving the host project's plugin contracts. It covers discovery, lifecycle, activation gates, implementation, and verification; it does not assume that desktop UI plugins, Python runtime plugins, MCP servers, and ordinary tools share an API.

## When to Use

- The user asks to clone, wrap, package, or integrate an external project into Hermes.
- An integration must start or perform side effects only after an explicit user action.
- A plugin's event source or lifecycle is uncertain and must be established before implementation.

## Prerequisites

- The exact target repository and intended Hermes surface (desktop UI, Python runtime plugin, MCP, or tool) are known.
- The relevant checkout and its existing local changes are accessible.
- User-directed activation conditions and prohibited implicit triggers are recorded literally.

## How to Run

1. Confirm the repository identity, current branch, and worktree status before writing.
2. Use CodeGraph first on the required workstation for repository navigation; then inspect the concrete plugin loader, examples, and tests.
3. Inspect the upstream project's actual install, CLI/API, configuration, supported platform, and shutdown behavior. Prefer official docs/source over assumptions.
4. Trace the requested activation event from its real producer to the plugin callback. Verify the channel/surface (Hermes chat versus an external app's chat) rather than inferring from wording.
5. Write a failing behavior test for the trigger and at least one non-trigger; then implement the smallest wrapper that passes.
6. Keep external process start explicit and idempotent. Do not start on application/process detection unless the user explicitly requested that trigger.
7. Run focused tests, relevant project checks, and a safe readiness/doctor check. Record exact outputs, changed files, and unresolved blockers in the required project log.

## Quick Reference

- **Find the correct extension surface first:** desktop UI plugin, Python plugin, MCP server, or core tool. Follow its native registration and lifecycle API; do not transplant an example from another plugin system.
- **Activation contract:** define exact event source, accepted phrase/command, normalization rules, and non-trigger behavior before coding.
- **Side effects:** test that ordinary startup and unrelated messages do not launch the wrapped program.
- **External projects:** pin or otherwise make the source reproducible; document setup and dependencies; avoid embedding secrets.
- **Delivery:** report implementation and verification separately. A plan or generated file is not a working integration.

## Procedure

1. **Scope the target.** Verify the repository URL/name from git remotes and local tree. If the checkout differs from the user-named repository, stop and resolve it before edits. Capture `git status --short` and do not overwrite unrelated changes.
2. **Map the extension contract.** Locate plugin discovery, registration signatures, enable/disable gates, tool/event dispatch, state storage, and tests. For desktop UI plugins, use the desktop-plugin SDK; for Python runtime plugins, inspect `plugins/` examples and loader code; for MCP, use Hermes MCP configuration/API. Never infer interchangeable APIs from the word “plugin.”
3. **Map upstream behavior.** Identify entrypoint, command arguments, local API, readiness signal, error reporting, and stop semantics from source or authoritative documentation. Use the upstream's supported operation rather than inventing flags or endpoints.
4. **Specify activation.** Write a short contract including:
   - event surface and provenance;
   - exact user command/phrase and whether matching is exact or normalized;
   - whether the trigger is consumed/acknowledged;
   - what happens for unrelated messages;
   - whether repeated activation is idempotent and how shutdown works.
5. **Test before implementation.** Add a behavior test showing the explicit trigger causes one launch, and a contrasting test showing app startup/process detection or unrelated chat does not launch. Run tests and confirm expected RED before production changes.
6. **Implement narrowly.** Keep lifecycle management separate from trigger parsing and upstream transport. Ensure no startup hook bypasses the explicit gate. Make launch failures visible and avoid blocking the chat loop.
7. **Verify safely.** Run focused tests first, then the relevant suite. Verify disabled/unconfigured behavior fails closed. Do not initiate a live external action merely to prove a mock or dry-run path.
8. **Log and report.** Use the repository's implementation/SOP log convention. Distinguish verified facts, attempted actions, and blockers; never claim a clone, install, launch, or test passed without tool evidence.

## Pitfalls

- Do not confuse a command written in Hermes chat with a message in the integrated application's chat. The actual source event matters.
- Do not interpret “when VRChat starts” as authorization to auto-start if the user requires an explicit Hermes-chat command. A process watcher is not equivalent to explicit user intent.
- Do not copy a guessed plugin skeleton or guessed CLI flags/API endpoints. Inspect the actual loader and upstream source first.
- Do not report intended changes as completed when the filesystem or terminal transport is unavailable. A failed tool call is a blocker, not evidence that a code change landed.
- Do not persist transient machine/tool failures as general rules or keep retrying an unchanged failing command indefinitely; use a genuinely independent supported route or report the blocker accurately.
- Do not edit protected or user-owned skills autonomously; if a relevant skill is protected, use an allowed curator-managed class-level skill or recommend curator adoption.

## Verification

- Tests prove the explicit activation path and a non-trigger path.
- Normal Hermes/desktop startup does not launch the external program without the trigger.
- The trigger originates from the requested chat surface, verified against the real event contract.
- Plugin enablement, missing dependency, launch failure, duplicate trigger, and shutdown behavior are accounted for.
- Report includes exact changed paths, commands and results, and any remaining limitations.