---
name: media-publish-workflow
description: >
  Class-level workflow for rendering narrated video from scratch, packaging it for social upload,
  cleaning the git worktree, and pushing from Windows. Use when the task involves numpy/PIL/OpenCV/ffmpeg
  rendering, narration audio fallback, lm-twitterer/X media uploads, or zapabob-main commit/push hygiene.
  Not for one-off manual posts.
---

# Media Publish Workflow

Windows-first playbook for producing narrated comparison video, posting to X, and committing the clean worktree to `origin/main`.

## Trigger

Use this skill when the task includes any of:
- render video from frames/slides with numpy/PIL/cv2 + ffmpeg
- attach narration audio when TTS is unavailable or unstable
- package media for lm-twitterer/X upload with known failure modes
- clean worktree before pushing to zapabob/hermes-agent `main`
- bump pins, `uv lock`, verify, commit, push

## Render Pipeline

1. **Text layout pre-check**: render 1 representative frame, inspect with vision, confirm CJK glyphs before full render.
2. **Font fallback order on Windows**: NotoSansJP-VF > `meiryob.ttc`/`msgothic.ttc` > `meiryo.ttc`/`msgothic.ttc` > western fallback.
3. **QC**: produce `contact_sheet.png` + per-scene frame diffs; do not skip frame extraction.
4. **Twitter encoding**: `-movflags +faststart -profile:v baseline -level 3.0 -pix_fmt yuv420p`. `mpeg4`/audio-less uploads are rejected by X.

## Narration Fallback Rule

If irodori-tts-server returns `ConnectionResetError(10054)`, exit 139, or Win32 error 1455 on `/v1/audio/speech`:
- Do not retry live synthesis repeatedly.
- Fallback: reuse an existing hakua voice sample (`hakua.ogg`), loop/extend with `ffmpeg` `aloop`/`stream_loop`, and merge to the master.
- Only retry synthesis after changing environment, not after identical failures.

## lm-twitterer Media Upload

- Media files must be under `%USERPROFILE%\.hermes\lm-twitterer\media\`.
- If `CreateTweet` returns error 324 (`Video metadata / videoInfo is required`):
  1. Do not immediately patch `plugins/lm-twitterer/core.py` again unless you have verified the upload response shape.
  2. Prefer diagnosing `_upload_media_with_cookies` raw response first.
  3. If uncertain, revert plugin to HEAD; workaround with known-good copy or different file length/encoding.
- Posting text must be genuinely English-only when requested; do not silently back-translate to Japanese.

## Windows venv / uv hygiene

- Prefer `.venv312/Scripts/python.exe` for direct execution checks.
- `uv run python ...` may fail on Windows due to in-use files inside `.venv` (`cryptography` RECORD rename / `os error 5`); if that happens, fall back to direct venv interpreter instead of forcing rebuild.

## Clean Worktree -> Commit -> Push

1. `git status --short` first. Classify each path:
   - keep: `pyproject.toml`, `uv.lock`
   - revert plugin code before commit if it was experimentally modified
   - unstage local env/addons: `.venv312/`, `bin/`, etc.
2. Ensure `.gitignore` contains environment paths; confirm with `git check-ignore -v`.
3. Revert any plugin file that was experimentally modified: `git checkout -- plugins/<plugin>/...`
4. Stage only intended changes: `git add pyproject.toml uv.lock`
5. Commit with a concise message, then push to `origin main`.
6. After push: `git status`, verify up-to-date state, report commit SHA.

## Pitfalls

- Repeating identical irodori synthesis requests after platform-level connection reset wastes time and can exhaust host resources.
- Repeatedly patching `lm-twitterer/core.py` for 324 without inspecting upload response turns a routing issue into code drift.
- `git status --short` output is authoritative; minimize redundant checks in the same state.
- Do not push with uncommitted experimental plugin modifications.