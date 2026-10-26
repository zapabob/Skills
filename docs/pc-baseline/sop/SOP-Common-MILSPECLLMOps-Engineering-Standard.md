# SOP Common MILSPECLLMOps Engineering Standard

## Purpose

This SOP defines the PC-wide baseline for Codex work that must be consistent with MILSPEC-traceable LLMOps, software engineering discipline, and internet-connected operational control.

## Traceability Baseline

- Development process and documentation: `MIL-STD-498`
- Configuration management: `MIL-HDBK-61A`
- Safety and hazard treatment: `MIL-STD-882E`
- Internet-connected control environment: `NIST RMF / SP 800-53`

## Mandatory Controls

1. Define requirements, acceptance criteria, and residual risks before substantial change.
2. Maintain traceability from requirement to implementation to verification evidence.
3. Prefer small, reversible changes with explicit rollback paths.
4. Enforce version control hygiene, configuration management, and artifact reproducibility.
5. Treat security, safety, reliability, and observability as release criteria, not follow-up tasks.

## Architecture and Design

1. Favor single responsibility, low coupling, clear interfaces, and explicit ownership.
2. Keep modules understandable in isolation.
3. Document design choices that would be expensive to reverse.
4. Reject hidden side effects, silent fallbacks, and unexplained magic values.

## Verification

1. Run the strongest practical verification available for the change surface.
2. No completion claim is valid without fresh evidence.
3. Record skipped verification steps, reasons, and residual risks.
4. Behavioral changes require tests or an explicit rationale for why no automated test applies.

## Logging and Observability

1. Use structured logging where feasible.
2. Preserve enough context to audit user actions, model actions, network calls, and release events.
3. Do not rely on ad hoc console output for production observability.

## Error Handling

1. Do not swallow exceptions or errors.
2. Add context, recover explicitly, or fail decisively.
3. Make failure modes observable and diagnosable.

## Documentation and Evidence

1. Leave an implementation log in `_docs` for every substantive change.
2. Create ADRs for durable architectural decisions.
3. Keep SOP references current when standards evolve.

## Release Gate

Before release or handoff, confirm:

- Requirements and scope are explicit
- Relevant SOPs were applied
- Verification evidence exists
- Rollback or containment exists
- Residual risk is recorded and visible
