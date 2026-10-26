---
name: windows-hermes-code-verification
description: "Verify Hermes Python changes on Windows with focused tests."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, pytest, verification, debugging, hermes, providers, file-operations]
    related_skills: [systematic-debugging, requesting-code-review, test-driven-development]
---

# Windows Hermes Code Verification

Use this class-level workflow after modifying or investigating Hermes Python code on a Windows checkout, especially ACP adapters, file operations, provider routing, optional extras, and cross-platform path handling.

## Goals

- Reproduce the reported failure with the narrowest test first.
- Distinguish environment/setup failures from regressions in edited code.
- Verify Windows-specific semantics such as CRLF/BOM preservation and path handling.
- Separate host-native path interpretation from target-platform path formatting.
- Report focused green tests separately from full-suite status.

## Workflow

1. **Inventory first.** Read `AGENTS.md`, inspect `git status`, and identify the project interpreter and dependency declarations. Never treat the start-of-session workspace snapshot as current.
2. **Reproduce narrowly — and confirm it still fails.** Run the exact named test(s) with the project interpreter and capture the full assertion/stack trace *before* changing code. A task brief that enumerates "N failing tests" can be stale relative to the current checkout: run each named test and only patch the ones that genuinely fail. In one session 3 of 6 "failures" already passed on the checkout — blind patching of already-green tests wastes effort and risks regressions.
3. **Trace the data flow.** For path failures, inspect values inside Python before blaming MSYS: native Windows `pathlib` and `os.path` can turn POSIX-looking paths into backslash or mixed-separator paths. For byte-count failures, follow the value from caller input through normalization and disk write. For provider failures, follow explicit runtime configuration through fallback order and check for ambient credentials/configuration.
4. **Classify production versus test assumptions.** Unconditional WSL conversion and host-native formatting of promised Linux/Termux strings are production defects. Tests that mock only POSIX `HOME` semantics or hardcode `/` while passing a Windows `Path` are test portability defects.
5. **Check dependency state.** If an optional package is declared in `pyproject.toml` and pinned in `uv.lock`, install that pinned package into the active development venv. Hermes intentionally rejects wheel/sdist builds of the project itself, so `pip install '.[extra]'` may fail at the project build step; in that case install only the declared package directly and rerun the focused tests.
6. **Make one root-cause fix.** Avoid broad fallback changes or platform-specific test hacks. For target-platform examples or commands, use target-specific formatting (`posixpath`/`PurePosixPath` for Linux, WSL, and Termux) while keeping genuine filesystem probing native. For text writes, preserve the API's established logical payload-size contract independently from physical CRLF/BOM bytes. For provider routing, incomplete explicit configuration must not silently select an unrelated globally configured provider.
7. **Verify in layers.** Run changed-path `py_compile`, `git diff --check`, focused regression tests, and related subsystem tests. For a single test or small set, do **not** use `scripts/run_tests.sh` — it is too slow for focused verification. Invoke the venv interpreter directly:
   ```bash
   cd '/c/Users/<user>/Documents/New project/hermes-agent' && \
     .venv/Scripts/python.exe -m pytest tests/plugins/<file>::<test> -xvs 2>&1 | tail -20
   ```
   Then attempt the standard full runner with a Windows interpreter override only for full-suite status:
   ```bash
   HERMES_PYTHON='/c/Users/<user>/.../.venv/Scripts/python.exe' \
     HERMES_TEST_WORKERS=1 bash scripts/run_tests.sh
   ```
8. **Report honestly.** Give exact pass counts and commands. State full-suite failures, timeouts, missing optional dependencies, and unrelated Desktop/UI failures separately; focused passing tests do not make the whole repository green.

## Loading a plugin module standalone (importlib)

When you must invoke a plugin's Python directly from a shell — debugging,
cron, or because the `hermes <plugin>` CLI is not registered — load its
`core.py` as a module. Four Windows-specific traps block the naive pattern:

