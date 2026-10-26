---
name: hermes-debugging
description: Techniques for debugging and fixing issues in the Hermes codebase.
category: devops
---

# Hermes Debugging

## Overview
This skill provides techniques for debugging and fixing issues in the Hermes codebase, particularly those related to platform-specific behavior, testing, and integration.

## When to Use
- When encountering test failures that are platform-specific (e.g., Windows vs. Unix).
- When debugging issues related to command resolution, PATH handling, or subprocess execution.
- When fixing issues in the Hermes CLI, gateway, or core agent logic.

## Key Techniques

### 1. Handling Platform-Specific Code in Tests
When writing or debugging code that behaves differently on Windows and Unix (e.g., using `shutil.which`), ensure that:
- Platform-specific logic is isolated and testable.
- Tests that mock functions like `shutil.which` should account for platform branches.
- Consider using a unified helper function (like `_safe_which_no_cwd`) that works across platforms and can be mocked in tests.

### 2. Fixing PATH-Related Issues
When a function searches the PATH for an executable:
- Avoid relying on the current directory being in the PATH for security and predictability.
- Filter out empty and `.` entries from the PATH before searching.
- Use `shutil.which` as the base implementation and wrap it to filter the PATH if needed.
- On Windows, be cautious of batch/shim files (`.cmd`, `.bat`) that may not be safe to use directly as `argv[0]` in subprocesses.

### 3. Handling Absolute Paths on Windows
Windows treats paths starting with a forward slash (e.g., `/usr/bin/hermes`) as relative to the current drive. To handle such paths:
- Check if the path starts with `/` and the system is Windows.
- Treat such paths as absolute (do not convert them to relative or prepend the current drive).
- Use `os.path.isabs()` after expansion, but note that it returns `False` for `/path` on Windows. Adjust accordingly.

### 4. Classify Windows test-environment failures before fixing production
When focused Windows tests fail around filesystem links or terminal rendering, distinguish test capability from product behavior before proposing changes:

- **Symlink creation failures (`WinError 1314`)** are usually test precondition failures when production only consumes or canonicalizes existing links. Use a capability-based guard around link creation rather than skipping all Windows runs; Developer Mode or elevation may allow the test to run.
- Directory links must use `target_is_directory=True`. Catch only creation-time `OSError`/`NotImplementedError`, and ensure `pytest` is imported before calling `pytest.skip()`.
- Do not weaken production `resolve()`/`realpath()` behavior merely to accommodate an unprivileged test host.
- **`prompt_toolkit` no-console errors** may expose a real product robustness bug. Reproduce the display helper outside pytest. If it also fails in a supported no-console process, add a regression test and a best-effort plain-output fallback instead of globally suppressing display calls in conftest.
- A `DummyOutput` app-session fixture is not sufficient for callbacks running in new threads because `ContextVar` state does not necessarily propagate. Prefer fixing the production display boundary; for a pure unit test, a narrow patch of that test's display collaborator is safer than a suite-wide fixture.

A useful no-edit confirmation technique is to inject a narrowly scoped runtime guard or display stub, rerun the focused file, and verify that only the unavailable capability skips while all behavioral assertions pass. See `references/windows-symlink-and-no-console-tests.md`.

### 5. Verifying Fixes with Tests
After making changes:
- Run the specific failing test to ensure it passes.
- Run the full test suite for the modified module to ensure no regressions.
- Use `pytest -v` to see detailed output and identify any new warnings or errors.

## Example: Fixing `kanban_db.py` Test Failure
### Problem
The test `test_resolve_hermes_argv_prefers_path_shim` failed on Windows because:
- `_resolve_hermes_argv` used `_safe_which_no_cwd` on Windows and `shutil.which` on Unix.
- The test monkeypatched `shutil.which`, which was bypassed on Windows.

### Solution
1. Refactored `_safe_which_no_cwd` to work on all platforms by filtering the PATH and delegating to `shutil.which`.
2. Changed `_resolve_hermes_argv` to always use `_safe_which_no_cwd` (removing the platform branch).
3. Fixed `_absolute_hermes_path` to treat POSIX-style absolute paths (starting with `/`) as absolute on Windows.

### Steps
1. Identified the platform-specific branch in `_resolve_hermes_argv`.
2. Replaced it with a unified call to `_safe_which_no_cwd`.
3. Updated `_safe_which_no_cwd` to filter out empty and `.` entries from PATH before calling `shutil.which`.
4. Adjusted `_absolute_hermes_path` to handle `/`-prefixed paths on Windows.
5. Verified the fix with the failing test and the full test suite.

## 6. Diagnosing Windows Environment Variable Corruption (CRLF in PATH/Env)

When Windows environment variables contain carriage return (`\r`) characters, path resolution fails with confusing errors. This commonly happens when tools or installers write variables with CRLF line endings.

**Common symptoms:**
- `SSL_CERT_FILE` points to a missing file: `C:\Users\user\certs\bundle.pem` (with trailing `\r`)
- Subprocess calls fail with "file not found" for paths that exist
- `os.environ['VAR']` shows correct value but the actual system call fails

**Detection:**
```python
import winreg
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_QUERY_VALUE)
val = winreg.QueryValueEx(key, 'SSL_CERT_FILE')[0]
print(repr(val))  # 'C:\\Users\\...\\bundle.pem\\r' if corrupted
```

**Fix via registry (removes CR):**
```python
import winreg
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_SET_VALUE)
val = winreg.QueryValueEx(key, 'SSL_CERT_FILE')[0]
val = val.replace('\r', '').replace('\n', '')
winreg.SetValueEx(key, 'SSL_CERT_FILE', 0, winreg.REG_SZ, val)
winreg.CloseKey(key)
```

**PowerShell alternative:**
```powershell
$val = (Get-ItemProperty -Path 'HKCU:\Environment' -Name 'SSL_CERT_FILE').SSL_CERT_FILE
$val = $val -replace "`r", '' -replace "`n", ''
Set-ItemProperty -Path 'HKCU:\Environment' -Name 'SSL_CERT_FILE' -Value $val
```

**Prevention:** Always use `winreg` or `ctypes.windll.shell32.SetEnvironmentVariableW` to write Windows env vars from Python. Never redirect bash-style strings (from WSL/Git Bash) directly into the Windows registry — the CRLF from POSIX tools corrupts the value.

## References
- See `references/kanban_db_fix.md` for the detailed patch and test output.
- See `references/windows-env-var-corruption.md` for CRLF diagnosis toolkit and PowerShell snippets.