---
name: cross-platform-path
description: Use when path assertions pass on POSIX and Windows.
---

# Cross-platform path assertions in Python tests

Use whenever a test compares, checks, or searches inside a filesystem path string
that is produced by `pathlib.Path` or `os.path` — and the suite is meant to run
on both POSIX (`/tmp/x`) and Windows (`\tmp\x`). The classic symptom: a test
"passes on Linux, fails on Windows" because `/tmp/...` becomes `\tmp\...`.

## The three patterns

### 1. Exact equality against a literal POSIX path
Wrap the literal in `Path` and stringify — this makes the expected value
platform-correct on both sides:

```python
assert result["image"] == str(Path("/tmp/openrouter_gen.png"))
# POSIX -> "/tmp/openrouter_gen.png"
# Windows -> "\\tmp\\openrouter_gen.png"  (matches what the code produced too)
```

Works because the code under test builds the path with `Path("/tmp/...")` as
well, so both sides transform identically. **Do not** compare against the raw
string `"/tmp/openrouter_gen.png"` — on Windows the actual value has backslashes
and the equality fails.

### 2. "Is this an absolute path?" — DO NOT use is_absolute()
```python
# CORRECT (platform-agnostic):
assert result["image"].startswith("/") or result["image"].startswith(chr(92))
```
`chr(92)` is the backslash. Avoid a literal `\` in source to keep it unambiguous
to editors/linters.

> **PITFALL — `Path(p).is_absolute()` is WRONG for `/`-prefixed paths on Windows.**
> On Windows, `Path("/tmp/x")` is parsed as a *relative, drive-less* path
> (relative to the current drive root), so `is_absolute()` returns `False`.
> Naively "improving" `startswith("/")` to `is_absolute()` will BREAK the test
> on Windows even though it reads as a strictness improvement. See
> `references/gotchas.md` for the full traceback.

### 3. Substring membership inside a path
Normalize separators before `in` / `==` checks:
```python
assert ".mp4" in result["video"] and "cache/videos" in result["video"].replace(chr(92), "/")
```
This folds `\home\x\.hermes\cache\videos\...` (Windows) into the POSIX form the
test author wrote, so the literal substring still matches.

## Why chr(92) instead of os.sep or a literal "\"
- A bare `"\\"` literal is easy to mis-escape and easy to misread in diffs.
- `os.sep`-based per-platform literals are more brittle than normalize-then-check.
- `chr(92)` is explicit, needs no import, and documents intent at the call site.

## Checklist for a "fix path test for Windows" task
- [ ] Equality vs literal POSIX path -> `str(Path(...))`
- [ ] Absolute-path check -> `startswith("/") or startswith(chr(92))` (NOT is_absolute())
- [ ] Substring-in-path check -> `.replace(chr(92), "/")` before `in`
- [ ] Confirm `Path` is imported where the pattern is used
- [ ] Run the tests on Windows if available to prove the fix, not just POSIX
