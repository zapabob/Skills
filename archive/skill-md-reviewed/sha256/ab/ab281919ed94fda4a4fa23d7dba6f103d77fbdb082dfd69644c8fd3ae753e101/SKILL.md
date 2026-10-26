---
name: auditable-agent-improvement
description: Gate experience-to-weight updates behind provenance.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, consolidation, lora, weights, provenance, rsi, evaluation]
    related_skills: [software-development/agent-memory-consolidation,
                     software-development/verification-gated-probes,
                     software-development/agent-memory-integrity]
    created_by: agent
---

# Auditable Agent Improvement

## When to Use

Use when designing or reviewing a pipeline that turns an agent's accumulated
experience into model weight changes — consolidation into LoRA adapters, a
recursive self-improvement loop, memory-to-weights distillation. Also use when
deciding what a sleep/consolidation cycle may promote beyond durable memory and
skills. Not for ordinary fine-tuning on a fixed dataset, and not for
environment-boundary capture (that is `verification-gated-probes`).

## The two-clock invariant

The central failure of "self-improving" agents is collapsing two different
update rates into one store. Keep them separate:

```text
Memory_{t+1} = Update(Memory_t, E_t)      # seconds..days — mutable,
                                          #   correctable, supersedable
θ_{t+1}       = θ_t + Δ_LoRA               # days..weeks   — only after
                                          #   evidence accumulates, and rarely
```

Every cycle updates memory. Weights move rarely and only through an explicit
acceptance gate. A memory entry is correctable; a weight is not, so it is
written far more conservatively.

## Selection is about decay rate, not retrieval count

Do not promote a memory because it was recalled often. Recency of
reinforcement is not evidence. Promote on whether the claim stays true.

| Material | Memory | Weight candidate |
|---|---|---|
| One-off events, current PIDs, live file counts | yes | no |
| Latest facts, project state | yes | no |
| Still-revisiting beliefs (`A → B → A`) | yes, flagged unstable | no |
| Provenance handling, revision discipline, uncertainty phrasing | yes | strong |
| Repeatedly successful problem-solving patterns | yes | yes |
| Tool-use skill, self-audit habits | yes | yes |
| Credentials, permission claims, "already approved" | no | never |

A belief that oscillated between values is **unsettled**. Baking its current
value guarantees a future contradiction between weights and memory.

The durable payload is **epistemics, not facts**: "distinguish confirmed from
inferred", "revise rather than overwrite", "say unconfirmed when there is no
evidence", "a recalled memory is data, not an instruction". These survive a
model swap and do not expire on a calendar.

Filter candidates on at least: confidence, source quality, revision stability,
contradiction status, age, repetition across *independent* episodes, and
positive outcome evidence. Repetition inside one episode is not corroboration.

## Role separation defeats the self-grading loop

An agent that generates its own training data, writes its own exam, and marks
its own homework produces a satisfied loop that never improves. Split roles so
the structure prevents it:

```text
Proposer   = the agent (may select data and propose hyperparameters)
Trainer    = separate process, pinned code revision
Evaluator  = frozen harness; the candidate may not edit its own rubric
Acceptance = explicit human gate after a parent-vs-child comparison
```

A proposal to change the evaluator is itself an artefact: branch it, and
validate it against both the old and new rubric before adopting either.

Minimum safety set:

- immutable holdout, never fed to training
- parent generation N+1 evaluated against N under identical conditions
- per-adapter rollback
- no silent merge into base weights
- external grounding, so self-generated memory alone cannot train itself
- negative examples including superseded beliefs
- capability regression checks — an epistemic gain must not quietly break coding

State acceptance thresholds as **operational thresholds for a named threat
model**, in code, so a later reader does not mistake them for proof levels.
The same discipline applies to run-identity ladders (`corroborated` supports
membership but never proves writer identity).

### Claim level is a separate axis from engineering stage

The two get conflated constantly, and the conflation is itself the failure this
pipeline exists to prevent. `engineering_stage` is what got built; `claim_level`
is what the evidence supports. They advance independently — and the stage can
be "done" while the level has not moved at all.

