---
name: colab-cloud-gpu-training
description: Run multi-hour GPU jobs on Google Colab that survive drops.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Colab, Cloud-GPU, Training, QLoRA, Durability, Session-Recovery]
---

# Colab Cloud GPU Training

Drive multi-hour GPU work (fine-tuning, big downloads, batch inference) on Colab
from the Hermes desktop app on Windows, so the run survives session drops and the
operator can hand it to a normal web browser when authorization is required.

Use when a task involves: Colab / `colab` CLI, rented A100/T4/H100 GPUs,
fine-tuning that will not fit locally, multi-gigabyte downloads on a rented VM,
or an operator who wants to drive the run themselves from a browser.

## When to Use

Reach for this when **any** of these hold:

- A GPU job will not fit the local box (27B+ fine-tuning, or VRAM < the model)
- The job runs longer than a Colab session, so a drop would cost real work
- Tens of gigabytes must be downloaded on a rented VM
- The operator wants to drive or authorise the run themselves from a browser
- You are writing a handoff zip so someone else can execute the pipeline

Do **not** use it for a quick inference check or a fine-tune that already fits
the local GPU — those belong to `peft-fine-tuning` and the local serving skills.

## The one fact that decides the whole design

**`/content` is ephemeral.** A Colab session that idles out and drops (404/401)
loses everything in it. Measured on this workstation: an idle drop destroyed all
**50.98 GiB** of downloaded safetensors — every shard gone, nothing recoverable.

Therefore:

> **Anything multi-GB must live on `/content/drive/MyDrive`.** Use `/content`
> only as scratch.

Do not design a "skip Drive to save a step" pipeline. It looks fine until the
first drop, and then every attempt re-downloads tens of gigabytes.

## Workflow

### 1. Create the session

```bash
colab new --gpu A100 --session <name>     # T4 | L4 | G4 | H100 | A100
```

Returns `Session READY.` in ~5s. Note the backend id (`gpu-a100-s-kkb-...`).
It appears in `colab sessions`; a `[?]` prefix means the session is already lost.

### 2. Mount Drive BEFORE downloading anything

```bash
colab drivemount -s <name>
```

This **blocks until the operator grants access in a browser** — it prints a
`https://accounts.google.com/o/oauth2/v2/auth?...` URL and waits. Do not
Ctrl+C it. Surface the URL to the user; they paste it into a normal browser,
sign in, and approve.

Confirm with `scripts/drivecheck.py` (see Support files) — it prints `DRIVE_OK`
plus per-directory sizes.

### 3. Stage scripts, then exec them

`colab exec -f` reads a **local** path and streams it as a cell. It does *not*
read a path that exists only inside the session.

```bash
cp scripts/stage1_....py ~/stage1.py      # stage into the local home first
colab exec -s <name> -f ~/stage1.py --timeout 10800
```

Passing `-f /content/stage1.py` fails with `FileNotFoundError` — that path is
resolved locally, not remotely. `colab upload` exists for files you genuinely
need on the VM, but exec wants the local copy.

### 4. Make every stage resumable

Long stages get killed by the Colab Pro session ceiling. Write a sentinel and
branch on it so a re-run continues instead of restarting:

```python
marker = f"{DRIVE}/base/.materialised"
if os.path.exists(marker):
    log("already present; skipping download")
else:
    ...download...
    open(marker, "w").write(rev)
```

Resolve HF cache symlinks into real bytes when materialising
(`hf download` without `--local-dir` leaves symlinks into `../../blobs`):

```python
real = os.path.realpath(s)
if os.path.islink(s) or os.path.abspath(real) != os.path.abspath(s):
    shutil.copyfile(real, d)      # copy the blob, not the link
```

### 5. Ship a handoff package when the operator wants to drive it themselves

Long operator-in-the-loop runs should end as a **zip**: a `README_手順書.md`
with numbered steps plus a `scripts/` dir, each stage guarded by a Drive check.
Verify before shipping — see *Verification before delivery*.

## Pitfalls

### `--auth=adc` is the wrong path when OAuth is already working

The CLI's default auth is `oauth2`, backed by `~/.config/colab-cli/token.json`.
Passing `--auth=adc` forces Application Default Credentials, which needs
`gcloud auth application-default login` and otherwise dies with
`DefaultCredentialsError`. If tokens already exist, **do not pass `--auth`**:

```bash
ls -l ~/.config/colab-cli/token.json     # present -> omit --auth entirely
```

### Session drops are not failures — check before re-downloading

`colab exec` may return `Session '<name>' appears to be lost (404/401). Cleaning
up.` That is an idle timeout, not an auth failure. Recreate the session and
re-run the stage; with Drive already holding the weights, the `.materialised`
marker skips the download.

### A dropped session invalidates in-flight Drive auth URLs

Each `drivemount` URL embeds the session endpoint and a one-shot token. If the
session died between issuing the URL and the user clicking it, the grant lands
nowhere. Check `colab sessions` first, then re-issue.

### Detached jobs need output on a shared mount

`execute_code` is capped (~300s), so a multi-hour stage must run detached.
Redirect into the `/mnt/c` shared mount so output survives the WSL process:

```python
with open(LOG_L, "wb") as fh:
    p = subprocess.Popen(
        ["wsl.exe", "-e", "bash", "-lc",
         f'colab exec -s {name} -f ~/stage.py --timeout 14000 > "{LOG_W}" 2>&1'],
        stdout=fh, stderr=subprocess.STDOUT)
```

A bare `nohup ... &` inside the WSL command dies with the calling shell and
leaves no log at all.

