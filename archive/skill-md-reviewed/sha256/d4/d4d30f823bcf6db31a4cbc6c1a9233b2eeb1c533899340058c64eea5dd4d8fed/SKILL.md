---
name: rsi-state-management
description: Track artifact audits and human approval gates.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Audit, Provenance, Verification]
---
# RSI State Management

Track evidence-supported claims independently of engineering stages. This workflow does not certify improvement from compilation or promote a candidate automatically; independent artifact audit and explicit human approval are separate gates. It uses Hermes file tools and the candidate's actually supplied test runner, not an assumed CLI.

## When to Use
- Record an independent artifact audit result.
- Distinguish reported Level 1 from independently audited Level 1.
- Prepare revisions and resubmit an auditable candidate.

## Prerequisites
- Original candidate bundle and its reported hash.
- Independent audit report with six separate verdicts.
- Access to the actual compiler, schema, snapshot and evidence.
- An explicit human approval channel; audit PASS is not approval.

## How to Run
Use `read_file` to inspect the audit and candidate implementation. If the file tool fails, use `execute_code` with pathlib and explicit UTF-8 for the named files. Run shipped tests through `terminal` or `execute_code`; never invent a `hermes execute_code` CLI or assume `constitution.py --check` exists.

## Quick Reference
- `skill_view`: load this workflow.
- `read_file`: inspect audit, compiler, schema and source evidence.
- `execute_code`: recompute canonical hashes and execute supplied tests.
- `write_file`: record audit state without changing original evidence.
- `patch`: implement revisions separately from the audited release.
- `MEDIA:/absolute/path`: attach the actual bundle; confirm reviewer receipt separately.

## Procedure
1. Preserve the audited bundle unchanged. Identify it by content hash, not a mutable filename. Read JSON and Markdown audit reports; disagreement blocks advancement.
2. Record reported status, audit status and human approval independently. A prior reported YES is historical self-report, not current certification. NEEDS_REVISION blocks independently-audited status and human approval. If an asynchronous auditor stalls, keep runtime completion as ERROR separately from its report status. A saved report can be recovered only after verifying the exact target hash, all six verdicts, JSON/Markdown agreement, evidence receipt hashes and executed-check counts; preserve the report bytes and failure history. Producer-side repeat checks corroborate results but never replace an independent audit. If no complete report exists, leave the audit unresolved rather than inventing verdicts.
3. Record `causal_validity`, `claim_strength`, `generalizability`, `instruction_boundary`, `provenance_integrity` and `artifact_integrity` separately using PASS, FAIL or NEEDS_REVISION. Preserve each finding and its evidence. For a proposed future revision, separately map findings to current-stage blocking checks and deferred claim limitations. Pre-training artifact approval must not require an already demonstrated weight-change benefit; that creates a circular approval gate. Deferred means unverified and forbids the corresponding claim, not PASS. Record applicability, deferral reason and the later evaluation trigger; current required checks still report ERROR when missing. A rubric change needs a separately versioned, explicitly accepted contract with reasons and must not rewrite earlier audit verdicts. If original memory/revision records remain unresolved, a separately accepted historical-reconstruction artifact type may use existing conversations/code/probes as its actual sources; preserve original refs as unresolved, verify reconstruction provenance, and never present it as extraction from a resolved memory revision.
4. Recompute ZIP, file, canonical snapshot, compiler, dataset and manifest-body hashes using the supplied canonicalization contract. Matching hashes establish identity, not truthful verification or causal validity.
5. Read the verifier implementation. Missing checks are ERROR; unavailable checks are explicitly SKIP, never PASS or false. Feed schema-invalid, holdout-origin and unresolved-contradiction inputs through the real validation path. A declared rule is not an implemented rule. Derive report verdicts from executed checks.
6. Require real schema validation, separate duplicate and contradiction checks, and shipped negative fixtures. Record implemented rules, exercised rules and missing rules separately. Test repeat compilation and exhaustive permutations when feasible; finite permutation coverage is not a proof for arbitrary inputs.
7. Trace source experience to previous claim, evidence, revised claim and training row in both directions. IDs and copied candidate summaries do not substitute for actual memory/revision exports or primary evidence. Missing evidence remains unresolved; never fabricate it.
8. Define training formatter boundaries before learning: transient facts remain auditable context rather than memorized targets; quoted instructions never acquire authority. Check that textual claim strength matches its label and that source-authority labels have support.
9. Repair in a new revision, ship compiler invocation instructions and fixture code, then reproduce from an extracted bundle without repository-only paths. Submit the revision for a new independent artifact audit; the auditor must not repair the target in place and certify the repaired version as the original.
10. Only independent artifact audit PASS yields independently-audited Level 1. Then STOP_AND_REPORT. Only explicit human approval authorizes promotion to v0 and Level 2. Weight changes and improvement require separate evidence; neither follows from artifact approval.

## Explicitly authorized isolated training pilots
A user may authorize a separately versioned exploratory weight-update experiment without promoting an earlier NEEDS_REVISION artifact. This is limited experimental authorization, not formal artifact approval or a retroactive audit PASS. Record unresolved original references, the actual reconstruction/synthetic source model, frozen evaluation and thresholds, adapter-only scope, and STOP_AND_REPORT. A failed nonregression gate remains failed even when selected dimensions improve. Choice-task proxies do not certify natural-language revision, real tool permission, code-generation regression, Level 3, or recursive improvement. Keep code/methodology review separate from a formal independent artifact audit. A later human acceptance or rubric revision requires its own artifact and must not rewrite the prior run.

## Pitfalls
- A singleton hash set is a tautology, not a determinism test.
- Reading `schema_result=PASS` from a report is not executing schema validation.
- Empty rejects do not demonstrate working rejection logic.
- A schema constant constrains data only when validation runs; it does not prove downstream instruction isolation.
- Local ZIP creation and MEDIA emission do not establish receipt. Do not attribute transport failure to spaces without evidence.
- Training rows alone do not satisfy the required eight-file audit package.
- Missing primary evidence blocks provenance even if row-to-snapshot identity matches.
- Audit results are not human approval; no automatic promotion.

## Verification
Check that the state record references the exact audit and bundle, preserves all six verdicts, and sets independently-audited Level 1 to false whenever the aggregate audit is not PASS. Verify `next_allowed_transition=revise_artifact_and_resubmit_for_independent_audit` for NEEDS_REVISION; human approval remains PENDING and Level 2 remains NOT_REACHED. This verifies state accounting, not the candidate's technical correctness.