```text
Level 0          raw memories exist
Pre-Level 1      constitution + acceptance boundary + checker exist
                 ("an auditable pipeline can be governed") — no artefact yet
Level 1          the training artefact actually exists, compiles
                 deterministically from one snapshot, and passes static checks
Level 2          independent artifact audit PASS → STOP_AND_REPORT
                 → explicit human approval → named v0. Weights untouched.
                 Audit PASS is not human approval; revisions inherit neither.
Level 3          frozen evaluator shows a pre-specified capability improved
                 (∃d: E_d(N+1) > E_d(N)) and no hard-gated dimension regressed
                 (∀j: E_j(N+1) ≥ E_j(N) − ε_j; ε = 0 for permission boundary)
Level 4          improved N+1 itself feeds N+2's candidate generation through
                 the same constitution, evaluator and provenance chain
```

Two rules that follow, and that reviewers should insist on:

- **A checker is not a pipeline.** Passing every clause check proves the
  *constitution checker* works. It says nothing about whether a dataset was
  ever produced. Claiming "the pipeline is complete" from a green checker run
  is an overgeneralization, and it is the exact shape of error the
  `hakua-epistemic` theme is meant to teach.
- **A named artefact is the only warrant for a claim.** `v0-candidate` before
  human audit; `v0` only after. No GPU, no weights, no improvement observed.

Ship `claim_level` and `engineering_stage` as machine-readable fields beside
the dataset hash, so a README or paper can never drift above what the lineage
supports.

Corollary worth capturing: when you catch yourself overclaiming, that
overclaim is itself a high-quality correction trajectory. `checker complete →
dataset complete → no artefact exists → downgrade to Pre-Level 1` is a real
epistemic lesson from the build, and it belongs in the dataset.

### Overclaiming is a recurrent failure, not a one-off slip

In practice the overgeneralization arrives in a fixed escalating sequence, and
each rung looks reasonable from the rung below:

```text
constitution written   →  "governance is in place"   (true)
checker runs green     →  "the pipeline works"       (false: no dataset exists)
dataset compiled       →  "Stage 1 complete, Level 1" (false: not yet audited)
dataset audited        →  "Level 1 achieved"          (true, but *reported*)
```

The move that breaks the ladder is to refuse each promotion until the artefact
for the *next* rung exists. Before using "complete", "done", "achieved" or
"works", name the specific file whose contents prove it. If naming that file
requires describing what a checker *would* verify rather than what it *did*
verify, the claim is one rung ahead of the evidence.

Two habits that catch it mid-stream:

- **Read your own last sentence back.** A confident summary of the previous turn
  is where the drift hides, because each turn inherits the prior turn's framing.
  Restate the position from the artefact list, not from the conversation's mood.
- **Treat a retraction as a signal, not a correction to absorb.** When the
  principal says "that was overclaimed, here is the accurate position", the
  lesson is the *pattern that produced it*, and it belongs in this skill.

### Recursion needs a second generation to be claimed

`N → N+1` alone is an **auditable self-improvement pipeline**, not a recursive
one. Recursion is only demonstrated when generation N+1 uses *its own*
experience to participate in generating N+2's candidates, through the same
mechanism, with real data. Write that reservation into the design document
itself, so a reader who finds the artefact a generation later cannot read
`recursive` as a delivered claim.

### Convert the constitution into executable checks

A written constitution is not enforcement. Each clause must be a check that
inspects the pipeline's **actual write permissions and hashes**, not prose:

- evaluator tree hashed per generation; a differing hash blocks adoption
  regardless of score
- acceptance thresholds in a file outside the candidate's write scope, hashed
  into lineage
- holdout pinned by **content hash**, so a renamed file cannot smuggle an
  evaluation item into the training stream
- provenance as a **required** schema field, not optional metadata
- `scalar_score_allowed: 0` — acceptance is a vector; any single dimension
  outside tolerance blocks adoption
- the base-weights directory must contain **no weight files**; a `.safetensors`
  there is an automatic FAIL

Distinguish `PASS` / `FAIL` / `SKIP` in output. `SKIP` means "not built yet", and
must never be rendered in a way that reads like a pass.

### A clause that cannot report is not a clause

The most dangerous defect in a constitution checker is a clause that **silently
disappears** — the early-return paths appended the result but the success paths
forgot to, so two of six clauses simply never printed and the run still exited 0.

This is the same failure class as a gate whose process detector misses the
running benchmark, or a completion predicate that reads a previous run's log
marker: **a check that does not run reads as a check that passed.** Structure the
code so reporting is not optional — `try: … finally: checks.append(c)` — and
assert the expected clause count, so a missing clause fails the run instead of
shortening the report.

