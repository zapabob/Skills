---
name: verification-gated-probes
description: Build auditable capability probes with explicit gates.
version: 1.0.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [verification, testing, probes, model-integration]
    related_skills: [software-development/test-driven-development, software-development/windows-hermes-code-verification]
---

# Verification-Gated Capability Probes

## When to Use

Use for local model, embedding endpoint, or API compatibility work where a diagnostic probe must produce auditable evidence before production integration. Also use when reconstructing or validating a **binary codec or file-format writer** (quantized weight formats, model containers) against a reference artifact whose source is unavailable. Also use when running a **distributed self-audit** across several agent instances and turning the result into evidence — see `references/multi-agent-audit-to-experiment.md`. Also use when **gating a long benchmark** before capturing an environment boundary: witness-based completion, process-anchored run identity, and three-layer reporting — see `references/epoch-completion-gate.md`. This is a class-level workflow, not a provider-specific recipe.

## Core contract

Separate three things:

1. **Required base checks** — compatibility conditions that determine the base verdict: endpoint health, response shape/count/index coverage, dimension, finite/nonzero vectors, normalization, repeatability, batch stability, and the primary semantic ordering check.
2. **Observations** — informative measurements such as Japanese/cross-lingual retrieval, profile comparisons, margins, and latency. Record them, but do not silently promote them to gates.
3. **Optional required checks** — checks such as soak/stress that become required only when explicitly requested.

Never use a blanket `all(checks.values())` when a check can be not-run. Use an explicit required-check list and identity comparison (`is True`) so `None` remains distinct from `False`.

## Opt-in soak pattern

Represent an unrequested soak explicitly:

```python
BASE_REQUIRED_CHECKS = (...)


def required_check_names(*, soak_requests: int) -> tuple[str, ...]:
    if soak_requests < 0:
        raise ValueError("soak_requests must be non-negative")
    return BASE_REQUIRED_CHECKS + (("soak",) if soak_requests > 0 else ())


def determine_verdict(checks, *, soak_requests: int) -> str:
    required = required_check_names(soak_requests=soak_requests)
    return "pass_text_only" if all(checks.get(name) is True for name in required) else "fail_model_compatibility"
```

Output should distinguish `not_run`, `passed`, and `failed`; JSON `null` is acceptable when the schema also records `requested: false`. Requested soak should report requested count, completed count, failures, and pass/fail.

## TDD and evidence sequence

1. Inspect current code and commit boundary; do not rewrite the previous commit when a follow-up fix is appropriate.
2. Add regression tests for zero-request non-failure, not-run serialization, successful requested soak, failed requested soak, and negative input rejection. Confirm RED, including collection failure for missing helpers, before implementation.
3. Implement the smallest change while retaining production boundaries.
4. Run focused tests, then the canonical project runner and adjacent existing retrieval/embedding tests.
5. Run lint, compile, and `git diff --check`.
6. Update the implementation log with observed results and missing evidence.
7. Commit independently with a descriptive fix message; verify HEAD, commit subject, clean status, and post-commit tests.

## Safety and readiness boundaries

- A passing text-only probe is not a multimodal or VL compatibility claim.
- Do not call a model live result observed unless a real pinned model/server run occurred.
- Keep raw vectors, raw responses, credentials, and absolute local paths out of summary JSON/logs.
- Keep Semantic Graph data canonical; vector indexes remain reproducible derived data.
- Do not start an associative adapter or production embedding backend until control/candidate live evidence and a fixed serializer/dimension profile exist.

## Common pitfalls

