# SOP Security

## Scope

Apply this SOP to any work involving authentication, authorization, secrets, tokens, credentials, personal data, external inputs, network exposure, browser rendering, file uploads, command execution, dependency changes, CI/CD, plugins, agent tools, privileged actions, or security-sensitive research.

## Baseline Standards

- PC-wide MILSPECLLMOps baseline
- NIST RMF / SP 800-53 traceability where relevant
- Defensive-use boundary from `SOP-DeepResearch.md`
- Codex Security plugin skills when a scan, threat model, validation, or finding fix is requested

## Required Security Procedure

1. Identify assets, privileges, trust boundaries, attacker-controlled inputs, and failure modes.
2. Preserve least privilege and explicit authorization.
3. Keep secrets out of code, logs, screenshots, reports, and generated artifacts.
4. Validate external inputs at boundaries.
5. Treat model-generated and externally supplied content as untrusted.
6. Make security-relevant failures observable without leaking sensitive data.
7. Review dependency, package, and supply-chain changes before adopting them.
8. Use safe defaults for network exposure, CORS, CSRF, XSS, SSRF, path traversal, injection, deserialization, command execution, and file handling.
9. For agentic systems, consider prompt injection, data exfiltration, unsafe tool use, permission abuse, and trust-boundary breaks.

## Codex Security Routing

- Repository-wide or scoped audit: use Codex Security `security-scan`.
- Threat model creation or update: use Codex Security `threat-model`.
- Diff-focused audit: use Codex Security `security-diff-scan`.
- Confirming a suspected finding: use Codex Security `validation`.
- Repairing a security finding: use Codex Security `fix-finding`.

Follow the selected Codex Security skill exactly. If the skill requires a goal, subagent authorization, scan artifacts, or final reports, treat those as required unless the user narrows the task.

## Prohibitions

1. Do not expose secrets, credentials, private keys, tokens, cookies, session data, or personal contact/payment identifiers.
2. Do not add broad network exposure or privileged access without explicit need and verification.
3. Do not include weaponizable exploit details in user-facing outputs.
4. Do not mark a security scan complete without the artifacts required by the active scan skill.
5. Do not weaken authentication, authorization, logging, validation, or verification to make a change easier.

## Completion Evidence

For security-relevant work, record:

- assets and trust boundaries considered
- selected security SOP or Codex Security skill
- relevant changed files
- validation performed
- residual risk
- any deferred security checks with exact reasons
