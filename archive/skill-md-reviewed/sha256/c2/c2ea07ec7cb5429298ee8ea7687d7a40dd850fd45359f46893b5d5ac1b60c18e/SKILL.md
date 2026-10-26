---
name: world-monitor-computer-use
description: Operate the local World Monitor desktop app through Hermes computer_use/cua-driver, especially when the user asks to open World Monitor, inspect the dashboard, search a country, or produce an OSINT/Japan brief without using a World Monitor MCP/server path. Covers Windows foreground-lock workarounds, direct pid/window_id background dispatch, evidence screenshots, and concise extraction of visible dashboard signals.
---

# World Monitor via computer_use

Use this skill for local World Monitor desktop operations. Prefer `computer_use` / `tools.computer_use.cua_backend.CuaDriverBackend` over any World Monitor MCP path.

## Operating policy

- Use the desktop app, not a World Monitor MCP/server integration.
- Do not use DesktopCompanion `--currently-open-config` for World Monitor.
- Treat `.env`/API keys as out of scope; report only visible dashboard content and safe local execution evidence.
- Save screenshots under `_docs/` when the task needs proof or OCR.

## Windows launch path

Default executable:

```text
%USERPROFILE%\AppData\Local\Programs\World Monitor\world-monitor.exe
```

The app may need 8–12 seconds after launch before the dashboard content appears. A black window with only File/Edit/Help usually means "wait and recapture", not failure.

## Reliable capture pattern

Use one `CuaDriverBackend` session and keep it open until the operation is done. `b.stop()` can end the driver session and the launched app may disappear.

```python
from tools.computer_use.cua_backend import CuaDriverBackend, _image_from_tool_result, _parse_elements_from_structured
from pathlib import Path
import base64, time

exe = r"%USERPROFILE%\AppData\Local\Programs\World Monitor\world-monitor.exe"
out = Path("_docs/world_monitor_capture.png")

b = CuaDriverBackend()
b.start()
try:
    launch = b.launch_app(name=exe)
    pid = int(launch["pid"])
    win = int((launch.get("windows") or [{}])[0]["window_id"])
    time.sleep(10)
    gws = b._session.call_tool("get_window_state", {"pid": pid, "window_id": win, "session": b._session_id})
    png_b64, _ = _image_from_tool_result(gws)
    elems = _parse_elements_from_structured((gws.get("structuredContent") or {}).get("elements") or [])
    if png_b64:
        out.parent.mkdir(exist_ok=True)
        out.write_bytes(base64.b64decode(png_b64))
finally:
    b.stop()
```

## Background dispatch workaround

On Windows, `bring_to_front` can fail with foreground-lock denial. Do not fight it. Use cua-driver tools with explicit `pid`, `window_id`, and `dispatch: background`.

Search for Japan and open the country brief:

```python
# after obtaining pid, win, and a fresh get_window_state snapshot
search = next(e for e in elems if "検索" in (e.label or "") or "search" in (e.label or "").lower())
b._session.call_tool("click", {
    "pid": pid, "window_id": win, "element_index": search.index,
    "button": "left", "count": 1, "dispatch": "background",
})
time.sleep(1)
b._session.call_tool("type_text", {"pid": pid, "window_id": win, "text": "Japan", "dispatch": "background"})
b._session.call_tool("press_key", {"pid": pid, "window_id": win, "key": "return", "dispatch": "background"})
time.sleep(2)

# Recapture and click "Open Japan brief".
gws = b._session.call_tool("get_window_state", {"pid": pid, "window_id": win, "session": b._session_id})
elems = _parse_elements_from_structured((gws.get("structuredContent") or {}).get("elements") or [])
target = next((e for e in elems if "Open Japan brief" in (e.label or "")), None)
if target:
    b._session.call_tool("click", {
        "pid": pid, "window_id": win, "element_index": target.index,
        "button": "left", "count": 1, "dispatch": "background",
    })
```

## Extraction checklist

For a country brief, extract only visible, non-secret UI content:

- Country/status line, e.g. `JP Japan`, `低 → 安定`.
- Instability score and category scores.
- Active signals and 7-day timeline markers.
- Intelligence brief bullets.
- Top news headlines and source/time.
- Forecast-market question and odds, if visible.
- Infrastructure exposure: cables, data centers, military bases, ports, etc.
- Screenshot path used as evidence.

## Pitfalls

- `capture(app="world-monitor.exe")` may not match; app/window names are not stable. Prefer launch-result `pid/window_id`.
- If the frontmost app is ChatGPT/Hermes, plain `capture()` will capture the wrong window. Always target the launched World Monitor window directly.
- Search click by raw screen coordinates is fragile. Prefer the structured element whose label contains `検索` or `search`.
- If the search modal remains open after pressing Enter, recapture and click `Open Japan brief` or the first `Japan` result by element index.
- Keep final reports concise and grounded in captured UI/OCR; do not invent World Monitor data that was not visible.