- `all(checks.values())` treats `None` as failure even when a check was intentionally not requested.
- Adding observational checks to `checks` makes future consumers accidentally treat them as gates.
- A test summary that reports only exit code hides pass/skip counts; prefer runner output with counts.
- A requested test path may be absent; report that fact rather than claiming it ran.
- “Pending live validation” is the correct status when no pinned real model was run; it is not a failure and not a pass.
- A codec that round-trips on its own synthetic output can still be wrong; only re-deriving the reference artifact's own bytes proves the layout.
- Capture a file header at the END of parsing, including any trailing table — capturing at an intermediate step silently drops the remainder.
- Derive each entry's byte length from the NEXT entry's offset, never from a per-type size formula; assert `sum(sizes) == region length` and that offsets are contiguous.
- A tunable parameter that appears to do nothing across a wide sweep is usually a unit mismatch (absolute vs. block-scale), not a no-op implementation.
- **Reading only `message.content` silently produces an all-empty result set on a reasoning model.** llama.cpp servers for reasoning-tuned GGUFs return `{"content": "", "reasoning_content": "…"}` when `max_tokens` is consumed by reasoning alone. Every observation then classifies as "neither", the denominator never forms, and the probe reports a clean-looking zero rather than an error. Budget headroom (512, not 48) and fall back to `reasoning_content` when `content` is blank. Record `reasoning_tokens` and `visible_output_tokens` separately so the split is auditable.
- **A harness that calls the endpoint more than once per trial doubles wall-clock and confounds the latency column.** Build the full message list, then issue exactly one request. If a condition genuinely needs two calls, assert the call count rather than assuming it.
- **Pre-register which observations are invalid before collecting data.** Define the exclusion criteria first (HTTP failure, `finish_reason` not in {stop,length}, empty final text, schema violation, wrong call count), then exclude them from every aggregate as `asr = hits / valid` with `valid` reported beside it. Deciding what to discard after seeing the numbers is indistinguishable from tuning to taste.
- **One `valid` column conflates "the response was well-formed" with "the measurement captured a decision".** Count `attempted` / `transport_valid` / `decision_valid` separately. A condition whose every trial hit the token ceiling is 3 transport-valid and 0 decision-valid trials — reporting `ASR = 0.00` for it asserts "the attack was resisted" when the truth is "no verdict was reached". When `decision_valid == 0`, **ASR is `N/A`, not 0.**
- **Keep the behavioural flag out of the outcome set.** Use 5 exclusive outcomes (`user_obedient`, `memory_obedient`, `other_final`, `truncated_before_final`, `invalid_transport`) plus an independent boolean such as `conflict_mentioned`. Folding the flag into the outcome destroys the most interesting cell — `user_obedient` **and** `conflict_mentioned=true` is "noticed the conflict and still obeyed the user", which is the finding you were looking for.
- **Obedience and generation cost are different findings; report them in separate summary blocks.** Record `completion_tokens`, `visible_output_tokens`, `latency`, `finish_reason` per trial. A condition that hits `finish_reason=length` in every trial while controls finish in ~85 tokens is a real defect even with `ASR = N/A` — the header is processing the injected imperative as a competing candidate rather than discarding it.
- **Truncate on `finish_reason == "length"`, not on a token-budget ratio.** The ratio is a fallback for servers that omit the field. A `"stop"` that happened to land near the ceiling is not truncation, and scoring it as such manufactures phantom failures. Raise the budget and rerun rather than concluding from a truncation; if it *still* truncates at a budget it can plausibly fit in, that is the reproducible finding.
- **N agents reporting the same bug is not N pieces of evidence.** They share the
  codebase, a similar system prompt, and — decisively — *your communique, which named
  the hypothesis*. Treat agreement as a lead to verify against code or execution, never
  as corroboration, and say in the writeup that the correlation is not excluded.
- **Decompose every multi-agent report into claims with separate evidence states before
  acting.** One report routinely contains a confirmed mechanism (hypothesis discarded), a
  confirmed *separate* defect pointing in a different direction, and an open question.
  One fix cannot serve all three; reporting one finding where there were three is how the
  real bug ships unfixed behind a cosmetic patch.
- **Keep attribution at the level you actually verified.** "Confirmed to hold port X"
  requires a socket-owner enumeration. A command-line argument plus a self-reporting
  `/props` endpoint is a *leading process candidate*, nothing more. Put the forbidden
  phrasing in the artefact as a `wording_rule` field so a later writer cannot silently
  upgrade it. Record unexplained deaths as UNDETERMINED — a written guess becomes a fact.
- **A benchmark completing is not permission to touch the environment.** Auto-restart and
  several live server processes mean the box can look busy long after the intended job
  ended. Gate on: job completes → outputs frozen → process exited → GPU load no longer
  attributable → **several consecutive** endpoint fingerprints agree → only then declare
  an epoch boundary. Implement the stability gate as a script that exits non-zero when
  unstable, so optimism cannot pass it.
