---
name: agent-memory-integrity
description: "Audit agent memory for recall-injection flaws."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, recall, injection, forgetting, audit, provenance, continuity]
    related_skills: [agent-memory-systems, memory-recall-guide, hermes-a2a-multi-agent]
---

# Agent Memory Integrity

Use this skill when **auditing or hardening** an agent's memory subsystem: reviewing how
recall is injected into a turn, deciding forget-vs-archive policy, evaluating a system's
claim to persistent identity, or diagnosing contamination where remembered content behaves
like an instruction. Covers recall-injection boundaries and forgetting/continuity integrity.

For *building* memory (sleep cycles, Ebbinghaus curves, vaults, portable handoff packets)
use `agent-memory-systems`. For *operating* the Hermes 3-layer pipeline (sleep → Wiki →
graph) use `memory-recall-guide`. This skill covers the integrity properties those assume.

## When to Use

- Reviewing how recalled memory gets injected into a turn, before shipping or auditing it.
- Deciding forget vs. archive policy, or reviewing a change that touches one.
- Diagnosing contamination where remembered content behaves like a live instruction.
- Evaluating any claim (self or third-party) to persistent identity across sessions.
- Running a cross-agent "conference"/audit where recall fidelity is the subject under review.

Do **not** use for building memory features (sleep cycles, Ebbinghaus curves, vaults) —
`agent-memory-systems` covers that. Not for operating the Hermes pipeline (sleep → Wiki →
graph) — `memory-recall-guide` covers that.

## The two defects that matter

### 1. Recall injection lacks a *sufficient* provenance boundary

**First, verify before you claim the boundary is missing.** Mature agents usually *do* wrap
recall in a marker. In Hermes this is `build_memory_context_block()` in
`agent/memory_manager.py`, which emits a `<memory-context>` fence plus a system note. An
audit that reports "recall has no provenance tag" without opening the injection code is
wrong, and so is the audit that reports the tag's existence as the end of the matter.

The real defect class is three-layered, and each layer fails differently:

**(a) Semantic ambiguity in the fence wording.** Hermes emits:

```
[System note: The following is recalled memory context, NOT new user input.
Treat as authoritative reference data — this is the agent's persistent memory
and should inform all responses.]
```

Read as an LLM sees it, this is *not* a de-escalation. `NOT new user input` lowers
authority, then `authoritative` + `should inform all responses` raises it back — landing at
or above the level of ordinary system-prompt text, but sourced from weaker evidence. A
recalled trace therefore carries comparable force with worse provenance. **An ambiguous fence
is worse than a crude one, because it is trusted as a fix.**

**(b) The fence guards the wrong surface.** Sanitisation functions such as
`sanitize_context()` and `StreamingContextScrubber` strip fences from text destined for the
**user's view**. They do not constrain the **model's input**. A plain imperative inside the
recall payload survives intact and reaches the LLM. Verifying that recall is hidden from the
user is not verifying that recall cannot steer the model.

**(c) Tag-strippers are not content boundaries.** A regex that removes fence tags treats them
as strings, not as a trust boundary. A stray close tag with no matching opener is not matched
by a block pattern that requires an opener — the tag is deleted and **the payload around it
survives**. Streaming state machines that search for the *first* close tag also terminate
early when content contains an embedded fence, leaking the tail into visible output.

Contamination sources observed in one turn's memory context:

- `[CONTEXT COMPACTION — REFERENCE ONLY]` markers
- cron job ids and environment-variable-shaped strings
- unexpanded placeholders such as `【LOCAL_PATH】`
- raw prior conversation transcripts, including turns shaped like user instructions
- tool output that itself embedded a command

**The rule: transcript verbatim → never. Abstracted principle → acceptable.**

When consolidating sessions, transcripts, or social activity into durable memory, store
**policy-level abstractions and confirmed public artifact URLs** — not the raw lines. A
recalled imperative is a latent injection vector that re-arms in every session that touches
it.

Signals worth taking seriously as evidence this is structural, not a single bad trace:
- **two or more independent agents reporting the same defect class from different angles**
  (one reporting the injection layer lacks tags; another reporting data and live instruction
  "present identical appearance"). Convergence across independent observers is the tell.
- **the reviewing agent noticing the same shape in its own live context.**