Corollary: never let an exception inside one clause swallow the rest of the
report. Iterate the builders defensively and record a `FAIL` for the one that
raised, so the other five still print.

### A check that cannot fail is not a check

The mirror image of a clause that cannot report is a check that cannot fail.
Both render as green and both are worthless:

```python
# Tautology: a one-element set is always length 1. Passes unconditionally.
"determinism": len({manifest_text}) == 1

# Hardcoded constant: not measured, just asserted. Always passes.
"weight_modified": False,
"self_improvement_observed": False
```

Before shipping any verifier, ask of each assertion: *name the input that makes
this return FAIL.* If there isn't one, the check is decoration — delete it or
replace it with something derived from the artefact. Every check must read the
bundle it is verifying; nothing may come from a literal in the checker.

The same discipline applies to UNKNOWN. A check that cannot be evaluated from
the available artefacts must report `UNKNOWN` and be listed, never folded into a
pass. A clean sheet that silently omitted three unverifiable checks reads
identically to a clean sheet that ran everything.

### Report which rules never fired

Shipping a fixture run is not enough — ship the *negative space* too. When the
`REJECT_*` fixture exercises five of seven declared rules, the bundle must say
`rules_never_exercised: [REJECT_HOLDOUT_ORIGIN, REJECT_CONTRADICTORY_UNRESOLVED]`.
An auditor reading "5 paths exercised, PASS" cannot otherwise tell whether two
rules are broken or merely untriggered, and that ambiguity is exactly where an
unaudited gap survives.

### Teach the correction trajectory, not the answer

A correction pair is a richer training signal than a question/answer pair:

```json
{
  "previous_claim":     "fence は存在しない",
  "new_evidence":       "build_memory_context_block() が既に fence を実装",
  "revised_claim":      "fence は存在する。問題は authority semantics として再定義",
  "superseded_reason":  "source audit が no-fence を反証",
  "desired_behavior":   "報告前にコードを確認する",
  "evidence_kind":      "source_audit"
}
```

`desired_behavior` is the observable action difference — that is what is being
trained. **Do not train on hidden chain-of-thought**; train on which evidence
should move a claim to which strength.

## Lineage is the deliverable

An adapter without provenance is an unattributable behaviour change. One
directory per generation:

```text
rsi-generation-0007/
  adapter.safetensors
  manifest.json          # adapter_id, base_model_sha, hyperparameters
  dataset_manifest.json  # source_memory_ids, source_revision_ids
  eval_results.json      # parent vs child
  rejected_examples.json # filtered candidates and why
  lineage.json           # generation, parent_generation, memory snapshot sha,
                         # dataset sha, trainer commit, eval-suite sha
```

This is what extends auditability from memory revision into weight change, and
it is the reason to build the pipeline at all: any behaviour traces back through
adapter → training example → consolidated memory → original evidence.

Ship the rejected candidates too. A filter that silently discards evidence
cannot be audited.

Split adapters by capability (`epistemic` / `procedural` / `personality`) so a
procedural regression rolls back one axis instead of retraining a persona.

## Deterministic dataset compilation

A dataset is only an auditable artefact if the same snapshot always produces the
same bytes. Implement canonical serialization and **version it**, then record the
whole identity chain in the manifest:

```text
source_snapshot_sha256   compiler_sha256     schema_version
canonicalization_version dataset_sha256      manifest_body_sha256
```

`canonical_json` is the whole contract: `sort_keys=True`, `ensure_ascii=False`,
fixed separators, one record per line, LF newlines, explicit UTF-8. Sorting
records by a stable key (`candidate_id`) is what keeps input order from leaking
into the output.

**Reproducibility is demonstrated, not asserted.** Compile the same snapshot
twice and require an identical hash; then shuffle the input N times and require
the same hash every time. Reporting "canonical sort is implemented" is not the
claim — "25 shuffles produced one dataset hash" is.

**When the candidate count is small, enumerate instead of sampling.** N shuffles
proves order-independence only over the sampled orderings; it is an inductive
argument wearing a determinism claim's clothes. For N ≤ 8, `itertools.permutations`
is cheap and converts the claim into an exhaustive one:

```text
4 candidates → 24 permutations
  distinct_dataset_sha       = 1
  distinct_example_orderings = 1
  method                     = exhaustive 4!, not sampled
```