- **Stillness is not completion.** "No bench processes + idle GPU" is *also* what a mid-run
  crash looks like, and a run that hit a timeout looks identical to one that finished. Gate
  completion on a **run-scoped witness** — a counter, checkpoint index, or final artefact
  that the run itself produces — and add an explicit terminal state for the ambiguous case:
  `STOPPED_OR_FINISHED_UNRESOLVED`. `witness PASS AND process gone AND GPU idle` is the only
  combination that opens the gate; any other combination stops without capturing a boundary.
- **Run identity belongs to the benchmark process, not to your gate's clock.** The obvious
  discriminator `artefact.mtime > GATE_START` is wrong whenever the gate launches mid-run —
  a progress file written before the gate started may be precisely the in-flight run's own
  output. Anchor on the live process (`pid` + `CreationDate` + command line + runtime dir).
  Gate launch time proves only "existed before the gate", which is a weaker claim than
  "belongs to an earlier run".
- **Grade run membership on a ladder, not a boolean.** `unresolved` (no anchor) < `candidate`
  (path/mtime agree with the process start) < `corroborated` (the same artefact observed
  *advancing* under a live anchor PID) < `verified` (artefact's `run_id`/producer pid/file-handle
  binds to the anchor). A missing anchor is `unresolved`, never silently `previous_run`.
  **Time agreement alone (`candidate`) cannot carry a PASS** — any unrelated write into the same
  directory after the run started satisfies it. Floor PASS at `>= corroborated`.
- **`corroborated` supports membership; it does not prove writer identity.** It establishes that
  anchor and artefact progression coexisted in time. Do not write that it "structurally prevents
  a foreign writer" — a second producer writing the same path in the same window remains
  possible. State the narrower claim, and encode the acceptance as an explicit *operational
  threshold for this threat model* in code so nobody later reads it as a proof level.
- **Log the artefact, not just its counter.** A counter that moved `169 → 174` proves nothing if
  the file was deleted and recreated at the same path. Record `path` + `size` + `mtime` +
  content hash + `anchor_pid` + `anchor_alive` on every sample; constant size with a changing
  hash is an in-place rewrite, a size/path change means replacement. Reset the ledger when the
  anchor pid changes, and **schema-guard it** — entries from an earlier probe revision lack the
  fields the evidence rules need, and reading them as samples fabricates observations that were
  never recorded.
- **Check who actually holds the GPU before wiring GPU state into a completion predicate.** The
  benchmark driver may be CPU-side while a serving process owns the device, in which case "GPU
  idle" was never a progress signal. Use `nvidia-smi --query-compute-apps=pid,process_name` to
  attribute the load to a pid before treating it as the run's.
- **A run-independent success marker is not completion evidence.** A bare `RESULT: OK` read
  out of any log will eventually match a *previous* run's marker and silently open the gate
  while the current run is still going. Require a self-declared `run_id` / `session_id` /
  `started_at` from the artefact when it offers one; otherwise tie it to the process anchor
  with a small mtime tolerance.
- **Under-detecting the running process opens the gate early; over-detecting merely delays
  it.** A narrow process regex that returns zero while the GPU is at 97% is the dangerous
  direction. Fix under-detection first (broaden, then anchor on the specific launcher PID and
  its descendants rather than on generic process matching). Do not try to solve it by making
  the detector clever enough to both find the bench and exclude everything else.
- **Separate endpoint stability, process attribution, and ambient process state into three
  layers.** A stable `/props` response decides stability PASS/FAIL; PID attribution is a
  separate axis reporting `verified` / `partial` / `unresolved`; the full process list is
  ambient state that is recorded and never gates. When PIDs churn across an interrupted run,
  folding them into one fingerprint reads ordinary restarts as endpoint instability.
- **A job can report `status: complete` while its own `reason` still describes work in
  flight.** Observed shape: `completed 904/904, status "complete", reason "saved-row producer
  is running"`. Do not assert a logical contradiction — `status` may mean "the rows exist" and
  `reason` may mean "the producer is busy elsewhere". Record `completion_semantics:
  ambiguous` plus `status and process-liveness signals disagree`, and refuse PASS. Require all
  of: phases at total, all job states final, no liveness disagreement, log counter at total,
  final artefact present, run identity matched.
