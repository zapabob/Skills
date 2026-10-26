# MILSPECLLMOps SOP Design

**Date**: 2026-04-16
**Author**: Codex

## Goal

Define a PC-wide SOP system for Codex work that treats LLMOps as a MILSPEC-traceable operating discipline rather than a vague quality aspiration.

## Structure

1. One common engineering standard:
- `SOP-Common-MILSPECLLMOps-Engineering-Standard.md`

2. Domain SOPs:
- `SOP-LLMOps.md`
- `SOP-MLOps.md`
- `SOP-AIOps.md`
- `SOP-WebApp-Development.md`
- `SOP-Application-Development.md`
- `SOP-Internet-Connectivity.md`

3. Language SOPs:
- `SOP-Python.md`
- `SOP-TypeScript.md`
- `SOP-Rust.md`
- `SOP-Go.md`
- `SOP-CSharp.md`
- `SOP-CPP.md`
- `SOP-C.md`

## Traceability Model

- Software development and documentation discipline trace to `MIL-STD-498`
- Configuration management traces to `MIL-HDBK-61A`
- System safety and hazard treatment trace to `MIL-STD-882E`
- Internet-connected operational controls trace to `NIST RMF / SP 800-53`

## Resolution Order

For any task, apply controls in this order:

1. `C:\Users\downl\AGENTS.md`
2. `C:\Users\downl\.codex\skills\milspec-codex-standard\SKILL.md`
3. `SOP-Common-MILSPECLLMOps-Engineering-Standard.md`
4. Relevant domain SOPs
5. Relevant language SOP

## Design Decision

Keep the common rules in one place, keep domain risk controls separate, and keep language implementation details in individual SOPs. This minimizes duplication and makes future tightening easier without rewriting all language rules.