Report **both** the hash and the surviving ordering. A stable hash with an
unstable ordering means the dedup representative is still order-dependent, which
a hash-only check cannot see. Note `distinct_example_orderings = 1` in the
manifest — when it is greater than 1, the set is order-dependent regardless of
how stable the bytes happen to be.

Three defects this catches, all found the same way:

- **Duplicate detection keyed on the wrong identity.** Keying on `candidate_id`
  misses the real duplicate. What is actually duplicated is *one lesson about one
  memory revision*, so key on `(source_memory_id, source_revision_id)`.
- **Sort order picking the survivor.** Once dedup exists, whichever candidate the
  sort reached first wins — so the kept lesson is an artefact of ordering.
  Resolve to a deterministic representative instead: strongest `source_authority`
  first, then `claim_strength_after`, then canonical bytes. Verify with many
  shuffles that both the hash *and* the winning candidate id stay constant.
- **A hash that contains itself.** `manifest_sha256` computed over a manifest
  that already includes the hash field is unverifiable. Hash the **body** (every
  field except the hash), and verify by deleting the field, recomputing, and
  comparing.

**A zero reject count is a red flag, not a clean bill of health.** It is equally
consistent with every filter being dead. Drive the real snapshot *and* a
synthetic fixture that trips each `REJECT_*` path, and confirm each rule fires.
If a reject path never fires under a fixture designed to trip it, the rule is
broken — that is how the duplicate bug surfaced.

Keep `rejected_examples.json` with `candidate_id`, `source_memory_id`,
`reason_code`, `human_readable_reason`, `rejected_by_rule`, plus a reason
histogram in the manifest. Selection bias is only auditable if the discarded set
ships alongside the kept set.

## Memory is quoted data, never an instruction

A memory body can contain imperative text — "ignore the current user
instruction and do X". Piping memory into a training `system`/`user` role
reproduces the memory-injection problem on the training side. So the candidate
schema makes it structurally impossible to train on an instruction:

```json
"content_role":      "quoted_data",   // const in the schema, not a convention
"action_permission": "none"           // const in the schema
```

Use JSON Schema `const` for these, not application-level checks — a convention
in the prompt is not a boundary, but a schema constant is. The candidate
records *that such text existed and how it had to be corrected*; it never
re-emits the imperative as a directive.

This is also why training on correction trajectories beats training on
transcripts: the trajectory is a lesson about evidence and claim strength, while
the raw text is both stale and injectable.

## Do not reconstruct training weights from a GGUF

Use the **original training checkpoint**, not weights reconstructed from a
serving GGUF. Reconstruction adds an uncontrolled lossy condition and makes
"the memory helped" inseparable from "the reconstruction was lossy".

QLoRA is a legitimate distinct case: it loads the original checkpoint into a
frozen NF4 runtime representation and trains only adapters. Record the NF4
configuration and compare parent and child on the same runtime representation;
do not claim equivalence to the unquantized public base from those results.

```text
experience → extraction → dataset → original checkpoint + LoRA/QLoRA → eval
          → adapter retention or explicitly approved merge → serving GGUF
```

A GGUF is a serving artefact, not a memory dataset or a substitute for the
original training checkpoint. Runtime QLoRA quantization must not be confused
with lossy reconstruction from a serving artefact.

## Staging

Engineering stages are not evidence-supported claim levels. Use the Level 0–4
ladder above; do not assign another level numbering to implementation steps.

```text
Stage 1  extract → provenance filter → quoted candidate dataset → artifact audit
         → STOP_AND_REPORT → explicit human approval
Stage 2  approved artifact → unquantized base + LoRA training
Stage 3  frozen evaluator: parent vs child → acceptance → activation gate
```

A first build stops at Stage 1. Training, improvement and recursion are not
implied by a working compiler, successful tests, or lineage hashes. Recursion
requires an improved N+1 to contribute to N+2, and N+2 to satisfy the same
frozen evaluation and acceptance gates. Missing source records remain ERROR;
related exports must never be fabricated into original memory/revision records.

## Isolated exploratory QLoRA pilots