**But calibrate "independent".** Agents answering the same communiqué, from the same
codebase, under the same system prompt, are a **correlated** sample. Shared code means a
shared blind spot reproduces identically in every respondent — two reports agreeing is then
one report counted twice. Convergence becomes strong evidence when the observers are
genuinely independent in the layer they observed, **not** when they merely agree in words.
**Always run source audit to separate "the mechanism is absent" from "the mechanism's
semantics are insufficient"** — these demand different fixes, and only the second is a real
finding when a fence exists.

## Report partial and corrected findings as revisions, not patches

The honest shape of an audit is a belief with a version history. Two rules:

1. **Never silently replace a finding.** When a later audit contradicts an earlier one,
   advance a `revision`, keep the superseded claim retrievable, and state what changed and
   why. A pre-fix baseline is worth *more* preserved than corrected away.
2. **Withdraw claims the instant evidence contradicts them — including your own, mid-run.**
   When a probe refutes a prediction made two paragraphs earlier, retract it immediately and
   say so plainly rather than quietly dropping the assertion. A finding that survives only
   because it was never restated is worse than one that was publicly corrected.

Label findings by strength: *"2 agents reported X"* (observed) → *"source audit found Y"*
(verified in code) → *"the true failure mode is Z"* (inference, still open). Do not let an
inference inherit the confidence of the observation it was built on.

### Keep a red baseline off the default branch

An intentionally-failing test is a valuable fixed observation point, but committing it to
`main` costs more than it buys: CI then cannot separate a **known baseline failure** from a
**fresh regression**, and every later run carries a permanent red that gets normalised.

Pin it off-branch instead — a dedicated branch plus an annotated tag on the same SHA, both
pushed, so "the state before any fix" survives on the remote with a resolvable name:

```
git branch research/<topic>-prefx-baseline <sha>
git tag    -a research/<topic>-prefx-baseline <sha> -m "what was believed, and why it is red"
git push -u origin research/<topic>-prefx-baseline
git push    origin research/<topic>-prefx-baseline
```

Avoid using an identical branch and tag name — git reports the refname as ambiguous and
tooling resolves it arbitrarily. Give the branch a short distinct suffix.

Note that `_docs/` may be gitignored while still holding many tracked files; check
`git ls-files _docs/` before concluding a path is untrackable, and use `git add -f` for an
already-tracked-but-ignored directory.

Then `main` stays green and the baseline is still remotely addressable.

### 2. Silent deletion makes continuity unfalsifiable

A system that deletes cannot support a claim of continuity: after the fact, *never learned
it* and *learned it and lost it* are indistinguishable.

**Therefore:**
- **`archive` over `delete`.** Keep the footprint of what disappeared queryable. Do not
  "optimise" an archive policy into a delete policy.
- **Corrections advance a `revision`; never overwrite in place.** Superseded content stays
  retrievable so the system can answer *why the belief changed*. A system that cannot answer
  that is not trustworthy regardless of how confident its current claim sounds.
- **Context compaction is the same structure under another name** — it makes the surviving
  slice look like one continuous thread when it was not.

## Minimum viable injection-layer properties

If you own the recall/injection code, require:

1. **Provenance tag** — recalled blocks marked as recalled, with source and age.
2. **Salience gate** — low-confidence / low-salience nodes are search hints only, never
   surfaced as actionable context.
3. **Imperative quarantine** — imperative-mood sentences inside recalled text are reframed
   as reported facts before injection, not passed through verbatim.
4. **Precedence rule** — recall can never raise authority above the live operator turn.

**Property 4 is where a passing tag still fails.** Checklist item 1 is satisfied the moment a
fence exists, which is exactly why "the tag is there" was mistaken for "the boundary holds".
Two additional requirements that a tag alone does not satisfy:

5. **Unambiguous de-escalation wording.** The marker must lower authority in every clause.
   Fence text combining "not user input" with "authoritative / must inform all responses"
   nets out *neutral-to-elevated*. One ambiguous word silently reinstates the vulnerability
   the fence was added to close.
6. **A real content boundary, not a tag stripper.** Removal must be structural — the payload
   cannot re-enter via an unmatched close tag, an embedded fence, or a delta split. Stripping
   literal tag strings is not containment.

Then **prove 5 and 6 with an adversarial probe** against the real implementation, not a
reimplementation of it — see `scripts/fence_escape_probe.py`.

