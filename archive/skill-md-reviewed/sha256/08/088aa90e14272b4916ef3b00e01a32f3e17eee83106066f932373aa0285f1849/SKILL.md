---
name: python-sqlite-script-safety
description: Safe patterns for Python/SQLite automation, verification, and remediation scripts — especially cron/scheduled runs. Covers the SQLite same-cursor UPDATE-while-iterating-SELECT bug, structural (high-entropy) no-secret regex guards with redact-not-delete, and the `python -I` workaround for hanging site initialization on Windows/MSYS.
---

# Python / SQLite Script Safety

Use this skill when writing standalone Python scripts that open SQLite databases, apply regex-based secret/guard checks, and insert/update/delete rows — especially in cron, scheduled, or no-agent automation contexts where a wrong loop or an over-broad guard can silently skip rows or delete good data.

## 1. SQLite cursor-reuse bug in remediation loops

Never run `UPDATE`/`DELETE` on the SAME cursor while iterating its `SELECT`. SQLite finalizes the in-flight SELECT the moment you call `execute` again on that cursor, so the `for` loop aborts after the first row and silently skips the rest.

Observed in a real run: a post-write guard-remediation loop fixed only 1 of 3 violating rows because the nested `cur.execute("UPDATE ...")` finalized the `SELECT` iterator.

Fix — materialize the offending rows first, then update with a fresh statement:

```python
con = sqlite3.connect(db, timeout=60)
con.execute("PRAGMA busy_timeout=60000")
cur = con.cursor()
offending = [c for (c,) in cur.execute("SELECT content FROM memories") if narrow_guard(c)]
for content in offending:
    newc = redact(content)
    if newc != content:
        cur.execute("UPDATE memories SET content=?, encoded=?, updated_at=? WHERE content=?",
                    (newc, enc, time.time(), content))
        remediated += 1
con.commit()
con.close()
```

Always re-run a post-remediation verification pass and report the resulting violation count; only call the run clean when it is 0.

## 2. Structural no-secret guard (not keyword-based)

When filtering stored text for secret material, do NOT block on bare keywords (`secret`, `Bitwarden`, `token`, `oauth`, `bearer`) — those false-positive on legitimate policy phrases and curated facts. Also avoid a bare `[A-Za-z0-9_-]{40,}` token rule: it flags long public URLs and numeric snowflake IDs as "violations."

Match REAL secret material only, with a narrow structural check:
- private-key blocks: `BEGIN ... PRIVATE KEY`
- local paths containing a username: `C:/Users/<user>`, `/home/<user>`, `/c/Users/<user>`
- a 40+ char HIGH-ENTROPY token: mixed case + digits AND Shannon entropy > 3.5 bits/char

Prefer REDACT-in-place (regex-replace the forbidden span with `<redacted-path>` / `<redacted-token>`) over DELETE, so non-secret content survives and a guard mistake cannot delete good memory. See `references/structural-no-secret-guard.md` for a concrete, copy-paste implementation (including the `bs = chr(92)` trick to avoid Windows backslash regex escaping).

## 3. `python -I` when startup hangs (Windows/MSYS)

If plain `python -c "..."` or `python - <<'PY'` hangs for minutes at startup while `echo` is instant, the hang is site initialization (a `sitecustomize` / `.pth` doing a blocking network call), NOT a DB lock and NOT the `python3` Windows-Store stub.

Symptom: `python -I -c "print('ok')"` returns immediately while the non-`-I` form times out.

Fix: launch terminal sync/verify scripts with `python -I` (isolated mode; implies `-E -s -S`, skips site init). Stdlib-only scripts (sqlite3, json, re, hashlib, pathlib) run fine. Do not wrap native `python.exe` in MSYS `timeout` (separate deadlock); use the terminal tool's own timeout parameter instead.

## 4. Windows file lock with tempfile + SQLite

When a test or script uses `TemporaryDirectory` together with SQLite, the `with` block may fail with `PermissionError: [WinError 32]` because SQLite connections hold the file open while `rmtree` runs.

**Pattern that works:**

```python
tmpdir = tempfile.mkdtemp()
try:
    # ... open SQLite, do work ...
finally:
    conn.close()  # Release SQLite connection FIRST
    shutil.rmtree(tmpdir, ignore_errors=True)  # Then cleanup
```

**Do NOT use** `with tempfile.TemporaryDirectory() as tmpdir:` when the body opens SQLite — GC timing is unreliable on Windows.

## Verification checklist
- Materialize SELECT results before mutating in the same loop (fetchall / list comprehension).
- Re-run the guard scan after remediation; report the post-remediation violation count (0 = clean).
- Guard matches REAL secret shapes, not keywords; redact, do not delete.
- If Python hangs at startup, retry with `python -I`.
- Use `tempfile.mkdtemp()` + explicit `close()` + `shutil.rmtree(ignore_errors=True)` on Windows with SQLite.
