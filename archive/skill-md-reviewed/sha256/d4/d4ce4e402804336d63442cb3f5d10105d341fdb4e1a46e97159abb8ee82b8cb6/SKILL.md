---
name: cron-real-post-recovery
description: Debug cron posts to real external success.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Cron, Posting, Verification, Windows]
---

# Cron Real Post Recovery

This skill captures the recovery workflow for a Hermes cron job that appears to run but does not complete its real external side effect, such as posting a VRChat video to X. It does not replace product-specific skills; it teaches the verification discipline: prove the actual post, not just the cron exit status. Dependency stance: prefer `uv`-managed venvs and pin the runtime used by the cron path when host Python compatibility is risky.

## When to Use

- User says a scheduled post “did not fire” or “posted nothing.”
- `cronjob` reports success but the external service has no new post.
- X/lm-twitterer posting fails with `No module named 'js2py_'`.
- Python 3.13/3.14 breaks an older automation dependency.
- A cron script works manually but fails under scheduler environment.
- Duplicate agent-driven cron jobs create noise or conflicting posts.

## Prerequisites

- Hermes repo on Windows at `%USERPROFILE%\Documents\New project\hermes-agent` or adapt paths explicitly.
- Cron script deployed under `~/.hermes/scripts/` for no-agent script jobs.
- `uv` installed.
- `lm-twitterer` configured and authenticated; never print cookies or tokens.
- For VRChat video posts: `ffmpeg`, `%USERPROFILE%\Pictures\VRChat`, Irodori TTS at `http://127.0.0.1:8088`, and the Irodori project at `%USERPROFILE%\Documents\New project\irodori-tts-server`.
- Use `terminal`, `read_file`, `patch`, `cronjob`, `skill_view`, and `search_files`; avoid manual shell readers when a Hermes file tool fits.

## How to Run

Use `cronjob` to list and trigger jobs, `read_file` to inspect the script, `patch` to repair it, and `terminal` to run syntax/import/status checks. Only rerun the live post when the user wants a real post or when the job is expected to publish now; otherwise verify non-posting paths and read activity logs.

## Quick Reference

- List cron jobs: `cronjob(action="list")`
- Run target job: `cronjob(action="run", job_id="07f62cef0201")`
- Pause noisy duplicates: `cronjob(action="pause", job_id="8836c500a031")`
- Stable script path: `%USERPROFILE%\Documents\New project\hermes-agent\scripts\daily_vrchat_post.py`
- Deployed cron copy: `~/.hermes/scripts/daily_vrchat_post.py`
- Python 3.11 venv: `.venv-vrchat-post311`
- Post command: `.venv-vrchat-post311/Scripts/python.exe -m hermes_cli.main lm-twitterer post ...`
- TTS health: `http://127.0.0.1:8088/health`
- TTS speech: `http://127.0.0.1:8088/v1/audio/speech`
- Activity log: `~/.hermes/lm-twitterer/activity.jsonl`

## Procedure

1. Identify the real target cron.
   - Use `cronjob(action="list")`.
   - Record the job ID, schedule, paused/enabled state, `script`, `workdir`, and whether `no_agent` is set.
   - If several jobs post the same content, pick the stable script-based job first and treat agent/skill-driven jobs as duplicate suspects.

2. Separate “cron ran” from “side effect happened.”
   - Run the target with `cronjob(action="run", job_id="...")` only when a live post is acceptable.
   - Then invoke `terminal` to inspect `~/.hermes/lm-twitterer/activity.jsonl` for `posted: true`, a status URL, or a concrete error.
   - Do not call the job fixed from `execution_success: true` alone.

3. Inspect the automation script with `read_file`.
   - Verify it starts Irodori TTS with its own venv and removes `HF_HUB_ENABLE_HF_TRANSFER` before `subprocess.Popen`.
   - Verify it posts through a pinned Python runtime instead of `hermes` from PATH.
   - Verify it treats `"posted": false` and `"ok": false` as failures even when the subprocess exits zero.

4. Build a pinned posting runtime when Python compatibility is suspect.
   - Invoke through `terminal` from the repo root:
   ```bash
   cd /c/Users/downl/Documents/New\ project/hermes-agent && uv venv --python 3.11.11 .venv-vrchat-post311
   cd /c/Users/downl/Documents/New\ project/hermes-agent && uv pip install --python .venv-vrchat-post311/Scripts/python.exe -e . js2py 'twitter-openapi-python>=0.0.44,<0.1' 'tweepy-authlib>=1.7.3,<2' tweepy
   ```
   - If pydantic metadata/runtime drifts, inspect `pydantic/version.py`, then use `ensurepip` and force the required `pydantic-core` version inside the same venv.

