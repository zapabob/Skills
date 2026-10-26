# SOP Implementation Start Gate

## Scope

Apply this SOP before any substantive implementation, file edit, dependency change, configuration change, test rewrite, release action, or automation update on this PC.

Read-only inspection, status checks, and evidence gathering may happen before this gate when they are needed to identify the relevant project files, SOPs, or risks.

## Required Inputs

- PC-wide baseline: `C:\Users\downl\AGENTS.md`
- Codex-local baseline: `C:\Users\downl\.codex\AGENTS.md`
- Pre-implementation system prompt: `C:\Users\downl\_docs\prompts\CLAUDE-FABLE-5.md`
- SOP index: `C:\Users\downl\_docs\sop\SOP-Index.md`
- Project-local `AGENTS.md`, when present
- Project-local SOP or `_docs` standards, when present
- Relevant skills named by the user or matched by task type
- Relevant repository code, docs, config, tests, and runtime state

## Gate Procedure

1. Read the PC-wide `AGENTS.md`.
2. Read the Codex-local `C:\Users\downl\.codex\AGENTS.md` when running inside Codex desktop, Codex CLI, plugin-managed Codex, or automation-managed Codex.
3. Read `C:\Users\downl\_docs\prompts\CLAUDE-FABLE-5.md` before implementation. Treat it as required context for the task, but do not let it weaken higher-priority system, developer, security, privacy, MILSPEC, or project-local instructions.
4. Inspect the current workspace for project-local `AGENTS.md`, nested `AGENTS.md`, SOPs, `_docs`, README files, design docs, security docs, and implementation logs.
5. Resolve the applicable SOP set in this order:
   - common engineering standard
   - this implementation start gate
   - skill selection SOP
   - deep research SOP when current, primary-source, web, package-trust, or security-sensitive facts are involved
   - security SOP when trust boundaries, secrets, auth, permissions, external inputs, networking, supply chain, or privileged operations are involved
   - domain SOPs
   - frontend design SOP when UI/UX is involved
   - language SOPs
6. Resolve the applicable skills:
   - skills explicitly named by the user
   - skills required by PC-wide `AGENTS.md`
   - skills whose descriptions match the task
   - plugin-associated skills when the user names or invokes a plugin
7. Confirm requirements, constraints, acceptance criteria, verification plan, and residual-risk handling before editing.
8. Do not begin implementation while the applicable standards are unknown, contradictory, or materially incomplete.

## Conflict Rule

When project-local instructions conflict with PC-wide instructions, use the stricter instruction. Project-local instructions may narrow or strengthen controls, but must not weaken MILSPECLLMOps, security, verification, secret handling, implementation logging, or evidence requirements.

## Minimum Start Checklist

- PC-wide `AGENTS.md` was read or already present in current context.
- Codex-local `C:\Users\downl\.codex\AGENTS.md` was read or already present in current context when applicable.
- `C:\Users\downl\_docs\prompts\CLAUDE-FABLE-5.md` was read or already present in current context.
- Project-local instruction files were checked.
- Applicable SOPs were selected.
- Applicable skills were selected and read as needed.
- Requirements and acceptance criteria are explicit enough to proceed.
- The verification path is known, or the reason it cannot be known yet is recorded.
- Security, privacy, and destructive-operation risks have been considered.

## Goal Handling

If a runtime goal feature is available and a task explicitly requires a goal, use it according to the active tool rules. If a slash-command goal UI is unavailable, use the exposed goal API when available. If no goal mechanism is available, state the objective in the working update and record it in the implementation log.

Do not use goal status as a substitute for verification evidence.

## Completion Evidence

For substantive changes, record in `_docs`:

- selected SOPs and skills
- implementation scope
- changed files
- commands run
- verification results
- skipped checks and reasons
- residual risk