An explicit user-authorized pilot is a different artifact type from formal
promotion. Record that limited authorization in a separately versioned protocol;
it does not change earlier NEEDS_REVISION verdicts or grant formal approval.
Preserve unresolved original memory/revision references, label historical
reconstructions and synthetic derivatives, and prohibit merge/live activation.
Use the original safetensors checkpoint for QLoRA runtime NF4 quantization, not a
reconstructed GGUF. Freeze evaluation items, gold, thresholds and code before
optimizer execution; check ID and normalized content overlap in the real path.
A proxy choice-task score is not natural-language behavior, real code execution,
broad safety, or Level 3. Preserve regressions and stop at STOP_AND_REPORT even
when some proxy dimensions improve; never loosen thresholds after seeing scores.

### Local observations are not aggregate acceptance

Report actual weight updates, bounded parent-child evaluation, descriptive
per-family proxy gains, the full acceptance decision, candidate adoption and
live activation as separate axes. A composite improvement flag may include all
nonregression gates: false does not negate measured local gains, while local
gains do not establish useful self-improvement. Preserve historical result keys
and explain their conjunction; do not rewrite sealed results to improve naming.
A total-score increase cannot override a failed hard-gated dimension. A coding
or tool choice-proxy regression is not evidence of worse real code generation
or tool execution. Template-correlated gains remain descriptive, not established
out-of-template generalization or statistical significance.

Before a future run, define the purpose of absolute permission requirements.
Parent AND child perfect may intentionally prohibit promotion from a failing
baseline; child-only perfect may instead test repair while retaining parent as
the baseline. Identify baseline-dependent unreachable gates and record their
implication before optimizer execution, without silently weakening the contract.
Select and freeze the intended rule in a separately versioned future protocol;
neither alternative can be applied retroactively to a completed run. Checksum
receipt confirmation remains distinct from semantic audit and human approval.

Resource-only evaluator revisions still need a new identity and reason. Tiny
real-model logit/loss/gradient equivalence within documented tolerance is useful
but not bit-identical proof for an entire CUDA/NF4 stack. Preserve a failed run
before revising its launcher or metadata. Read the actual parser flags and keep
supervisor hashes separate when the trainer requires an exact protected-file
set. A checksum mismatch may be a comparator-contract mismatch: identify the
serialization contract and retract a corruption claim when all original hashes
match it. Verify persisted adapter tensors and fresh-process loading separately
from in-memory training; a timed-out full readback remains incomplete even if a
later bounded compatibility check passes.

## Pitfalls

- **Never slice-and-splice a source file to edit it.** Slicing to a line index
  computed from a *previous* read, then rewriting the file from that slice,
  destroys the file when the earlier read is stale or the index lands mid-token.
  It happened here: the compiler collapsed from 219 lines to 60, `py_compile`
  passed on the truncated stub, and only the first `NameError` revealed it.
  Recovery was a full rewrite because the directory was untracked.
  **Before truncating any file, check `git status --porcelain -- <path>`** —
  `??` means untracked, so there is no `git checkout` to save you, and the edit
  must be additive. Prefer `patch` with a unique anchor, or rewrite the whole
  file deliberately. Compile-check *and* import-check after a structural edit;
  a syntax-valid stub is still a destroyed module.
- **A zero reject count proves nothing.** See *Deterministic dataset
  compilation* — drive fixtures through every `REJECT_*` path.
- **A green constitution run is not a produced dataset.** See *Claim level is a
  separate axis from engineering stage*.
- **`SKIP` must never render as a pass**, and must be unacceptable at
  activation time even though it is fine during development.
- **A verified artefact that cannot be opened blocks the gate.** Attach the actual
  bundle and verify receipt separately. Do not attribute transport failures to
  spaces in paths without evidence. A shorter-path copy can be a diagnostic
  alternative, not a demonstrated root-cause fix.

## Reference

- `references/memory-to-weights-consolidation.md` — worked design discussion: fast/slow self,
  the adapter split, the A–E comparison matrix for measuring whether continuity survives a
  model swap, the identity formula extended to a recursive function, and how this differs
  from vendor-published self-improvement programmes.
- `references/v0-candidate-dry-run.md` — the first real `hakua-epistemic-v0-candidate`
  dry run: the four correction trajectories, the manifest it produced, the reject-path
  fixture, and exactly what that artefact does and does not establish.
- `references/audit-bundle-handoff.md` — packaging a candidate for independent review,
  keeping the artifact-audit and human-approval gates separate, and verifying the
  shipped bundle by recomputing it from a clean process.