5. Patch the script to call the pinned runtime.
   - Use `patch`, not ad-hoc text replacement.
   - The final post step should use:
   ```bash
   .venv-vrchat-post311/Scripts/python.exe -m hermes_cli.main lm-twitterer post
   ```
   - Set `cwd` to the Hermes repo root for the subprocess.

6. Sync the deployed cron copy.
   - Invoke through `terminal`:
   ```bash
   cp "/c/Users/downl/Documents/New project/hermes-agent/scripts/daily_vrchat_post.py" "$HOME/.hermes/scripts/daily_vrchat_post.py"
   ```
   - Verify the copy matches before claiming cron will use the new code.

7. Verify without duplicate posting first.
   - Invoke through `terminal`:
   ```bash
   cd /c/Users/downl/Documents/New\ project/hermes-agent && python -m py_compile scripts/daily_vrchat_post.py
   cd /c/Users/downl/Documents/New\ project/hermes-agent && .venv-vrchat-post311/Scripts/python.exe - <<'PY'
   import js2py
   import twitter_openapi_python
   import twitter_openapi_python_generated
   import tweepy_authlib
   import tweepy
   print('imports: ok')
   PY
   cd /c/Users/downl/Documents/New\ project/hermes-agent && .venv-vrchat-post311/Scripts/python.exe -m hermes_cli.main lm-twitterer status
   cmp -s "/c/Users/downl/Documents/New project/hermes-agent/scripts/daily_vrchat_post.py" "$HOME/.hermes/scripts/daily_vrchat_post.py" && echo 'cron-copy-match: ok' || echo 'cron-copy-match: mismatch'
   ```

8. Run focused tests around cron script execution.
   - Prefer the repo runner when it works:
   ```bash
   cd /c/Users/downl/Documents/New\ project/hermes-agent && scripts/run_tests.sh tests/cron/test_cron_script.py tests/cron/test_cron_no_agent.py -q
   ```
   - If the Windows clean env breaks `Path.home()`, run direct pytest with home variables and report the blocker:
   ```bash
   cd /c/Users/downl/Documents/New\ project/hermes-agent && export USERPROFILE='%USERPROFILE%' HOMEDRIVE='C:' HOMEPATH='\Users\downl' LOCALAPPDATA='%USERPROFILE%\AppData\Local' APPDATA='%USERPROFILE%\AppData\Roaming' HOME='/c/Users/downl' && .venv/Scripts/python.exe -m pytest tests/cron/test_cron_script.py tests/cron/test_cron_no_agent.py -q
   ```

9. Execute the live cron only when appropriate.
   - Use `cronjob(action="run", job_id="07f62cef0201")`.
   - Confirm a real `posted: true` activity entry and a URL.
   - Pause duplicate failing jobs with `cronjob(action="pause", job_id="...")` if they would keep producing noise or duplicate posts.

10. Leave an implementation log.
    - Use `write_file` under `_docs/` with scope, changed files, cause, fix, evidence, skipped checks, and residual risk.
    - Do not commit unless the user asks.

## Pitfalls

- `cronjob` success is not post success. Always check the plugin activity or the external URL.
- Python 3.13/3.14 can break `js2py` with `No module named 'js2py_'` or bytecode errors; use Python 3.11 for this path.
- `uv` venvs may not include pip. Use `uv pip`, or run `ensurepip` only when a package must be forced with pip.
- `HF_HUB_ENABLE_HF_TRANSFER` can make Irodori downloads fail; remove it from the Irodori server subprocess environment.
- Do not rerun live posting repeatedly while testing; use syntax/import/status/copy checks to avoid duplicate X posts.
- Hermes cron script paths for no-agent jobs resolve under `~/.hermes/scripts/`; editing only the repo copy may not affect the scheduled job.
- `scripts/run_tests.sh` may clean Windows home variables. If `Path.home()` fails, state that as an environment blocker and run the closest direct pytest with explicit home variables.
- Never show X cookies, OAuth tokens, session material, or connection strings; redact accidental secret-looking output.

## Verification

A non-duplicate recovery is verified when this command passes and the deployed copy matches:

```bash
cd /c/Users/downl/Documents/New\ project/hermes-agent && python -m py_compile scripts/daily_vrchat_post.py && .venv-vrchat-post311/Scripts/python.exe - <<'PY'
import js2py
import twitter_openapi_python
import twitter_openapi_python_generated
import tweepy_authlib
import tweepy
print('imports: ok')
PY
```

A live recovery is verified only after `cronjob(action="run", job_id="07f62cef0201")` and `~/.hermes/lm-twitterer/activity.jsonl` show `posted: true` plus a real X status URL.