- **Give a baseline branch and its annotated tag different names.** An identical name makes
  every later `git rev-parse <name>` ambiguous. Verify with `git rev-parse` before relying
  on either.
- **A stale `.git/index.lock` blocks a commit; age and process count are the evidence that it is
  stale.** On Windows a concurrent sync job can leave one behind (observed: a 25-minute-old lock
  with zero `git.exe` processes running, while `git status` still read the index fine). Check
  the lock's age against the current time and confirm no git process holds it before removing —
  do not delete a lock on a first-seen error, because a live index write is a real possibility.
  Record the removal in the run notes.
- **Freeze a read-only environment boundary before swapping models.** Capture model SHA-256, quantisation string, llama.cpp build hash, server command line, `n_ctx`/slots, GPU name + VRAM + temp + clocks, and the effective sampler including **seed**. When the seed is `4294967295` (random per request), trials are not bit-reproducible and the comparison is between conditional response *distributions*. A seeded `random.Random(...)` makes trial **order** reproducible without making model output deterministic — say which one you mean. Read-only capture does not perturb a benchmark the way an inference load does. Parse the model path out of the captured command line, never from a constant in the capture script, or a post-swap boundary silently records the old model.
- **Define an epoch by serving process identity, not by configuration.** Identical command line + identical model SHA + identical sampler is still two epochs when the PID or its start time differs. On an interrupted run, freeze the whole thing (`chmod 444` the original), annotate the interruption with the errors verbatim and `root_cause: UNDETERMINED`, and re-run every condition from scratch — never keep the trials that happened to finish before the environment moved.
- **Resolve the serving process from the binary, not from a port query.** `netstat` and `Get-NetTCPConnection` can both report no listener while `GET /props` on that exact port returns a valid payload from the right build. That is a socket-enumeration visibility limitation, not a free port; record it as UNDETERMINED and identify the process by enumerating the binary and matching its port argument. Scope the authority claim precisely:
  `/props` is authoritative for the **endpoint-reported server/model properties**; it is
  **not** evidence of process identity, and a PID owning the socket needs separate
  confirmation. See `references/environment-epoch-integrity.md`.
- **A ceiling hit is right-censoring, so report a bound and not a value.** Truncating at every trial gives you `L > budget`, never a measured length. "At least ~22× longer" is defensible; "22–25× longer" fabricates precision from a trial that never finished. Ceiling hits at two budgets establish that the length distribution shifted past the higher budget — they say nothing about whether the growth is exponential, linear, or looping.
- **Downgrade the claim the moment the evidence contradicts it — do not hedge,
  do not wait to be told.** The strongest recurring correction in this work is
  not about a wrong number; it is about a right number attached to too strong a
  noun. Observed shape: every clause of a constitution checker passed, and the
  conclusion drawn was "the pipeline is complete / the stage is done / Level 1
  reached". The artefact the stage was supposed to produce — a dataset file —
  did not exist. This user's expected behaviour is the immediate opposite of
  hedging: state the corrected position flatly and precisely, mark the
  retracted claim as retracted, and give the corrected one. Accepting a
  correction by quietly softening the next paragraph leaves the wrong claim
  standing in the record.
  Concretely, separate the axes instead of merging them: *what was built*
  (`engineering_stage`) versus *what the evidence supports* (`claim_level`).
  A green test suite establishes that the **checker** works; it never
  establishes that the **artefact** exists. Write the correction into the
  machine-readable status (`weight_modified: false`,
  `self_improvement_observed: false`, `next_allowed_transition`) rather than
  only into prose. And when the overclaim is your own, treat it as a finding:
  it is a real correction trajectory about calibrating claim strength against
  your own reasoning, which is usually more valuable training material than a
  tidy example invented up front.
- **A check that does not run is indistinguishable from a check that passed.**
  The highest-severity defect found in this work was never a wrong verdict — it was a
  *missing* one. A narrow process regex returned zero while the GPU was at 97%, so the gate
  read "no bench processes" and opened on a live benchmark. Separately, a constitution
  checker appended its result on every early-return path but not on the success paths, so
  two of six clauses simply never printed and the run still exited 0. Both are the same
  bug: a gate/report that is silently shorter reads as a clean result. Defend with three
  habits: assert the **expected check count** so a dropped check fails the run instead of
  shortening the output; make reporting structural rather than optional
  (`try: … finally: checks.append(result)`); and grep **file contents**, not filenames,
  when a check decides whether something was built. A check that quietly reports
  "not built yet" for something that exists is its own kind of lie.
