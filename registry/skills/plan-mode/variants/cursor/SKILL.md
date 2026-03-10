---
name: plan-mode
description: Create, manage, and execute structured multi-step plans with MILSPEC-grade traceability, audit logging, and fail-closed gates. Use when the user asks for a plan, roadmap, phased approach, or checklist, or when a task has 3+ steps, cross-cutting concerns, risk, or requires coordination. Also triggers on keywords like plan mode, execution plan, task decomposition, phased rollout, or implementation strategy.
short_description: Create, manage, and execute structured multi-step plans with MILSPEC-grade traceability, audit logging, and fail-closed gates. Use when the 
---

# Plan Mode (MILSPEC-Aware)

Structured planning with traceability, verification gates, and audit-friendly progress tracking.
Designed for ShinkaEvolve-OSINT and general multi-step workflows.

## Decision: Plan or Skip?

**Plan** when:
- Task has 3+ distinct steps with dependencies
- Changes touch multiple files/systems
- Risk of data loss, breaking changes, or security impact
- User explicitly asks for a plan/roadmap/checklist
- Architectural decisions with trade-offs exist

**Skip** when:
- Single-step or trivial task
- Answer is a quick lookup or explanation
- Current mode is already working well

## Plan Creation

### Step 1: Scope Analysis

Before creating a plan, gather context:

```
1. Read relevant files / search codebase
2. Identify affected components and dependencies
3. Estimate risk level: LOW / MEDIUM / HIGH / CRITICAL
4. Determine if MILSPEC gates apply (code changes to shinka/ or shinka_osint/)
```

### Step 2: Structure the Plan

Use the TodoWrite tool with 3-7 outcome-based steps:

- **Verb + Object** format (e.g., "Implement retry logic", not "retry stuff")
- Each step should be independently verifiable
- Include a **verification/test step** for non-trivial changes
- Include a **MILSPEC gate step** when modifying core modules

### Step 3: Assign Metadata

For each plan, mentally track:

| Field | Value |
|-------|-------|
| `plan_id` | `PLAN-{YYYY-MM-DD}-{short-name}` |
| `risk_level` | LOW / MEDIUM / HIGH / CRITICAL |
| `milspec_required` | true if touching shinka/ or shinka_osint/ |
| `estimated_steps` | count |
| `rationale` | 1-sentence why this approach |

### Step 4: Publish

Use TodoWrite with all steps. Set only the first actionable step to `in_progress`.

## Plan Templates

### Template A: Feature Implementation

```
1. [ ] Analyze requirements and existing code
2. [ ] Implement core logic
3. [ ] Add error handling and logging
4. [ ] Write/update tests
5. [ ] Run MILSPEC quality gates
6. [ ] Update documentation
```

### Template B: Bug Fix / Investigation

```
1. [ ] Reproduce and isolate the issue
2. [ ] Identify root cause via hypothesis testing
3. [ ] Implement fix
4. [ ] Verify fix + regression test
5. [ ] Run quality gates
```

### Template C: Refactoring

```
1. [ ] Map current architecture and dependencies
2. [ ] Design target state
3. [ ] Implement changes incrementally
4. [ ] Verify behavioral equivalence (tests pass)
5. [ ] Run MILSPEC gates + coverage check
```

### Template D: Research / Exploration

```
1. [ ] Define research questions
2. [ ] Gather evidence (code search, docs, web)
3. [ ] Analyze findings
4. [ ] Synthesize recommendations
5. [ ] Present options with trade-offs
```

## Execution Rules

### Progress Tracking

- Mark step `completed` immediately when done
- Set next step to `in_progress` before starting
- Only ONE step `in_progress` at a time
- If scope changes materially, revise the plan (add/remove steps)
- Never silently skip a step — mark `cancelled` with reason

### Verification Gates

At verification steps, run the appropriate checks:

