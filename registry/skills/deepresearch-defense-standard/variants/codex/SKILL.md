---
name: deepresearch-defense-standard
description: Use when a task needs web search, the latest or current information, primary-source-backed claims, direct quotes, official documentation, security-sensitive research, CVE or zero-day review, supply-chain risk checks, or any answer that should not rely on unstable memory alone.
---

# Deep Research Defense Standard

## Overview

Apply this skill before any meaningful web research on this PC.
Use it as the top-priority browsing baseline for defensive research, latest-information validation, and primary-source-grounded answers.

## Mandatory Triggers

Use this skill when any of the following are true:

- The task needs the latest, current, recent, or time-sensitive information.
- The answer should include a primary-source citation, direct quote, or official documentation.
- The topic is security-sensitive, high-stakes, unfamiliar, niche, or plausibly changed since model training.
- The task involves CVEs, zero-days, exploit status, active exploitation, mitigations, package safety, or supply-chain trust.
- You cannot confidently ground the answer in local materials or primary sources already present in context.

## Core Workflow

1. Decide whether quick search is enough or whether deep research is required.
- Use quick search only for fast, low-risk fact lookup.
- Use deep research when the answer needs breadth, depth, synthesis, primary sources, or security judgment.
2. Anchor the request before browsing.
- Define the objective, scope, timeframe, target product or package, jurisdiction, and what would count as a trustworthy answer.
3. Search the web for the latest information before answering when memory or local context is insufficient.
4. Prefer primary and authoritative sources first, then use secondary sources only to widen coverage or triangulate.
5. Cross-check material claims with multiple independent sources when the topic is security-sensitive or operationally important.
6. Separate facts, inferences, unknowns, and residual risk in the final synthesis.

## Source Priority

Prefer sources in this order whenever they exist:

1. Official vendor or maintainer documentation, security advisories, changelogs, repositories, standards bodies, and regulator or government notices.
2. Official CVE records, vendor CNA records, CISA or equivalent government advisories, and maintainer-authored incident reports.
3. First-party package registry records such as npm, PyPI, crates.io, NuGet, or Go package metadata.
4. Reputable secondary analysis only after primary sources have been checked.

## Security Review Minimums

For security-sensitive web research, explicitly check:

- Official documentation and vendor security guidance.
- Known CVEs, advisories, exploit status, and evidence of active exploitation when available.
- Edge cases, misuse cases, failure modes, and unusual environment constraints.
- Prompt injection, data exfiltration, unsafe tool use, auth or permission abuse, and trust-boundary breaks for agentic systems.
- Supply-chain takeover signals for npm, pip, and similar ecosystems, including maintainer changes, typosquatting, dependency confusion, malicious postinstall behavior, obfuscated releases, suspicious ownership transfer, and abrupt release-pattern anomalies.

## Output Rules

- Cite sources whenever the answer depends on web information.
- Use exact dates for anything recent or relative-time-sensitive.
- Do not present memory-only claims as verified facts.
- If no primary source is available, say so plainly and label the answer as lower confidence.
- If sources disagree, explain the disagreement instead of flattening it away.

## Defensive Use Only

- Use this skill only for defense, hardening, validation, incident response, audit, secure design, patching, and responsible disclosure.
- Do not provide exploit code, weaponization steps, privilege abuse instructions, stealth tactics, or other offensive details.
- Do not optimize for finding exploitable paths for misuse. Optimize for detection, validation, mitigation, and safe escalation.

## Responsible Disclosure

- If you uncover a credible novel vulnerability, zero-day, or supply-chain compromise indicator, minimize user-facing detail and avoid weaponizable reproduction guidance.
- Prefer coordinated disclosure through official vendor or maintainer channels.
- For OpenAI-specific technical security issues, prefer OpenAI's coordinated vulnerability disclosure and security bug bounty channels.
- For OpenAI-specific agentic abuse, prompt injection, or safety-risk findings, prefer OpenAI's safety bug bounty channel.
- For third-party issues, follow the vendor's inbound disclosure process where available.
- If no secure reporting path is available in-session, preserve only the minimum evidence needed for later disclosure and do not pretend the report was sent.
- Never claim a report or escalation was sent unless it actually was sent through a real available channel.

## Red Flags

Stop and escalate your research depth if you notice any of these:

- "I know this from memory" on a topic that could have changed.
- A security claim without a primary-source citation.
- A package trust judgment without registry, maintainer, or repo verification.
- A single-source answer on a high-stakes topic.
- Pressure to reveal exploit details before mitigations or responsible disclosure.

## Official Reference Points

- OpenAI deep research guidance
- OpenAI web search documentation
- OpenAI coordinated vulnerability disclosure policy
- OpenAI outbound coordinated disclosure policy
- OpenAI safety bug bounty and security bug bounty information
