---
name: milspec-codex-standard
description: Use when starting any Codex session on this PC, and before coding, testing, reviewing, documenting, or changing project files in local workspaces that must follow the PC-wide MILSPECLLMOps baseline, the canonical SOP set under `%USERPROFILE%\_docs\sop`, verification discipline, implementation-log policy, and language-specific controls for Python, TypeScript, Rust, Go, CSharp, CPP, and C.
---

# MILSPEC Codex Standard

## Overview

Apply this skill as the mandatory baseline for all Codex work on this PC.
Enforce MILSPECLLMOps discipline, SOP-driven engineering control, evidence-based verification, and detailed `_docs` implementation logging.
For any task that needs web search, latest information, official documentation, or security-sensitive research, apply `%USERPROFILE%\.codex\skills\deepresearch-defense-standard\SKILL.md` before this skill.

## Mandatory Baseline

1. Read the relevant existing code, docs, config, and tests before changing anything substantial.
2. Prefer the smallest safe change that preserves architecture, clarity, and maintainability.
3. Add input validation, error handling, and observability at boundaries when behavior or risk changes.
4. Comment the why, not the what.
5. Do not claim MILSPEC-compliant LLMOps unless the mapped standards, requirements, acceptance criteria, test plan, and evidence are explicitly defined.
6. Do not rely on memory alone for unstable, current, primary-source-sensitive, or security-sensitive facts.

## SOP Resolution

1. Apply `%USERPROFILE%\_docs\sop\SOP-Common-MILSPECLLMOps-Engineering-Standard.md` first.
2. Apply the relevant domain SOPs next:
- `SOP-LLMOps.md`
- `SOP-MLOps.md`
- `SOP-AIOps.md`
- `SOP-WebApp-Development.md`
- `SOP-Application-Development.md`
- `SOP-Internet-Connectivity.md`
3. Apply the relevant language SOP last:
- `SOP-Python.md`
- `SOP-TypeScript.md`
- `SOP-Rust.md`
- `SOP-Go.md`
- `SOP-CSharp.md`
- `SOP-CPP.md`
- `SOP-C.md`

## Verification Rules

1. For behavior changes, update or add tests at the appropriate level.
2. Run the strongest practical verification available: lint, typecheck, build, unit, integration, E2E, or smoke checks as applicable.
3. If a verification step is not run, record the reason, the unverified scope, and the residual risk.
4. Do not claim completion or success without fresh verification evidence.

## Logging Rules

1. Every substantive change must leave a Markdown implementation log under the workspace `_docs` directory.
2. Use the house filename format defined by `%USERPROFILE%\AGENTS.md`.
3. Each log should include at least:
- Overview
- Background / requirements
- Assumptions / decisions
- Changed files
- Implementation details
- Commands run
- Test / verification results
- Residual risks
- Recommended next actions

## Workspace Interaction

1. Treat `%USERPROFILE%\AGENTS.md` as the PC-wide baseline.
2. Project-local `AGENTS.md` files may add stricter or more specific rules, but they must not weaken this baseline.
3. Treat the files under `%USERPROFILE%\_docs\sop` as the canonical SOP set for common, domain, and language controls.
4. Use these shared templates when useful:
- `%USERPROFILE%\Desktop\_docs\templates\AGENTS.project-template.md`
- `%USERPROFILE%\Desktop\_docs\templates\ADR-template.md`
- `%USERPROFILE%\Desktop\_docs\templates\REQUIREMENTS_TRACE_TEST_EVIDENCE-template.md`
- `%USERPROFILE%\Desktop\_docs\templates\IMPLEMENTATION_LOG-template.md`
5. Use `%USERPROFILE%\Desktop\_docs\tools\Initialize-CodexProjectStandards.ps1` to bootstrap a project with the standard file set when needed.
6. Treat `%USERPROFILE%\.agents\skills\milspec-codex-standard\SKILL.md` as the shared cross-tool mirror of this baseline.
7. Treat `%USERPROFILE%\.agents\skills\deepresearch-defense-standard\SKILL.md` as the shared cross-tool deep research baseline for browsing and latest-information work.
8. Keep the tool-specific mirrors aligned when intentionally changing the deep research baseline:
- `%USERPROFILE%\.codex\skills\deepresearch-defense-standard\SKILL.md`
- `%USERPROFILE%\.cursor\skills\deepresearch-defense-standard\SKILL.md`
- `%USERPROFILE%\.config\opencode\skills\deepresearch-defense-standard\SKILL.md`
- `%USERPROFILE%\.gemini\antigravity\skills\deepresearch-defense-standard\SKILL.md`
- `%USERPROFILE%\.gemini\antigravity\global_skills\deepresearch-defense-standard\SKILL.md`
9. Keep the tool-specific mirrors aligned when intentionally changing the baseline:
- `%USERPROFILE%\.cursor\skills\milspec-codex-standard\SKILL.md`
- `%USERPROFILE%\.config\opencode\skills\milspec-codex-standard\SKILL.md`
- `%USERPROFILE%\.gemini\antigravity\skills\milspec-codex-standard\SKILL.md`
- `%USERPROFILE%\.gemini\antigravity\global_skills\milspec-codex-standard\SKILL.md`

## Completion Gate

Before considering work complete, confirm all of the following:

- Code, config, docs, and tests are internally consistent
- Verification evidence exists for the claims being made
- `_docs` contains the implementation log when files were materially changed
- Any formal MILSPEC compliance claim is backed by explicit standard references and evidence
