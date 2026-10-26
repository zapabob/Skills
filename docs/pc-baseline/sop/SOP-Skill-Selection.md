# SOP Skill Selection

## Scope

Apply this SOP before choosing how to perform a task with Codex, subagents, plugins, connectors, browser tools, research tools, security tools, document tools, or local scripts.

## Selection Order

1. User-named skills or plugins are mandatory candidates.
2. PC-wide mandatory skills from `C:\Users\downl\AGENTS.md` are applied before substantive work.
3. Task-matching skills are applied when their descriptions directly match the work.
4. Plugin-associated capabilities are preferred when the user explicitly names or invokes that plugin.
5. Existing project-native tools, scripts, test runners, and documentation are preferred over ad hoc replacements.

## Required Practice

1. Read the relevant `SKILL.md` before using a skill.
2. Load only the referenced files needed for the task.
3. Use scripts, templates, and assets from the skill when they exist and fit the task.
4. If multiple skills apply, use the smallest set that covers the task.
5. If a skill path is missing or stale, locate the actual installed skill path before falling back.
6. If no suitable skill exists, proceed with the applicable SOPs and record that no task-specific skill was available.

## Common Routing

- General implementation: `milspec-codex-standard`
- Current facts, official docs, primary sources, package trust, or web research: `deepresearch-defense-standard`
- Frontend UI/UX: `frontend-ui-engineering` plus `SOP-Frontend-Design.md`
- Documentation and ADRs: `documentation-and-adrs`
- Security scan or audit: Codex Security `security-scan`
- Threat model: Codex Security `threat-model`
- Security finding repair: Codex Security `fix-finding`
- GitHub PR, issue, or CI work: GitHub plugin skills when available
- Browser UI verification: Browser or frontend testing skills when local UI behavior must be inspected

## Prohibitions

1. Do not ignore a user-named plugin or skill without saying why.
2. Do not use a broad repository-wide security scan when the user asked for a narrow fix, unless risk evidence justifies widening scope.
3. Do not spawn subagents or long-running exhaustive scans without the authorization required by the active skill.
4. Do not replace project-native tools with unrelated tooling for convenience.

## Evidence

For substantive work, the implementation log should list the selected skills or state why no task-specific skill was used.
