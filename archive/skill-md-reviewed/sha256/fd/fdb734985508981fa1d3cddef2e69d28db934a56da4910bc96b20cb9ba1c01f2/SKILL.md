---
name: desktop-dashboard-widgets
description: Build lightweight tkinter desktop dashboards with live data, clocks, and i18n.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [tkinter, desktop, dashboard, clock, weather, trends, i18n]
    category: desktop
    related_skills: [computer-use]
---

# Desktop Dashboard Widgets Skill

Build small, always-on-top desktop dashboards with Python's standard-library tkinter. This skill covers digital and analog clocks, weather panels, public trend feeds, AI-related feeds, i18n, background refresh, and lifecycle handling. It does not replace native desktop automation; use `computer_use` for driving an existing GUI.

## When to Use

- The user wants a desktop clock, widget, or glanceable dashboard.
- Multiple public data sources should appear in one persistent window.
- The UI needs Japanese/English switching or another lightweight i18n layer.
- The clock must follow the computer's current system time and timezone.

## Prerequisites

- Python with tkinter available.
- On Windows, prefer the `py -3` launcher.
- Public endpoints should be key-free where possible; secrets belong in `.env`, never in source.
- For long-lived GUI processes, use `terminal` with `background=true`.

## How to Run

1. Write the application to a user-visible location such as the Desktop.
2. Compile first: `py -3 -m py_compile dashboard.py`.
3. Run from the script's own directory: `py -3 dashboard.py`.
4. For live data, test each endpoint independently before debugging the GUI.
5. Verify the process remains running and provide explicit close/restart instructions.

## Quick Reference

| Concern | Recommended pattern |
|---|---|
| System clock | `datetime.now().astimezone().tzinfo` |
| UI tick | `root.after(250, update_clock)` |
| Network fetch | daemon worker thread |
| Worker → UI | `root.after(0, lambda: var.set(value))` |
| Weather | Open-Meteo forecast endpoint |
| Japan trends | Public trends page with fallback |
| AI trends | Hugging Face Daily Papers API |
| i18n | `TRANSLATIONS` dict + `t(key)` |
| Refresh safety | Store and cancel the `after` timer id |

## Procedure

### 1. Establish the location and time contract

Ask for the city if it is not known. For a location-specific weather panel, store city name plus latitude and longitude. For the clock, use the operating system's current time and timezone unless the user explicitly requests a fixed timezone:

```python
self.tz = datetime.now().astimezone().tzinfo
self.local_tz_name = self.tz.tzname(datetime.now()) if self.tz else "UTC"
now = datetime.now(self.tz)
```

Do not hardcode `ZoneInfo("Asia/Tokyo")` when the user asks to synchronize with the time currently used by the machine. Use the requested location's timezone only for the weather API query if needed.

### 2. Build the window and panels

Use a `Tk` root, `-topmost` for an always-on-top widget, and optional `-alpha` transparency. Use frames with stable references to each panel and label. Import tkinter geometry constants explicitly (`BOTH`, `LEFT`, `RIGHT`, `X`) rather than relying on implicit names.

### 3. Implement digital and analog clocks

The digital clock should update at least once per second; 250 ms gives a smooth second transition. For a Canvas analog clock, use these angles, with `-90` degrees so 12 o'clock points upward:

- Hour: `((hour % 12) + minute / 60) * 30`
- Minute: `(minute + second / 60) * 6`
- Second: `second * 6`

The hour hand is a common copy/paste bug: it uses 30 degrees/hour, not 6.

### 4. Fetch data without freezing tkinter

Never perform network I/O in the tkinter main loop. Start one daemon thread per independent source, catch errors, and update StringVars on the main thread:

```python
def set_var(self, variable, value):
    self.root.after(0, lambda: variable.set(value))

threading.Thread(target=self.fetch_weather, daemon=True).start()
```

Set a `User-Agent` header in urllib requests. Use bounded timeouts and show a localized fallback string if a source is unavailable.

### 5. Use resilient public sources

For weather, Open-Meteo is a practical no-key source. For Japan X trends, a public trends page can be used as a best-effort fallback, but it is not equivalent to the official X API and its markup may change. For AI-related trends, Hugging Face Daily Papers provides a useful public feed of recent ML/AI paper titles. Keep parsing conservative and never claim official X API data when it was not used.

See `references/data-sources.md` for endpoints and response fields.

### 6. Add i18n

Default to Japanese for this workspace. Keep visible labels and fallback messages in a `TRANSLATIONS` dictionary, expose a `t(key)` helper, and refresh panel headings when the language toggles. Avoid mixing hardcoded English into the Japanese path except for technical identifiers such as timezone names.

### 7. Make refresh and shutdown safe

Manual refresh plus scheduled refresh can accidentally stack timers. Keep the timer id:

```python
if self._refresh_timer_id:
    self.root.after_cancel(self._refresh_timer_id)
self._refresh_timer_id = self.root.after(REFRESH_MS, self.refresh_all)
```

Cancel the timer in `close()` before destroying the root. Bind both Escape and a visible context-menu or right-click action to close the window.

### 8. Verify the real path

Run syntax compilation, then run the GUI. Separately probe each endpoint and inspect parsed values. Confirm the process remains alive rather than treating a background launch with exit code 0 as proof that a GUI is visible. If GUI capture is unavailable, report that limitation honestly and provide the exact file and command for the user to inspect.

## Pitfalls

- **Wrong working directory on Windows shell wrappers:** run `py -3 dashboard.py` from the directory containing the file; passing an absolute path from an unrelated working directory can be mangled by a bash-style wrapper.
- **Missing tkinter constants:** `RIGHT`, `BOTH`, `LEFT`, or `X` may fail at layout time with `NameError`; import them explicitly.
- **Timer leaks:** do not schedule another refresh without cancelling the prior timer.
- **Thread-unsafe UI updates:** worker threads must call `root.after(0, ...)`, not mutate widgets directly.
- **Analog hour hand:** use 30 degrees per hour and include the minute fraction.
- **Fragile trend scraping:** always provide a fallback notice and label unofficial/public scraping accurately.
- **Dead panel variables:** store the label/StringVar reference when building a panel; do not create a throwaway `StringVar` and later expect to retrieve it reliably.
- **Stale location copy:** update comments, labels, and help text when changing the city; do not leave the previous city name in user-facing text.
- **Language race:** workers may finish after a language toggle; keep results data-oriented and refresh after toggling, or tag requests with the active language.

## Verification

- `py -3 -m py_compile dashboard.py` exits successfully.
- Weather endpoint returns current data for the requested coordinates.
- Trend endpoint either produces a non-empty list or the localized fallback appears.
- AI feed produces titles or a localized fallback appears.
- Digital and analog clocks agree with the OS clock and timezone.
- Manual refresh does not multiply callbacks.
- Escape/right-click closes the process cleanly.
- Final response includes the exact path, launch command, close method, data-source caveat, and whether live endpoint probes succeeded.

## Supporting Files

- `references/data-sources.md` — endpoint contracts, parsing notes, and attribution caveats.
- `templates/tkinter-dashboard.py` — compact starter skeleton for future dashboards.
