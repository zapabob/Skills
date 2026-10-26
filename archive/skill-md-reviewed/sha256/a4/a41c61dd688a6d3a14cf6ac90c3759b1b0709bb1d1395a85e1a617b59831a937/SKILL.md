---
name: kanban-db-resolution
description: Fix for Hermes Kanban database PATH resolution issues on Windows
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [kanban, devops, windows, path-resolution]
    related_skills: [hermes-agent]
---

# Kanban DB Resolution Fix

## When to Use

Use this knowledge when encountering issues with Hermes Kanban database resolution, particularly related to the `_resolve_hermes_argv` function in `hermes_cli/kanban_db.py`. Symptoms include failing tests like `test_resolve_hermes_argv_prefers_path_shim`, Kanban worker spawning problems, or incorrect Hermes executable being used.

## Problem

The original implementation of `_safe_which_no_cwd` used platform-specific logic: on Windows it used a custom path traversal that respected PATHEXT, while on Unix it used `shutil.which`. This inconsistency caused unit tests that mocked `shutil.which` to fail on Windows because the mock was not used in the Windows branch.

Additionally, the manual path traversal could miss edge cases and was more complex than necessary.

## Solution

Refactor `_safe_which_no_cwd` to use `shutil.which` consistently across all platforms, while still preventing the current-directory hijack issue by temporarily filtering out empty and `.` entries from the `PATH` environment variable.

Also, make `_resolve_hermes_argv` consistently use `_safe_which_no_cwd` on all platforms, removing the conditional that used `shutil.which` directly on non-Windows systems.

## Fix Details

### Changes to `hermes_cli/kanban_db.py`:

1. **Updated `_safe_which_no_cwd`**:
   - Filters out empty and `"."` entries from `PATH`
   - Temporarily replaces `PATH` with the filtered list
   - Delegates to `shutil.which` to find the executable
   - Restores original `PATH` afterwards

2. **Updated `_resolve_hermes_argv`**:
   - Removed the platform-specific branch (`if _IS_WINDOWS else shutil.which`)
   - Now consistently calls `_safe_which_no_cwd("hermes")` for all platforms
   - Preserves the batch-shim safety check in `_hermes_path_argv`

### Benefits:
- Consistent behavior across platforms
- Unit tests that mock `shutil.which` now pass on Windows
- Maintains protection against current-directory hijacking
- Preserves batch-shim avoidance for Windows `.cmd`/`.bat` files
- Simpler, more maintainable code

## Verification

After applying the fix, the following tests should pass:
- `test_resolve_hermes_argv_prefers_path_shim`
- `test_resolve_hermes_argv_falls_back_to_module_form_when_no_path_shim`
- Other related PATH resolution tests in `tests/hermes_cli/test_kanban_db.py`

## References

- See the commit that introduced this fix in the Hermes agent repository.
- Related discussion in issue #XXXXX (if applicable).