**For MILSPEC-scoped changes:**
```powershell
# Lint
py -3 -m ruff check shinka/ shinka_osint/ --fix
# Format
py -3 -m black --check shinka/ shinka_osint/
# Tests
py -3 -m pytest tests/ -q --no-cov
```

**For general changes:**
- Run ReadLints on edited files
- Execute relevant test commands
- Verify no regressions

### Fail-Closed Behavior

If a verification gate fails:
1. **Do NOT proceed** to the next step
2. Mark current step as `in_progress` (not completed)
3. Diagnose and fix the failure
4. Re-run the gate
5. Only advance after gate passes

### Hypothesis-Driven Execution (CoT)

For complex steps, use Chain-of-Thought:

```
Hypothesis: [What I expect to happen]
Action:     [What I'll do to test it]
Result:     [What actually happened]
Verdict:    [Confirmed / Refuted / Partial — next action]
```

## MILSPEC Integration

### When MILSPEC Gates Apply

MILSPEC quality gates are required when the plan modifies:
- `shinka/` or `shinka_osint/` directories
- `shinka_mcp_server.py` or `shinka_mcp_skill_hub.py`
- Test files in `tests/`
- Configuration in `pyproject.toml` or `.pre-commit-config.yaml`

### MILSPEC 5 Principles in Planning

| Principle | How It Applies to Plans |
|-----------|------------------------|
| **Evidence-first** | Each plan step has a rationale; decisions cite code/docs |
| **Traceable** | Plan ID + step progression logged in TodoWrite |
| **Reproducible** | Plan templates ensure consistent approach |
| **Governable** | Verification gates block unsafe progression |
| **Auditable** | All steps tracked with status transitions |

### Quality Gate Step (Copy-Paste Ready)

When your plan includes a MILSPEC gate step:

```powershell
py -3 -m ruff check shinka/ shinka_osint/ shinka_mcp_server.py shinka_mcp_skill_hub.py --fix
py -3 -m black --check shinka/ shinka_osint/ shinka_mcp_server.py shinka_mcp_skill_hub.py
py -3 -m pytest tests/test_milspec_requirements_trace.py -v --no-cov
py -3 -m pytest tests/ -q --cov --cov-fail-under=75
```

## Risk-Based Planning

### Risk Level Determines Plan Depth

| Risk | Steps | Verification | Rollback Plan |
|------|-------|--------------|---------------|
| LOW | 3-4 | ReadLints only | Not needed |
| MEDIUM | 4-5 | Lint + tests | Git stash/branch |
| HIGH | 5-7 | Full MILSPEC gates | Feature branch + backup |
| CRITICAL | 6-7 + review | Full gates + manual review | Separate branch + approval |

### Risk Indicators

- Modifying shared utilities or base classes → HIGH
- Changing data schemas or APIs → HIGH
- New dependency introduction → MEDIUM
- Documentation-only changes → LOW
- Experimental/exploratory work → MEDIUM

## Adaptive Replanning

### When to Replan

- Discovery of unexpected dependency or constraint
- User changes requirements mid-execution
- A step reveals the approach won't work
- Estimated effort significantly exceeds initial assessment

### How to Replan

1. Mark remaining steps as `cancelled`
2. Briefly explain why the plan changed
3. Create new steps reflecting updated understanding
4. Resume execution with the revised plan

## Integration with Other Skills

- **milspec-gatekeeper**: Invoke at verification steps for MILSPEC-scoped changes
- **SwitchMode**: If already in Agent mode and planning is needed, switch to Plan mode first
- **TodoWrite**: Primary tool for plan state management

## Examples of Triggers

- "Make a plan to refactor the evidence store"
- "Create a phased approach for adding the new MCP tool"
- "Break down the corpus manager migration into steps"
- "Give me a roadmap for implementing the verifier scoring"
- "Plan the integration of e-Gov API with fail-closed gates"

## Additional Resources

For detailed planning patterns, risk matrices, and advanced templates, see [reference.md](reference.md).
