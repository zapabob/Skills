---
name: empty-pipeline-root-cause
description: Root-cause empty results in memory and graph pipelines.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Debugging, Memory, Semantic-Graph, SQLite, Root-Cause, Verification]
    related_skills: [systematic-debugging, hakua-memory-dev, memory-consolidation-sleep-obsidian-sync, python-sqlite-script-safety]
---

# Empty-Pipeline Root Cause

Root-causes a pipeline that returns a **structurally empty** result — `[]`, `count: 0`,
`association_id not found` — and proves the repair on a database copy before touching the
live store. It does not run the periodic consolidation cycle itself (that is
`memory-consolidation-sleep-obsidian-sync`) and it does not teach general debugging method
(that is `systematic-debugging`). Stdlib Python plus `sqlite3`; no test framework needed.

## When to Use

- A memory/graph tool answers successfully but with an empty payload, for cycles in a row.
- You have a **suspected cause** ("the provider is wrong", "the embedding is broken") and
  need it confirmed or killed before acting on it.
- A repair means flipping a config flag or seeding rows, and you must prove the blast radius
  on a copy before the live store.
- A second call to the same tool returns empty while the first returned data.

## Prerequisites

- A readable SQLite DB path and a writable temp dir (`tempfile.gettempdir()`).
- For Hermes memory subsystems: the runtime interpreter is the repo venv, and the code that
  actually executes may be an installed package rather than the repo copy (see Pitfalls).

## How to Run

Invoke the probe through the `terminal` tool, always against a **copy**:

```bash
python scripts/probe_seed_sources.py --db "<live.db>" \
  --sql "SELECT COUNT(*) FROM <focus_table>" \
  --sql "SELECT COUNT(*) FROM <fallback_table> WHERE <status_col>='<value>'"
```

Open the DB read-only when you only need counts; the script copies first by default so the
live file is never written. Use `read_file` on the implementation module to enumerate the
focus sources by hand, then encode them as `--sql`.

## Quick Reference

| Need | Action |
|------|--------|
| Empty result, live tool | Call the tool once; capture the response verbatim |
| Candidate seed sources | Read the function; count each source table directly |
| Live counts | `probe_seed_sources.py --db <db> --sql "SELECT COUNT(*) …"` |
| Kill a suspect theory | `search_files` the function for its network / LLM call sites |
| Prove a repair | Same probe against a copy, with the flag flipped |
| Blast radius | Run the side-effecting cycle on two copies, compare metrics |
| Commit + verify remote | `git push`, then `git ls-remote` + `gh api …/commits/<branch>` |
| Record the finding | Wiki concept page + `ebbinghaus_memory(action="remember")` |

## Procedure

1. **Capture the empty result verbatim.** One call to the real tool. Record whether the
   response distinguishes *disabled* from *enabled-but-empty* — several tools return both, and
   an `enabled: true` flag with an empty list is a different bug from `enabled: false`.

2. **Enumerate every source the function can draw from.** Read the implementation and list
   each query feeding its focus set. Do not accept the first source you find; a focus set with
   two independent inputs needs both counted.

3. **Count each source in the live DB.** Use the probe with one `--sql` per source. Zero rows
   in every source means the empty result is **structural, not transient** — there was never
   anything to assemble. That single measurement usually ends the investigation.

4. **Falsify the leading suspect explicitly.** For a "the provider/LLM is broken" theory, read
   the function under repair and search it for network or model call sites. If there are none,
   the theory cannot explain the symptom: record that it is a *separate* failure and stop
   chasing it. Name the correct failure you did find, so the earlier note stops misleading.

5. **Prove the repair on a copy, never on the live store.** Copy the DB into temp, construct
   the store object against the copy, flip the flag or seed the rows, and drive the full chain
   end to end (trigger → assemble → propose → validate → promote). Record the promoted id and
   the before/after counts. This also proves the repair is sufficient rather than merely
   correlated.

6. **Measure blast radius before recommending the flip.** Run the side-effecting cycle on two
   copies — one with the flag off, one with it on — and diff the metrics. Equal results are the
   evidence that the change is safe; equal-by-luck is not the same as equal-by-measurement.

7. **Re-run the original tool once.** One call. Never twice (see Pitfalls). Confirm the count
   moved and report the residual manual step (a restart) as **unverified** until the runtime
   actually reports the new state.

8. **Record, then commit, then verify the remote.** Write the root cause into the durable
   concept page, note the unverified step explicitly, commit with a scoped message, push, and
   confirm with three independent checks: local `rev-parse`, `git ls-remote`, and the forge API.
   Write the run result back into the memory system **after** the commit, and say so in the
   record so the exported snapshot is not mistaken for post-write-back state.

## Pitfalls

- **A repeat call can fake a regression.** A `UNIQUE` fingerprint column plus a swallowed
  `IntegrityError` makes the second identical call return empty while the first row is stored.
  Verified pattern: preview → 1 result, immediate re-preview → 0, row count still 1. Delete the
  row before re-testing or the check lies.
- **Never seed or repair the production DB to make a check pass.** `shutil.copy2` into temp,
  run the whole chain there, then apply the real change only after the copy passes.
- **The runtime code may not be the repo code.** Compare file hashes between the repo module and
  the installed package the interpreter actually imports, and compare version strings. Edit and
  diagnose the one that runs.
- **Config flags load at startup.** A flipped flag changes nothing until the process restarts,
  and the live status call keeps reporting the old value until then. Report that step as
  pending, never as done.
- **"Empty" is often "no qualifying input", by design.** When a threshold must be both rare
  enough to miss and common enough to be shared, a low hit rate is the mechanism working. Probe
  many samples, report the rate, and do not treat frequent failure as a bug.
- **Count parity is not loss-freedom.** Two snapshots with equal item counts can differ by
  removed-and-added rows. Diff exact keys and classify revisions, additions, and churn.
- **Byte-size differences across a push are usually line endings.** `core.autocrlf=true` with no
  `.gitattributes` inflates the checked-out copy. Compare blob hashes, not sizes, before calling
  a file corrupt.
- **Windows shell blocks long commands.** `command length exceeds safe limit` also breaks
  `read_file` and `search_files`; switch to Python inside `execute_code` and read files with
  `open(..., encoding="utf-8")`.
- **Python 3.11 inspection scripts reject backslashes in f-string expressions.** Precompute the
  value into a variable, then format it.
- **A private-repo snapshot can still carry session excerpts** in label fields even with secret
  patterns clean. Zero secret-pattern hits is not the same as zero disclosure risk.

## Verification

```bash
python scripts/probe_seed_sources.py --db "<live.db>" --sql "SELECT COUNT(*) FROM <focus_table>"
```

Passing means the probe read the DB and reported a count; the investigation is only complete
when **every** enumerated source is non-empty in the live store *or* the empty ones are named
as the root cause, the suspect theory is recorded as falsified, and the repair is demonstrated
on a copy.
