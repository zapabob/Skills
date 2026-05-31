# Plan Mode Reference

Advanced patterns, risk matrices, and templates for plan-mode skill.

## Risk Assessment Matrix

### Impact vs Likelihood Grid

```
              Low Impact    Med Impact    High Impact
High Likely   MEDIUM        HIGH          CRITICAL
Med Likely    LOW           MEDIUM        HIGH
Low Likely    LOW           LOW           MEDIUM
```

### Risk Categorization for Common Tasks

| Task Type | Default Risk | Bump to Higher If... |
|-----------|-------------|---------------------|
| New feature (isolated) | MEDIUM | Touches shared APIs |
| Bug fix (known root cause) | LOW | Fix changes public interface |
| Bug fix (unknown cause) | MEDIUM | Affects data integrity |
| Refactoring | MEDIUM | No test coverage exists |
| Schema/API migration | HIGH | Multiple consumers exist |
| Security fix | HIGH | Involves auth or crypto |
| Dependency update | MEDIUM | Major version bump |
| Config/infra change | MEDIUM | Affects production paths |
| Documentation only | LOW | — |
| Experimental/PoC | LOW | Merging to main branch |

## Advanced Plan Patterns

### Pattern: Parallel Workstreams

When steps can run concurrently, indicate with grouping:

```
Phase 1 (sequential):
  1. [ ] Analyze requirements
  2. [ ] Design architecture

Phase 2 (parallel):
  3a. [ ] Implement frontend component
  3b. [ ] Implement backend API
  3c. [ ] Write integration tests

Phase 3 (sequential):
  4. [ ] Integration testing
  5. [ ] Quality gates
```

### Pattern: Checkpoint-Based Plan

For long-running tasks with intermediate save points:

```
1. [ ] Setup + checkpoint-0 (save baseline state)
2. [ ] Core implementation + checkpoint-1
3. [ ] Edge cases + error handling + checkpoint-2
4. [ ] Tests + verification + checkpoint-3
5. [ ] Final review + cleanup
```

### Pattern: Hypothesis Cascade

For investigation/debugging where each step informs the next:

```
1. [ ] Hypothesis H1: [description]
   → If confirmed: proceed to step 3
   → If refuted: proceed to H2

2. [ ] Hypothesis H2: [description]
   → If confirmed: proceed to step 3
   → If refuted: escalate / broaden search

3. [ ] Implement fix based on confirmed hypothesis
4. [ ] Verify fix
```

### Pattern: ShinkaEvolve Workflow Plan

For tasks involving the evolution loop:

```
1. [ ] Define fitness function (verifier_score formula)
2. [ ] Prepare corpus snapshot (sha256 + allowlist check)
3. [ ] Configure workflow YAML (genome definition)
4. [ ] Run inner loop (analyze → verify → score)
5. [ ] Evaluate fitness and select top individuals
6. [ ] Save run manifest + audit log
7. [ ] Archive artifacts with sha256
```

## MILSPEC Compliance Checklist for Plans

Before finalizing any plan that touches MILSPEC-scoped code:

```
Evidence-first:
  [ ] All decisions in the plan reference code/docs/evidence
  [ ] No step relies on assumptions without verification

Traceable:
  [ ] Plan has a logical ID (PLAN-YYYY-MM-DD-name)
  [ ] Each step maps to specific files/functions

Reproducible:
  [ ] Plan includes seed handling if applicable
  [ ] Steps are deterministic (same input → same output)

Governable:
  [ ] Verification gates included at appropriate points
  [ ] Prohibited operations identified and blocked

Auditable:
  [ ] Progress tracked via TodoWrite
  [ ] Quality gate results will be logged
  [ ] Implementation log entry planned for _docs/
```

## Plan Communication Templates

### Status Update (Mid-Execution)

```
Plan: PLAN-{date}-{name}
Risk: {level}
Progress: {completed}/{total} steps
Current: Step {n} — {description}
Blockers: {none | description}
ETA: {estimate}
```

### Plan Completion Summary

```
Plan: PLAN-{date}-{name} — COMPLETED
Steps: {total} ({completed} done, {cancelled} cancelled)
Quality Gates: {PASS | FAIL — details}
Key Decisions:
  - {decision 1}: {rationale}
  - {decision 2}: {rationale}
Artifacts: {list of created/modified files}
```

### Replan Notification

```
REPLAN: PLAN-{date}-{name}
Reason: {why the original plan changed}
Original steps remaining: {count} → cancelled
New steps added: {count}
Impact on timeline: {none | +N steps}
```

## Estimation Heuristics

| Step Type | Typical Complexity | Notes |
|-----------|-------------------|-------|
| Read/analyze code | Low | ~1-2 tool calls |
| Search codebase | Low-Medium | May need multiple queries |
| Implement small change | Medium | 1-3 file edits |
| Implement large change | High | 5+ file edits, tests |
| Write tests | Medium | Depends on coverage needs |
| Run quality gates | Low | Copy-paste commands |
| Debug/investigate | Variable | Use hypothesis cascade |
| Documentation | Low | Unless complex diagrams |

## Anti-Patterns

### Planning Anti-Patterns

- **Over-planning**: 10+ steps for a simple task. Keep it 3-7.
- **Vague steps**: "Do the thing" — use Verb + Object.
- **No verification**: Skipping test/lint steps for "speed".
- **Rigid plans**: Refusing to replan when evidence contradicts the approach.
- **Invisible progress**: Not updating TodoWrite as steps complete.

### Execution Anti-Patterns

- **Skipping failed gates**: Proceeding despite lint/test failures.
- **Parallel in_progress**: Multiple steps marked active simultaneously.
- **Silent cancellation**: Dropping steps without noting why.
- **Gold-plating**: Adding unrequested features during execution.
- **Scope creep absorption**: Accepting new requirements without replanning.