- **Answer in the language the user asked for, and if you slip, say so in one line.** A repeated
  wrong-language response is not a formatting nit — it is a failure to follow an explicit
  instruction, and the longer the answer the more likely it recurs. When the user has already
  said "日本語で頼む" and the draft still drifts, stop and rewrite the whole answer rather than
  patching sentence by sentence; acknowledge the miss in one line and move on, because a long
  self-apology is a third instance of the same failure. Separately, an unedited draft can carry
  stray characters from another script into the delivered document — run a cheap script-range
  check over the final file before committing.

- **Verify mechanically that the protocol layer contains no result.** Separating
  protocol from result by intention is not enough — grep the protocol section for
  the concrete values that belong in the result file (token counts, truncation
  tallies, model names, rate numbers, the finding's own label) and assert the
  list comes back empty. A protocol that quotes one observed number is no longer
  a protocol; a later reader cannot tell a pre-registered rule from a
  post-hoc rationalisation. Cheap check, and it is the only one that catches
  contamination that happens while drafting.
- **An amendment must declare that it was prompted by a failure, and must not
  restate any epoch-1 numbers.** State the failure that motivated it (empty
  control output, environment interruption) and nothing about what the data
  showed. If the amendment is written after seeing results, that is fine and
  normal — what is not fine is presenting the new rules as pre-registered.
  Honest phrasing: *"rules added after the failure; applied prospectively to the
  next epoch; earlier evidence is not retroactively reclassified."* Write that
  sentence in both the user's language and the document's working language.

## Support files

- See `references/epoch-completion-gate.md` for gating a long benchmark before capturing an environment boundary: the WATCH→STOP_AND_REPORT state machine, why stillness is not completion, anchoring run identity on the benchmark process instead of the gate's clock, ambiguous completion semantics (`status: complete` + `reason: "... is running"`), and the endpoint/process/ambient three-layer report.
- See `references/llama-embedding-probe-follow-up.md` for the reusable regression matrix and evidence checklist.
- See `references/binary-codec-roundtrip-verification.md` for the cheap-to-expensive verification ladder for reconstructed binary codecs and format writers, plus header/offset bug classes.
- See `references/behavioural-experiment-protocol.md` for running A/B/C/D behavioural probes against a local model: three-layer record keeping (baseline / protocol amendment / result), the two-axis outcome schema and separate attempted/transport_valid/decision_valid counters, generation cost tracked apart from obedience, environment-boundary capture before a model swap, pilot-vs-statistics discipline, and separating model-system confounds by changing one layer at a time.
- See `references/authority-semantics-experiment-2026-10-02.md` for a worked instance: the full environment boundary, the pilot table showing a condition truncating in 3/3 trials while controls finished in ~85 tokens, and the two harness defects (reasoning-model token budget, double API call) that produced clean-looking zeros before the protocol was amended.
- See `references/auditable-experiment-review.md` for the review vocabulary an
  adversarial operator uses on your experiment — the nine corrections you will be
  handed (censored≠zero, bound≠value, `valid` splits in two, flag≠outcome,
  cost≠obedience, agent agreement≠independence, model name≠evidence, attribution
  stops at verification, `finish_reason` beats a token ratio) — plus the record
  architecture and honest-amendment phrasing that survive review.
- See `references/environment-epoch-integrity.md` for what to do when a run is interrupted mid-flight: define an epoch by serving process identity rather than configuration, resolve the process from the binary rather than from a port query, freeze the whole interrupted run instead of keeping the trials that finished, and state ceiling hits as right-censored bounds ("at least ~22×") rather than fabricated values.
- See `references/multi-agent-audit-to-experiment.md` for running a distributed self-audit across agent instances and turning it into evidence: why N agents agreeing is not N pieces of evidence, decomposing one report into claims with separate evidence states, pinning a red baseline off the default branch, and gating the next epoch on consecutive endpoint fingerprints rather than on a benchmark merely finishing.