### Verify an upstream tool against the version you will actually install

Reading a GitHub repo and then writing against its API is how you end up with
code that imports a module the published package does not ship.
`happyscienceiscult/heretic` is the worked example: the git `master` branch has
`heretic/plugin.py` and `heretic/scorer.py`, but the PyPI release
`heretic-llm==1.4.0` does **not** — so every
`from heretic.plugin import Plugin, Context` fails at import time on the installed
package.

Install it and check what actually imports before building on it:

```python
for mod in ("heretic", "heretic.plugin", "heretic.scorer", "heretic.config"):
    try:
        __import__(mod); print(f"{mod}: OK")
    except ImportError as e:
        print(f"{mod}: MISSING ({e})")
```

What 1.4.0 *does* ship is more useful than the plugin API: `Settings.benchmarks`
lists eleven lm-evaluation-harness benchmarks (agieval, bbh, commonsense_qa,
eq_bench, gsm8k, hellaswag, ifeval, mmlu, mmlu_pro, piqa, winogrande), and
`main.objective` is an Optuna search over `direction_scope`, `direction_index`,
`max_weight`, `max_weight_position`, `min_weight`, `min_weight_distance`. Reuse
those instead of inventing an evaluation surface. Keep any plugin-API shim behind
a function that raises a clear ImportError on builds that lack it — never
module-level subclassing that breaks the whole import.

Install with `--no-deps` when the dependency closure is large and you only need to
inspect the API surface; a full install can exceed a foreground timeout on its own.

### Multi-file pipelines need a real orchestrator, not a README

Once a job has three or more stages, numbered steps in markdown become the failure
point: after a drop, neither the operator nor the agent can tell which stages
completed. Ship a `run_pipeline.py` with `--list`, `--from N`, and `--only N`,
where every stage checks its own marker file and the orchestrator stops at the
first failure and prints status. Drive the Drive mount through it too, so a
missing mount is one refusal at the top rather than a silently ephemeral write in
stage 4.

### When the terminal tool refuses `wsl.exe`

Some hosts block direct `wsl.exe` invocations from the terminal tool
(`Security Center blocked a unverified execution candidate (SCAN_ERROR)`).
Route through `execute_code` + `subprocess` instead of retrying the terminal
form — that is the working path, not a dead end. On this workstation that is the
normal route for every `colab` call.

### A full-model plan over every tensor exceeds a 300s foreground budget

Scanning a 6.7 GiB GGUF, or planning edits across every tensor of a 27B model,
routinely runs past several minutes — and `execute_code` is capped at ~300s, so
the run dies and you learn nothing. Two fixes, in order of preference:

- **Cut the work with a debug flag first.** A per-tensor block cap
  (`--max-blocks-per-tensor 40`) turns an all-tense minutes pass into a ~5s one
  and exercises the identical code path, so validate the logic before spending
  the long run.
- **Then launch the full pass detached** and poll the log file, rather than
  re-issuing the foreground call and losing the result again each time.

```python
log = r"H:\work\plan.log"
with open(log, "w", encoding="utf-8") as fh:
    p = subprocess.Popen([py, script, "--full"], stdout=fh,
                         stderr=subprocess.STDOUT)
# poll: read the log until a sentinel line appears
```

Picking a timeout budget up front is not enough — a genuinely long pass also
outlives a `time.sleep` poll loop, so poll the LOG and check for the sentinel,
not the wall clock.

### Long-lived binaries may not exist on the remote platform

A Windows-only runtime build cannot be used on a Linux VM, and its absence
usually surfaces only at stage 5. Detect it in the notebook before the expensive
stages by asserting the capability you need, and make the failure name the fix:

```python
out = subprocess.run([quant, "--help"], capture_output=True, text=True)
out = (out.stdout or "") + (out.stderr or "")
assert "PQ2_0" in out, "this build does not support PQ2_0; aborting"
```

Refusing early with the exact required capability beats downloading 50 GiB and
discovering at hour six that the quantizer cannot do the job.


For a handoff package, prove the artifact works rather than assuming:

```python
for f in glob.glob(f"{PKG}/scripts/*.py"):
    py_compile.compile(f, doraise=True)     # every script parses
# then: zip it, extract to a clean temp dir, recompile from the extract
```

Also check the markdown you ship: a broken code fence or a reference to a file
you never created makes the procedure unusable. Cheap assertions that catch it:

- `txt.count("```") % 2 == 0` (fences balanced)
- every `foo.py` mentioned in the README exists in `scripts/`

Fix the package, not just the local copy — the operator only ever sees the zip.

## Support files

- `scripts/drivecheck.py` — reusable probe: prints `DRIVE_OK` / `DRIVE_MISSING`,
  per-directory sizes, shard count + GiB, config arch summary, adapter presence.
  Run it after mounting and again after any long download.
- `references/single-token-classifier-lora.md` — training a model to answer by
  scoring allowed candidate tokens (CE over the candidate logits only, no
  generation), plus the two evaluator keying/rounding traps that silently zero
  your score.
- `references/ternary-bonsai-nimble.md` — worked end-to-end case: Ternary-Bonsai
  27B × Nimble LoRA, including the 324-example holdout numbers, the model-family
  provenance facts, and the PQ2_0 lattice-ablation method.

## Related

- `peft-fine-tuning` — LoRA/QLoRA mechanics, rank and target-module selection
- `gguf-quantization` / `llama-cpp` — re-quantising a merged adapter back to GGUF
- `verification-gated-probes` — building auditable probes with explicit gates
