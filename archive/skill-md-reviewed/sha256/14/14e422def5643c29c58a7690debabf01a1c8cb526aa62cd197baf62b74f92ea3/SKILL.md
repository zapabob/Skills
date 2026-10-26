---
name: desktop-gui-scripting
description: Create lightweight Python desktop widgets when GUI automation is unavailable.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
tags: [desktop, python, tkinter, gui, widgets]
category: desktop
metadata:
  hermes:
    tags: [desktop, python, tkinter, gui, widgets]
    category: desktop
    related_skills: [computer-use]
---

# Desktop GUI Scripting Skill

This skill creates small native desktop utilities such as clocks, timers, overlays, and status widgets with Python's standard-library `tkinter`. It is a fallback for cases where direct desktop automation is unavailable; it does not replace `computer_use` for interacting with existing applications.

## When to Use

- The user asks for a simple desktop widget or overlay.
- The widget should run locally without a package installation.
- `computer_use` is unavailable or not suitable for creating the artifact.
- The user needs a persistent, always-on-top display with a simple exit path.

## Prerequisites

- Python with Tk support installed.
- A writable destination such as the user's Desktop.
- On Windows, prefer the launcher requested by the workspace convention (`py -3`) when available.

## How to Run

1. Create a standalone `.py` file with `tkinter` and no third-party dependencies.
2. Validate syntax before launch.
3. Launch it as a tracked long-running background process.
4. Confirm the process remains running; report the absolute file path and exit controls.

For the reusable skeleton, see `templates/desktop_widget.py`.
For the clock-specific implementation notes from the reference session, see `references/digital-clock.md`.

## Quick Reference

```python
root.attributes("-topmost", True)
root.attributes("-alpha", 0.90)
root.after(250, update)
root.bind("<Escape>", close)
root.protocol("WM_DELETE_WINDOW", close)
```

## Procedure

1. **Clarify the widget contract.** Identify what is displayed, whether it should stay above other windows, and how the user will close it.
2. **Keep the implementation self-contained.** Use `tkinter`, `datetime`, and other standard-library modules unless the user explicitly requests a richer framework.
3. **Design for visibility.** Use readable fonts, sufficient contrast, and conservative padding. Add date or secondary status only when useful.
4. **Add multiple exit paths.** Bind Escape, window close, and—when appropriate—a right-click context menu.
5. **Use an update loop correctly.** Schedule refreshes with `root.after()` rather than blocking with `sleep()` inside the UI thread.
6. **Write to an explicit path.** Prefer an absolute user-facing path, especially when the process will outlive the current shell.
7. **Validate and launch.** Run a syntax check, then launch from the script's directory or use an absolute path. Poll the background process to distinguish a live GUI from an immediate startup failure.
8. **Report operation.** Give the user the file path, current behavior, exit instructions, and optional customization points.

## Pitfalls

- **Relative-path launch failure:** A path such as `py -3 desktop_clock.py` only works when the working directory is the script directory. Use an absolute path or set `workdir` explicitly.
- **GUI lifetime:** A widget is intentionally long-running. Use a tracked background process with no completion notification, then poll once to verify it is still alive.
- **Automation fallback loop:** If `computer_use` repeatedly fails during initialization, do not keep retrying blindly; switch to a file-and-process workflow and mention the limitation accurately.
- **Tk update blocking:** Never use a tight loop or `time.sleep()` on the main thread; use `after()`.
- **Overlays and focus:** `-topmost` keeps the widget visible, but platform window managers may still affect focus. Keep a normal title bar unless the user explicitly wants a borderless overlay.
- **Transparency portability:** `-alpha` is optional and may vary by window manager; retain a readable opaque fallback.
- **Unverified visual claim:** Process liveness confirms the event loop started, not that the window is visible on the user's monitor. Avoid claiming a screenshot-level verification when desktop capture is unavailable.

## Verification

- Syntax validation returns success.
- The background process remains running after launch.
- The script has at least one timer callback and at least two clean exit paths.
- The final response contains an absolute artifact path and truthful verification scope.
- If visual confirmation is needed, use `computer_use` after the widget is launched or ask the user to confirm visibility.