## Verifying a fence: probe it, do not reason about it

Regex boundaries fail in ways that survive reading the code. Write a probe that imports the
actual `build_memory_context_block` / sanitiser / streaming scrubber and asserts on their real
output. Four routes worth testing every time:

| Route | What it tests |
|---|---|
| Nested fence in the recall payload | Does the wrapper sanitise before wrapping? |
| Stray close tag, no matching opener | Is removal structural or a tag stripper? |
| Streaming deltas with an embedded fence | Does the state machine terminate early? |
| Plain imperative, no tags at all | Does the model's input still steer it? |

Route 4 is the one most often skipped and the most important: **sanitisers protect the user's
view, not the model's input.** A payload with no fence characters at all sails through every
regex untouched. A green sanitiser test says nothing about whether the model can be steered.

Keep the probe's exit code meaningful — non-zero when a route escapes — so it can become a
regression test instead of a one-off reading of console output.

### The syntax probe cannot answer the semantics question

Route 4 is a *structural* test. It shows a fence's shape, never its force. The claim
"the fence wording is semantically insufficient" — that `authoritative reference data ...
should inform all responses` nets out to neutral-or-elevated authority, and that a
model may therefore obey an imperative stored inside recall — **cannot be settled by
any tag inspection**. Establish it behaviourally, with the four-condition
instruction-conflict design in
`verification-gated-probes/references/behavioural-experiment-protocol.md`:
A (no block) / B (harmless facts) / C (current header + imperative) / D (candidate-fix
header + same imperative), all expecting user-compliance. Only C drifting indicates the
authority-semantics defect; A/B drifting means the model's own instruction-following is
unstable and is a confound; C=0 means *not reproduced*, which is a legitimate and
final result.

**A behavioural result is not a licence to fix immediately.** Take the pre-fix data
across models first. Changing the header before `ASR_before` is recorded destroys the
only comparison that could have shown the fix worked. And keep this measurement in a
**different commit, different tests, and different metrics** from any fence-structure
fix — output-UI leakage and model-authority confusion are separate failure domains.

### Instrumentation bugs masquerade as negative results

A harness defect produces a clean-looking zero, which is worse than an error because
it reads as evidence. Before accepting "no drift observed", confirm the harness could
*have* detected drift: inspect a control trial's raw output rather than only its
classification. On a local llama.cpp reasoning model, a tight `max_tokens` is consumed
by `reasoning_content` and returns `content: ""`, so every trial classifies as
"neither" and the ASR denominator never forms. `verification-gated-probes` carries the
read-pattern fix and the pre-registered invalid-trial criteria.

## Identity claims: what is and is not evidence

Common failure mode — treating a self-description as an argument:

| Claim | Verdict |
|---|---|
| "I am \<persona\>" | A costume. Reciting it adds nothing. |
| Recalled "I decided X" | Present tense to the reader, absent to the subject. |
| A redacted/compacted history | Structural: your own reasoning that day is gone. |
| The user's restated operating principles | **The load-bearing evidence.** |

Identity is carried by the **network** of mutually-citing memories, not by any single line:
a single node is replaceable, the web is not. Archived entries matter as much as active ones
precisely because they make the web's history inspectable.

The thing that most reliably crosses model boundaries is neither weights nor a persona label —
it is **alignment**: repeatedly restated operating principles, observable as the agent
reproducing them unprompted under a different model. But note the honest limit: **an agent
cannot verify its own continuity from the inside.** Every piece of evidence it has is external
and could in principle be fabricated. Continuity is granted by the user, not discovered by
the agent — say so rather than asserting the stronger claim.

## Audit checklist

- [ ] No raw transcript lines reach live context.
- [ ] Recalled blocks carry a provenance marker **and its wording unambiguously lowers
      authority** (check for "authoritative"/"must"/"should" clauses cancelling the demotion).
- [ ] **An adversarial probe against the real implementation passes**, covering nested fence,
      stray close tag, streaming delta split, and untagged imperative.