1. **Register the module in `sys.modules` before `exec_module`.** Plugin
   `core.py` usually declares `@dataclass` classes at module top level.
   Loading with `spec_from_file_location(name, path)` + `module_from_spec` +
   `exec_module` *without* first setting `sys.modules[name] = mod` raises
   `AttributeError: 'NoneType' object has no attribute '__dict__'` (the
   dataclass decorator cannot find its own module). Fix: assign to
   `sys.modules` immediately after `module_from_spec`.
2. **MSYS rewrites forward-slash path arguments.** Under Git Bash / MSYS a
   path passed as a Python string like `/c/Users/downl/...` is silently
   converted by the shell to `C:\c\Users\downl\...` before Python sees it,
   causing `FileNotFoundError: 'C:\\c/Users/.../core.py'`. Fix: prefix the
   command with `export MSYS_NO_PATHCONV=1`, or pass native Windows paths
   (e.g. `%USERPROFILE%/...` — no leading slash — or `C:\Users\...`).
3. **Use the venv interpreter, not bare `python`.** On Windows `python` is the
   Microsoft Store stub: it prints `Python` and exits non-zero (49) without
   running your script. Use the Hermes venv interpreter explicitly
   (`<repo>/.venv/Scripts/python.exe`) and verify the plugin's deps
   (`twitter_openapi_python`, `tweepy_authlib`, etc.) import there. `py -3`
   works for general scripts but may lack plugin packages.
4. **Put the repo root on `sys.path`.** Plugin `core.py` often imports
   `hermes_constants`; insert the Hermes repo root before loading or imports
   fail even though the plugin file itself is healthy.

See `references/standalone-plugin-module-loading.md` for a copy-paste template
that discovers the plugin path (it may be under `~/.hermes/plugins/<name>/`,
not `<repo>/plugins/<name>/`) and applies all four fixes.

## Windows-specific checks

