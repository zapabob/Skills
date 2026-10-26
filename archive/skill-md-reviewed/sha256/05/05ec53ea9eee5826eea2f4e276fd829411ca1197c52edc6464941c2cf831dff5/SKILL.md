---
name: oss-program-application-strategy
description: "Research and position a user for open-source support programs, grants, maintainer credits, and ecosystem contributor applications."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [open-source, grants, applications, github, maintainer, strategy, deepresearch]
    related_skills: [github-repo-management, github-pr-workflow, github-issues]
---

# OSS Program Application Strategy

Use this skill when the user asks whether to apply to an open-source program, grant, maintainer fund, startup/OSS credit program, or ecosystem initiative, especially when comparing whether to build their own project, fork an existing project, or contribute upstream.

## Goal

Produce a grounded recommendation that improves the user's odds of acceptance by aligning their work with the program's stated intent, public ecosystem signals, and credible proof of maintainer impact.

## Workflow

1. **Separate the program's official intent from community speculation.**
   - Find the official application page, terms, announcement, developer docs, and linked GitHub docs if available.
   - Extract the beneficiary type: maintainer, contributor, project owner, security researcher, startup, educator, etc.
   - Identify concrete benefits and eligible work: credits, subscriptions, security tooling, grants, maintainer automation, release work, etc.

2. **Map the user's options to the program's language.**
   - Rephrase each option as an application narrative, not just a technical project.
   - Prefer narratives that directly reduce maintainer burden, improve security, triage issues, review PRs, ship releases, or help real users.
   - Treat "I built a fork" as weaker than "I maintain or improve a real workflow used by OSS maintainers" unless the fork has clear adoption or differentiation.

3. **Measure ecosystem traction with live evidence.**
   - Use GitHub API/search data where possible: stars, forks, open issues, recent pushes, language, license, contributor activity.
   - Compare upstream projects, known forks, adjacent tools, and the user's candidate project.
   - Do not over-index on stars; also look at issue volume, update cadence, and whether the project has maintainer pain the user can credibly solve.

4. **Check public sentiment and prior art.**
   - Search X, Reddit, Hacker News, developer forums, and project issues for the program/tool name.
   - Capture both enthusiasm and skepticism: duplication, maintenance burden, breaking changes, lock-in, security concerns, or friction.
   - Use this to warn against saturated project ideas and identify gaps with stronger differentiation.

5. **Choose the portfolio shape.**
   - Best shape is often hybrid:
     1. upstream PRs for credibility,
     2. a focused companion repo for differentiated workflows,
     3. a concise application narrative tying both to program goals.
   - Avoid recommending a large fork unless it has a durable reason to exist beyond provider swapping or cosmetic changes.

6. **Give an execution plan.**
   - Suggest 1–3 small upstream PRs the user can land quickly.
   - Suggest one public repo or demo artifact with README, screenshots/logs, workflows, and verification.
   - Draft the positioning paragraph the user can paste into the application.

## Decision heuristics

- **Contribute upstream** when the target project is active, official, widely used, or directly relevant to the program sponsor.
- **Maintain a fork** only when upstream cannot accept the needed design, the fork solves a distinct audience, or the user can sustain compatibility work.
- **Create a companion toolkit** when the user's value is workflow integration, documentation, automation, templates, or domain-specific maintainer operations.
- **Create a new agent/tool** only when existing tools cannot express the user's unique thesis and the user can show adoption or compelling demos quickly.

## Output format

Use a concise but decision-oriented structure:

1. **Short verdict** — one or two sentences.
2. **Evidence table** — official criteria, ecosystem metrics, social signals.
3. **Option comparison** — upstream contribution vs fork vs new repo.
4. **Recommended narrative** — how the user should describe themselves/project.
5. **Immediate action plan** — PRs, repo, docs, demo, application draft.

## Pitfalls

- Do not treat social posts as authoritative eligibility rules. They are sentiment and positioning evidence only.
- Do not recommend a fork just because the program name matches the upstream tool; sponsors often want maintainers using the tool, not competing clones.
- Do not persist transient API/search failures as skill rules. Retry with different search terms or alternate public sources.
- Do not fabricate metrics. If live counts are unavailable, say so and recommend checking before submission.

## References

- `references/codex-for-open-source-positioning.md` — distilled research notes from a Codex for Open Source strategy session: official signals, ecosystem comparisons, public sentiment, and recommended Hermes + Codex maintainer-workflow positioning.