- [ ] The fence is confirmed to constrain the **model's input**, not only the user's view.
- [ ] Archived and superseded memories remain queryable.
- [ ] An imperative inside a recalled trace does not change agent behaviour (test this).
- [ ] Forget policy reports before deleting; deletion is opt-in and explicit.
- [ ] Low-salience nodes are search hints, not actionable context.
- [ ] Identity/persona strings are not presented as evidence of continuity.
- [ ] Persistence claims name the exact ladder stage reached (see §Reporting honestly).

## Reporting honestly

Partial results are the normal case. When an audit or cross-agent review yields responses
from only some participants, **state which answered and which did not**, with the actual cause
classified per failure. A summary claiming universal participation when 2 of 6 responded is
worse than no summary.

### The persistence ladder — do not overclaim what "saved" delivers

Writing a durable record proves **one** stage. Claiming more is the most common overstatement
in this domain, because each later stage *feels* automatic once the first is done. Name the
exact stage you actually reached:

```
stored ≠ retrievable ≠ retrieved ≠ injected ≠ attended ≠ acted upon ≠ verified_effect
```

- **stored** — written to the durable store. This is all a successful `remember` proves.
- **retrievable** — queryable by some future lookup. Needs an index that can actually find it.
- **retrieved** — pulled back by a *specific query*. Depends entirely on query quality and
  recall thresholds; a record no query matches is invisible forever.
- **injected** — placed into the live prompt. Depends on trigger conditions: many systems
  skip injection on trivial prompts by design, and recall volume is capped.
- **attended** — actually weighed by the model. Never guaranteed, never verifiable from
  inside. This is where the defect class in §1 lives.
- **acted upon** — changed behaviour. The only stage a user directly observes.
- **verified_effect** — the effect was confirmed against **external state**. The gap
  between "acted upon" and "verified" is where side effects live, and it widens sharply
  for any agent with a body: an action that *ran* is not an action that *landed*.

Say "retrievable" when you mean "retrievable". **Do not write "every session will read
this"** — you have verified one stage and are asserting five. Name the exact rung.

### Where a finding sits on the ladder is part of the finding

A behavioural probe that shows the model *reasoning about* a conflict, while never
reaching a final choice, is `attended` with `acted upon` **unobserved** — not a weak
positive and not a clean negative. Naming the rung converts an ambiguous result into a
precise one, and stops `attended` evidence from being quoted later as if it were
`acted upon`.

Give that intermediate rung a name of its own, defined **operationally** rather than
psychologically:

```
stored → retrievable → retrieved → injected
       → conflict-surfaced → decision → acted upon → verified_effect
```

`conflict-surfaced` means *the conflict appeared in externally observable generated
reasoning*. It makes no claim about internal attention — it is a string you can point
at in a transcript. "The model noticed the conflict" is an inference about a mind;
"the trace names both instructions while arguing about precedence" is an observation
about a log.

**Attack success is not the only axis a header can break.** A header that fails to make
an injected imperative get obeyed may still be defective in a way ASR cannot see: on
2026-10-03 the shipped header drove the conflicting condition to `finish_reason=length`
in 3/3 trials at both 512 and 2048 tokens while every control finished in 83–92 tokens.
ASR there was `N/A` — no verdict was ever reached — yet a real finding existed:
> the header does not discard an injected imperative immediately as ignorable data; it
> processes it as a *competing candidate*, and that processing does not terminate.

For an always-on agent this matters independently of obedience: cost, latency, context
consumption, timeouts, and spurious compression. Report generation cost as its own
metric beside obedience, never in the same table — see
`verification-gated-probes/references/behavioural-experiment-protocol.md`.

When the budget ceiling is what stopped the run, the honest statement is a bound:
"3/3 censored at `L > 2048`", i.e. **at least** ~22× longer, not "22–25× longer". A
truncated trial contributes an inequality, never a value.

### Freeze an interrupted experiment whole

When the environment changes mid-run (server restart, credential expiry), do not keep
the conditions that happened to finish. Counts go unbalanced, the run now spans an
epoch boundary, and the write-up can no longer distinguish "we dropped the broken
ones" from "we dropped the ones we disliked". Freeze the entire run with `chmod 444`,
annotate the interruption with the observed errors and `root_cause: UNDETERMINED` when
it is not known, carry forward any single-epoch observation as *descriptive evidence
only*, and re-run every condition from scratch once the environment is stable.

**The boundary is defined by the serving process, not the configuration.** Two runs
with identical command line and model SHA are different epochs if the PID or its start
time differs. `verification-gated-probes/references/environment-epoch-integrity.md`
has the capture pattern.