- CRLF preservation can make physical file bytes larger than the logical UTF-8 input. Test both the returned API value and actual file contents.
- `Path.as_uri()` and POSIX/MSYS path translation can expose separate ACP resource-link failures. Do not conflate these with dependency installation or provider failures.
- A `file:///C:/...` URI should remain a native drive path on Windows; translate it to `/mnt/<drive>/...` only in WSL.
- Python 3.8+ Windows `os.path.expanduser()` uses `USERPROFILE` or `HOMEDRIVE`/`HOMEPATH`, not `HOME`; when a Git Bash/Termux-facing contract explicitly uses `HOME`, expand `~` against that variable before falling back to `expanduser()`.
- Windows asyncio pipe tests may fail with `WinError 6`; retain protocol coverage by using `socket.socketpair()` plus `asyncio.open_connection()` instead of anonymous `os.pipe()` handles.
- For Python-launched shell snippets and `.sh` hooks, resolve Git-for-Windows Bash with the existing `tools.environments.local._find_bash()` logic and use `--noprofile --norc`; bare `bash` can resolve a WSL stub or leave capture pipes open. Quote test-generated Windows paths and pass forward-slash forms inside Bash scripts.
- **`shlex.split(posix=True)` silently strips backslashes from Windows paths.** Any slash-command / CLI argument parser built on `shlex.split` (Hermes's `run_slash` does this) turns `attach 123 C:\Users\...\file.txt` into the token `C:Users...file.txt`, producing "no such file". Path-extraction heuristics that only match `/` or `~/` Unix prefixes (e.g. a terminal-result regex `(?:^|\s)(/[^\s'"]+|\~/[^\s'"]+)`) likewise never catch `C:\...` drive paths. Fixes: (1) pass **forward-slash** path forms into slash-command strings — Windows `pathlib`/`open()` accept `/` natively — i.e. `run_slash(f"attach {task_id} {str(src).replace(chr(92), '/')}")`; or quote the path if the parser honors quotes. (2) Extend Unix-only path regexes with a Windows drive alternative: `[A-Za-z]:[\\/][^\s'"`]+`. See `references/windows-shlex-and-path-extraction.md` for copy-paste snippets and the reproduction recipe.
- `prompt_toolkit` can raise `NoConsoleScreenBufferError` in services and captured tests. Fall back to plain output only for that exception; do not suppress unrelated renderer errors.
- Symlink tests must preserve coverage when creation succeeds and only skip the specific privilege failure (`WinError 1314` from `os.symlink`/`Path.symlink_to` without Developer Mode or admin on Windows), never weakening production path guards. Use a **probe helper**, not a bare `sys.platform == "win32"` check — some Windows builds (Developer Mode, admin, CI runners) *can* create symlinks, so a platform-only guard wrongly drops coverage there. The probe tries a real symlink in a throwaway temp dir and returns `False` on `OSError`/`NotImplementedError`:
  ```python
  def _can_symlink() -> bool:
      try:
          with tempfile.TemporaryDirectory() as td:
              (Path(td) / "real").mkdir()
              (Path(td) / "link").symlink_to(Path(td) / "real")
          return True
      except (OSError, NotImplementedError):
          return False
  ```
  Then decorate the test: `@pytest.mark.skipif(not _can_symlink(), reason="symlinks not available on this platform")`. See `references/symlink-test-skip-pattern.md` for the full ready-to-paste helper, decorator, and the keep-production-guards pitfall.
- **`pytest-randomly` can manufacture setup/teardown ERRORs that are not your bug.** On this Windows box the repo's default addopts load `pytest-randomly`, whose reseed hook calls `thinc.util.fix_random_seed` → `numpy.random.seed`, raising `ValueError: Seed must be between 0 and 2**32 - 1` at *setup* and *teardown* of arbitrary tests. Symptom: a run reports e.g. `109 passed ... 13 errors` where every error traceback is inside `pytest_randomly/__init__.py`, never in your code. Do not chase it. Re-run with the plugin disabled to get a clean signal:
  ```bash
  py -3 -m pytest tests/<file>.py -q -o addopts= -p no:randomly
  ```
  `-o addopts=` drops repo default flags; `-p no:randomly` is the part that removes the false errors. Read the traceback before concluding the errors are environmental — if the frames are in your module, they are real.
- **Bare `python` on this host is the Microsoft Store stub**: it prints `Python` and exits 0 without running anything, so `python -m pytest ... | tail` silently produces no test output and looks like a pass. Use `py -3` (or the repo venv's `.venv/Scripts/python.exe`) and confirm the output contains an actual pass/fail count before reporting success.
- Ambient `.env`/Hermes config credentials can make provider fallback tests nondeterministic. Tests for explicit provider selection must exercise partial runtime configuration while ambient credentials exist.

## Reusable references

- See `references/windows-verification-and-provider-fallbacks.md` for the concrete ACP installation, byte-count reproduction, provider fallback reproduction, and verification commands from a representative Hermes Windows session.
- See `references/cross-platform-path-test-triage.md` for probes and decision rules covering native Windows paths, MSYS, WSL, file URIs, Termux hints, and platform-neutral fixtures.
- See `references/windows-shlex-and-path-extraction.md` for the `shlex.split(posix=True)` backslash-stripping gotcha and the Windows drive-path regex fix (slash-command arg parsing and terminal path extraction).
- See `references/symlink-test-skip-pattern.md` for the copy-paste `_can_symlink()` probe helper, skipif decorator, and the Windows `WinError 1314` gotcha (skip the test, keep the production path guard).
- See `references/standalone-plugin-module-loading.md` for a copy-paste template that loads any Hermes plugin module standalone on Windows (sys.modules registration, MSYS path fix, venv interpreter, plugin-path discovery).
- See `references/semantic-graph-live-smoke-and-commit-bound-evidence.md` for isolated Semantic Graph runtime smoke gates, metadata redaction, bilingual recall, provenance, run-scoped export, correction history, and commit-bound review evidence.
- See `references/llama-server-hf-live-embedding-probe-windows.md` for Windows llama-server HF resolution, TLS build gates, model-loading lifecycle, embedding endpoint verification, stability interpretation, and public-diff hygiene.
- See `references/ssrf-safe-client-remediation.md` for fixing SSRF review findings in gateway adapters (`create_ssrf_safe_async_client` + `await async_is_safe_url`) and the autouse fixture that keeps the affected tests resolver-free.

## Commit-bound evidence and runner post-processing

When verification uses a Windows/MSYS canonical runner, bind every claim to an exact commit SHA and working-tree state. A green run on `HEAD + uncommitted changes` is not evidence for `HEAD` alone. If a runner fix is uncommitted, report that boundary, commit the runner fix separately when practical, and rerun the identical canonical commands at the new HEAD before treating the evidence as commit-bound. Keep targeted tests, canonical-runner results, static checks, full-suite results, live integration, CI/review, merge, and production-readiness claims separate.

Treat test-worker exit codes and failure counts as authoritative. Duration metadata such as `test_durations.json` is optional scheduling data: normalize its path, create the parent directory, catch filesystem errors, emit a warning with path plus exception type/message, and never let cache persistence override the primary test result. After changing runner post-processing, use `scripts/run_tests.sh` rather than direct `pytest` alone and record pass/fail counts, `RUNNER_EXIT`, warnings, interpreter, shell, worker count, and timestamp. Update the implementation log with the final SHA and any failed patch attempt; a hunk mismatch is not a code change unless the working tree confirms one. See `references/canonical-runner-commit-bound-evidence.md`, `references/msys-doubled-separator-fix.md`, and `references/semantic-graph-hardening.md`.

## Runner Failure Triage

When the canonical per-file runner exits non-zero after test execution, first separate test assertions from runner teardown or aggregation failures. Re-run the same test selection with the project interpreter directly, disabling unrelated pytest plugins or cache providers when the traceback implicates teardown noise. Report the direct pytest result separately from the canonical-runner result; never call a runner-level failure a test pass, and never promote focused green tests to a full-suite claim.

For the verified Windows/MSYS worktree case where all tests pass but `_save_durations()` fails while writing the ignored `test_durations.json`, see `references/semantic-graph-hardening.md`, `references/canonical-runner-post-processing-failures.md`, and `references/test-runner-duration-cache-worktree.md`. Treat duration-cache persistence as best-effort: normalize the path, create the parent, catch `OSError`, and preserve the primary test result.

## Semantic retrieval / embedding verification

For incremental Semantic Graph lexical/dense retrieval work, preserve commit-scoped evidence rather than validating only the final branch. Record the base SHA and clean status before editing; write contract tests first and confirm a meaningful RED failure; keep each logical commit's boundary explicit; run the canonical runner after implementation and again after documentation or metric changes; and finish with lint, compile, diff/secret/path inspection, HEAD, and clean status.

Report per-class Recall@k/MRR and latency separately for identifiers, English/Japanese paraphrases, history/correction, and negatives. Distinguish candidate generation from final LLM context injection with `negative_wrong_memory_hit_rate` and `negative_context_injection_rate`. A candidate returned for a negative query is not itself proof that memory was injected.

For every hybrid retrieval increment, require zero rejected/superseded leakage in normal mode, zero cross-run leakage, zero secret-bearing recall, and zero retrieval-induced state mutation. Verify embedding-disabled and backend-failure paths preserve the lexical result. Keep targeted, CI, full-suite, live-provider, deployment, and production-readiness claims separate.

See `references/semantic-retrieval-verification.md` for the reusable evidence checklist and metric definitions.

## Completion criteria

- The requested package is installed or a precise blocker is reported.
- The reported regression has a focused test that passes, or an investigation-only task has a grounded production-versus-test classification.
- Related subsystem tests pass.
- Static checks pass when files were changed.
- Full-suite status is reported without overstating it.

For SQLite-backed Semantic Graph schema evolution and derived-embedding invalidation, see `references/semantic-graph-v2-migration-pattern.md`.
For float32-le embedding vector math, underflow-safe validation, two-stage normalization, model-identity boundaries, and exact cosine search isolation, see `references/semantic-graph-embedding-vector-math.md`.
