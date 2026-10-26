---
name: cron-diagnosis-and-repair
description: Diagnose and fix no-agent script cron jobs.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Cron, NoAgent, Debugging, Operations]
    related_skills: [cron-runtime-reliability]
---

# Cron Diagnosis and Repair

Diagnose why a `no_agent: true` cron job is failing by inspecting job state, the called script, and its execution environment, then apply targeted patches. Does not cover LLM-driven cron jobs or gateway health. The example in this skill follows the daily VRChat photo post cron (`07f62cef0201`).

## When to Use

- "cronがエラーで止まってる、原因を調べて"
- "このcronジョブのlast_statusがerrorになってる"
- "毎朝のVRChat投稿が動かなくなった"
- "no-agentスクリプトがcronでだけ失敗する"
- "スクリプトを修正したからcronに反映して"

## Prerequisites

- `cronjob` tool available
- Access to the script file the cron references
- If the script calls external tools (irodoriTTS, FFmpeg, lm-twitterer), those must be independently testable

## Procedure

### 1. List cron jobs and find the failing one

Use the `cronjob` tool with `action='list'` to check all cron jobs. Scan `last_status` for `"error"` and note the `job_id`.

The VRChat post cron was:
```
job_id: 07f62cef0201
last_status: error
schedule: 0 7 * * *
script: daily_vrchat_post.py
no_agent: true
workdir: %USERPROFILE%\...\hermes-agent
```

### 2. Read the called script

Use `read_file` to inspect the script the cron executes. Look for:
- Hardcoded paths that may not exist
- External process calls (`subprocess.Popen`, `subprocess.run`)
- Environment variables that control behaviour
- The fallback path dependency chain

For the VRChat cron, the key function was `start_irodori_server()` which spawned irodoriTTS without the CPU-mode env vars needed for RTX 5060 Ti.

### 3. Test the root cause independently

Reproduce the failing operation outside the cron, through the `terminal` tool. Run the script manually or test its components:

```text
# Start irodoriTTS to test GPU crash
cd /c/Users/downl/Documents/New\ project/irodori-tts-server
# Without CPU env vars (will crash):
/venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
# With CPU env vars (fix):
IRODORI_MODEL_DEVICE=cpu IRODORI_CODEC_DEVICE=cpu IRODORI_PRELOAD=false HF_HUB_ENABLE_HF_TRANSFER=0 /venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
```

Check the irodoriTTS health endpoint:
```text
curl http://127.0.0.1:8088/health
```

### 4. Apply the fix with `patch`

Use the `patch` tool to modify the script. The VRChat fix added four env vars to `start_irodori_server()`:

```python
env = os.environ.copy()
env.pop("HF_HUB_ENABLE_HF_TRANSFER", None)
env["IRODORI_MODEL_DEVICE"] = "cpu"
env["IRODORI_CODEC_DEVICE"] = "cpu"
env["IRODORI_PRELOAD"] = "false"
```

### 5. Sync the fixed script across deployment copies

No-agent scripts in workdir-based cron resolve relative to either the workdir or `~/.hermes/scripts/`. Both copies must be patched.

```text
# Patch repo copy
patch path="scripts/daily_vrchat_post.py" old_string=... new_string=...
# Same fix to deployed copy
patch path="~/.hermes/scripts/daily_vrchat_post.py" old_string=... new_string=...
```

### 6. Update cron script path

If the script path in cron is ambiguous (no directory prefix), update it with the explicit relative path from the workdir:

```text
cronjob action=update job_id=07f62cef0201 script=scripts/daily_vrchat_post.py
```

### 7. Verify the fix

Check both copies are identical and syntactically valid:

```text
# Syntax check
python -c "import py_compile; py_compile.compile('scripts/daily_vrchat_post.py', doraise=True); print('OK')"
# File comparison
python -c "
import filecmp
a = r'%USERPROFILE%\...\scripts\daily_vrchat_post.py'
b = r'%USERPROFILE%\.hermes\scripts\daily_vrchat_post.py'
print('IDENTICAL' if filecmp.cmp(a, b) else 'DIFFERENT')
"
```

The cron will run on its next scheduled tick. Check `last_status` after the next execution to confirm success.

## Pitfalls

- **Cron scripts are cached**: no-agent scripts run in a fresh subprocess each tick, so no restart is needed after patching.
- **Script path resolution**: with `workdir` set, `script: daily_vrchat_post.py` resolves relative to the workdir; if not found there, falls back to `~/.hermes/scripts/`. Always set an explicit relative path like `scripts/daily_vrchat_post.py`.
- **Global `python` hangs on Windows**: Use a dedicated venv's `python.exe` for verification commands, not the system `python` or `python3`.
- **irodoriTTS GPU SIGSEGV**: On RTX 5060 Ti 16GB, the server crashes (exit 139) during model load with `model_device=auto`. Always force CPU mode + preload=false.
- **Script env isolation**: `subprocess.Popen(cmd, env=env)` passes a full copy; the cron job's own environment variables (e.g. `HERMES_HOME`) are not automatically inherited by the spawned process. Hardcode or pass explicitly.
- **`last_status` alone is ambiguous**: An `"error"` status means the script exited non-zero or timed out — it does not reveal where in the script the error occurred. The script's own stderr is not stored in the cron record; reproduce manually.
- **Silent skip ≠ error (config drift)**: An unpinned LLM-driven cron job can skip with `SKIPPED — global inference config drifted` and propagate as `RuntimeError` up to `cron.scheduler`. This is NOT a script-level defect and patching the no-agent script will not help. See the `cron-runtime-reliability` umbrella and its `references/2026-08-03-drift-repair-correction.md` for the repair. CRITICAL: `cronjob action=update job_id=<id> provider=<p> model=<m>` does NOT pin (silent no-op, model stays null). The working repair is: pause the `Daily MoA Orchestrator Rotation` cron, pin the global via `hermes config set moa.active_preset hakuapulse-orchestrator`, then `cronjob pause`+`create` each failing job. Treat a config-drift skip as a separate failure layer from no-agent script bugs.
- **ffmpeg path quoting**: File paths with multiple dots (e.g. `21-00-04.175` in VRChat filenames) confuse MSYS/bash. Use single-quoted Windows paths (`'C:\...'`) in the `terminal` tool.

## Verification

After the fix, check the cron job's next `last_status` after its scheduled run. Also verify the script can be imported cleanly without side effects:

```text
python -c "import ast; ast.parse(open('scripts/daily_vrchat_post.py').read()); print('AST parse OK')"
```