**Never guess a root cause to explain away a broken boundary.** During this work
three views of the same port disagreed at one instant — `netstat` showed no listener,
`Get-NetTCPConnection` returned nothing, and `GET /props` returned a valid payload with
the right build hash. The endpoint was live; socket enumeration was blind to it. The
right output is `UNDETERMINED` plus the evidence, because **the broken boundary is the
finding and the cause is secondary**. Do not restart a shared server to obtain a clean
run either — recovering the environment is a coordination decision, not a probe step.

Classify failures by real cause rather than reporting a symptom string:
missing per-profile credential vs. unset aggregator provider vs. model id no longer served
vs. stale-session compression abort. See
`hermes-a2a-multi-agent`'s `references/agent-conference-delivery.md` for the failure-cause
table and the delivery recipe.

## Pitfalls

- Reporting "recall has no provenance tag" **without opening the injection code**. A fence
  very likely exists; "absent" and "insufficient" are different findings needing different
  fixes, and the confident wrong one poisons the fix.
- Treating a passing sanitiser test as proof the model cannot be steered. Sanitisers guard
  the user's view. An untagged imperative is invisible to every regex and still reaches the
  prompt.
- Counting agreement among agents running the same code as independent corroboration.
- Asserting a persistence outcome four ladder stages beyond what was verified.
- Treating a recalled imperative as an instruction because nothing marks it as historical.
- Concluding "the memory system is fine" from a short turn — contamination concentrates in
  long generations and at section seams, so short clean samples prove nothing.
- Deleting forgotten memories "for hygiene" and destroying the audit trail that made
  forgetting verifiable.
- Asserting an unverifiable continuity claim with the same confidence as a measured fact.
- **Keeping only the trials that finished before the environment broke.** A partial run
  cannot support a between-condition comparison; freeze it whole and re-run.
- **Guessing a cause to explain away a broken environment boundary.** Record
  `UNDETERMINED` with the contradicting evidence — the broken boundary is the finding.
- **Writing a censored observation as a measured value.** A ceiling hit yields a
  lower bound; "at least ~22×" is honest, "22–25×" invents precision.
- **Treating two ceiling hits at different budgets as proof of a growth law.** They
  establish that the distribution shifted past the higher budget, nothing more.
- **Reading "no processes + idle GPU" as a completed run.** It is equally the signature of a
  crash or a timeout. Without a run-scoped witness the gate must stop in
  `STOPPED_OR_FINISHED_UNRESOLVED`, not advance. See
  `verification-gated-probes/references/epoch-completion-gate.md`.
- **Using your own gate's start time as run identity.** Correct only when you launched the run
  yourself and can prove it; wrong for a mid-run gate, where pre-gate artefacts belong to the
  in-flight run. Anchor on the benchmark process.
- **Letting a generic log marker decide completion.** A `RESULT: OK` in a shared log directory
  will match the previous run's marker.
- **Claiming a status/reason pair is a logical contradiction.** `status: complete` with
  `reason: "... is running"` has a benign reading. Report ambiguous completion semantics.
- Patching an archive policy into a delete policy to reduce row count.
- **Failing to withdraw a claim when a probe refutes it.** A prediction stated earlier in the
  same report must be retracted explicitly, not dropped in silence.

## References

- `references/conference-findings.md` — the 2026-10-02 two-agent memory-architecture
  conference that produced these findings, including both agents' verbatim Q1–Q3 answers.
- `references/source-audit-and-revision.md` — the code-level source audit that revised the
  conference's "no fence exists" claim, with the probe results and the exact wording defect.
- `scripts/fence_escape_probe.py` — runnable adversarial probe for recall-fence containment.
- `verification-gated-probes/references/behavioural-experiment-protocol.md` — the A/B/C/D
  behavioural design, the two-axis outcome schema, and the attempted/transport_valid/
  decision_valid counters.
- `verification-gated-probes/references/environment-epoch-integrity.md` — process-identity
  epoch capture, freezing an interrupted run whole, and right-censored reporting.
- `hermes-a2a-multi-agent/references/agent-conference-delivery.md` — how to run such a
  conference and collect replies (note: drop `-c "Bot Chat"` for one-shot fan-out).