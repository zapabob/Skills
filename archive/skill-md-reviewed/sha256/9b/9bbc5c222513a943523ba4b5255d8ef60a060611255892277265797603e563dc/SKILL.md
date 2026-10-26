---
name: autonomous-paper-generation
description: Plan and validate AI-assisted scientific paper generation.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Research, Papers, AI-Scientist, Reproducibility, ClaimAudit]
---

# Autonomous Paper Generation

Use this skill to plan and validate AI-assisted scientific paper drafting and experiment automation. It does not establish mathematical correctness, literature priority, or publication readiness automatically; those remain human-reviewed and claim-level audited. Keep provider billing, API access, repository execution, and paper validation as separate concerns.

## When to Use

- When the user wants SakanaAI AI-Scientist to generate experiments or papers.
- When comparing a consumer subscription with an API free tier or paid API.
- When adapting an autonomous research tool to an existing repository.
- When generated output must preserve frozen definitions, proofs, and non-claims.
- When a local AI-Scientist checkout, template, or launcher must be verified.

## Prerequisites

- Confirmed repository root and an actually verified AI-Scientist checkout.
- The checkout's README, launcher help, templates, and dependency manifests.
- Provider credentials configured outside conversation, memory, skills, logs, and source files.
- A bounded research brief, frozen notation, exact assumptions, and claim ledger.
- A review plan for proofs, citations, experiments, and generated LaTeX.

## How to Run

Use `search_files` and `read_file` to inventory the repository before proposing commands. Inspect the local README, launcher, templates, and requirements, then invoke only documented commands through the `terminal` tool. Use `web_search` and `web_extract` for current official pricing, API documentation, model identifiers, and free-tier limits. Use `write_file` or `patch` for controlled drafts, and load `research/mathematical-claim-audit` with `skill_view` when theorem or novelty status is involved.

## Quick Reference

- Repository inventory: `search_files`, `read_file`
- Official provider research: `web_search`, `web_extract`
- Existing skill lookup: `skills_list`, `skill_view`
- Launcher and PoC execution: `terminal`
- Draft and ledger persistence: `write_file`, `patch`
- Proof and novelty audit: `skill_view` → `research/mathematical-claim-audit`
- Independent reasoning: `delegate_task`

## Procedure

1. **Resolve the repository root.** Treat a user-provided relative path such as `vendor/` as relative to the actual repository root. Confirm the root with a filesystem inspection before using any nested path.

2. **Verify the checkout.** Search only the relevant subtree for the AI-Scientist directory, README, launcher, templates, dependency files, and provider configuration. A `vendor/` directory does not prove that `vendor/AI-Scientist/` exists. If the expected checkout is absent, report the observed layout and stop setup planning; never present an untested command as executable.

3. **Read the local contract.** Inspect the checkout's README and launcher help/documentation for exact installation steps, supported providers, model names, flags, output directories, and platform requirements. Do not copy commands from a different version or from a generic memory.

4. **Classify the requested output.** AI-Scientist-style systems generally target an idea → experiment → write-up loop. For a mathematics paper, use the system as a constrained drafting and experiment assistant unless the local template explicitly supports theorem proving. Never treat an ML experiment template as a general mathematical proof generator.

5. **Freeze the research contract.** Before generation, record notation, exact assumptions, quantifiers, allowed conclusions, explicit non-claims, target sections, and required evidence. Maintain separate proof status and novelty status in the claim ledger.

6. **Choose the cheapest validated provider.** Start with a documented free API tier only for a small proof-of-concept. A web subscription and an API key are separate billing/access products unless the provider explicitly links them. Recheck official pricing, model identifiers, rate limits, data terms, and region restrictions immediately before execution.

7. **Run a bounded PoC.** Generate one tightly scoped unit—one definition, theorem draft, proof rewrite, or experiment—not an entire thesis. Limit ideas, iterations, context, and output files according to the verified launcher interface. Preserve command provenance and generated artifacts.

8. **Audit the result.** Check symbols, quantifiers, domains/codomains, constants, citations, experiment reproducibility, and every non-claim. For mathematics, independently verify each theorem and mark unsupported material `UNVERIFIED`.

9. **Escalate based on evidence.** If the free-tier PoC fails on context, reasoning, rate limits, or reproducibility, compare a paid API or subscription using measured quality and cost. Do not purchase or switch providers merely because a model is marketed for research.

10. **Record provenance without secrets.** Store provider/model, date, prompt or input version, repository revision, template, commands, outputs, and human edits. Never store API keys in the ledger, generated source, skills, or logs.

## Pitfalls

- Assuming `vendor/AI-Scientist` exists because a skill or example command mentions it.
- Running repository-relative commands from an unrelated working directory.
- Confusing ChatGPT, Claude, Gemini, or Sakana web subscriptions with API credits.
- Treating an API free tier as unlimited or stable; quotas and eligible models change.
- Launching a full autonomous loop before a one-unit PoC passes review.
- Letting generated prose strengthen a theorem beyond frozen assumptions.
- Treating citation snippets or abstracts as proof of novelty.
- Calling numerical regression a proof of a general mathematical claim.
- Saving credentials in prompts, memory, skills, logs, or source control.
- Writing a provider-specific command or model identifier not found in the verified local documentation.

## Verification

A run is verified only when the repository path, launcher, template, provider/model, bounded command, generated artifact, and review record are all present, and the claim ledger contains no unreviewed strengthened claims.

## References

- Load `references/session-ai-scientist-vendor.md` with `skill_view(name="autonomous-paper-generation", file_path="references/session-ai-scientist-vendor.md")` for the repository-path and provider-selection lessons from the originating session.
