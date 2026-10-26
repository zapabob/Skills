---
name: desktop-app-recovery
description: "Diagnose and recover desktop apps after failed updates."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, desktop-app, electron, state-recovery, troubleshooting]
    related_skills: [systematic-debugging]
    category: devops
---

# Desktop App Recovery

## Overview

This skill covers diagnosing and recovering desktop applications after failed updates, with a focus on Electron-based apps on Windows. It also includes standard rebuild and restart workflows for healthy Electron apps.

## Quick Rebuild Workflow

Use this when the desktop app needs a fresh build, not just recovery from a broken state.

1. `cd <app-dir>`
2. `npm run build`
3. Start the app with the project start command
4. Verify with process state instead of searching for terminal output on Windows GUI apps

## Common Pitfalls

- `electron` may not be on PATH; prefer the project npm script or `npx electron`
- Windows GUI apps launched from terminal typically produce no stdout
- Rebuilding does not guarantee the app is visible; confirm by process state if needed
- For Electron apps supervised through CDP, process presence alone is insufficient: verify the CDP endpoint, page target count, renderer URL, and any injected/read-back configuration.
- A newly started worker can briefly report `running: true` but `healthy: false` while the renderer is still starting. Re-check after the renderer settles; if the CDP target remains absent or configuration seeding fails, perform one controlled restart rather than repeatedly launching duplicate Electron processes.
- Keep dependent service liveness separate from UI configuration readiness. A synchronized provider/voice setting can be valid while its local server is offline; report those as separate checks.

### Electron Worker Verification Pattern

1. Check supervisor status before changing anything.
2. Start or restart only when `running`/`healthy` is false.
3. Verify the final state using process health, CDP page, positive target count, HTTP/auth probe, and configuration read-back.
4. Report optional dependent services separately from the core app result.
5. Do not declare success from a start command alone; require a final status probe.

## CDP-Based Renderer Inspection (when window is invisible)

When an Electron app launches (process exists, CDP responds) but the window is invisible:

1. **Check `/json/list` for all pages and workers** — the main window may simply not be in CDP, which means its webContents never registered (renderer crash before navigation, or main window creation failed).

   ```sh
   curl -s http://localhost:<cdp-port>/json/list
   ```

2. **Restart with DevTools forced open** — set `MAIN_APP_DEBUG=1` env var before launching. The Electron main process checks this in its window setup code; DevTools opens in detached mode, making the window visible and showing console errors.

   ```sh
   export MAIN_APP_DEBUG=1
   pnpm dev -- --remote-debugging-port=<cdp-port> --remote-allow-origins=*
   ```

3. **Attach to the renderer via CDP WebSocket** — use Node.js native `WebSocket` (v18+) to connect, enable Console/Runtime, and collect all buffered messages.

   ```js
   const ws = new WebSocket('ws://localhost:<port>/devtools/page/<page-id>');
   ws.addEventListener('open', () => {
     ws.send(JSON.stringify({id:1, method:'Console.enable'}));
     ws.send(JSON.stringify({id:2, method:'Runtime.enable'}));
     ws.send(JSON.stringify({id:3, method:'Runtime.evaluate',
       params:{expression:'document.title+"|"+document.body?.innerText?.substring(0,200)'}}));
   });
   ws.addEventListener('message', (event) => {
     const msg = JSON.parse(event.data.toString());
     if (msg.method === 'Console.messageAdded')
       console.log(msg.params.message.level, (msg.params.message.text||'').substring(0,300));
     if (msg.id === 3) { console.log('PAGE:', msg.result?.result?.value); ws.close(); }
   });
   ```

4. **Check framework mount** — inspect `window.__vue_app__` (Vue), `window.__NUXT__` (Nuxt), or `window.__NEXT_DATA__` (Next.js) via CDP `Runtime.evaluate`. If the framework mounted successfully, console logs will show store initialization messages (e.g. Pinia "store installed").

5. **Common `show: false` + `ready-to-show` pattern** — Electron apps that hide the window during load typically do:
   ```
   const win = new BrowserWindow({ show: false })
   win.on('ready-to-show', () => win.show())
   ```
   If the renderer initialization is slow (170+ seconds observed with Three.js/Live2D/PixiJS on Electron 41), `ready-to-show` may never fire or fire after a very long delay inside the `load()` promise. Workarounds:
   - Set `show: true` in constructor (accepts white flash)
   - Add a timeout fallback to show the window after N seconds regardless
   - In dev mode, DevTools opening (detached) often forces the window visible as a side effect

## Client Area of Electron Windows on Windows

Use this Python snippet (with `win32gui`) to detect whether an Electron `BrowserWindow` exists and is visible on screen, independent of CDP or process list:

```python
import win32gui, win32process, psutil
app_pids = {p.info['pid'] for p in psutil.process_iter(['pid','name'])
            if p.info['name'] and 'myapp' in p.info['name'].lower()}
def enum_cb(hwnd, _):
    cls = win32gui.GetClassName(hwnd)
    if cls in ('Chrome_WidgetWin_1', 'Chrome_WidgetWin_0'):
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in app_pids:
            print(f'hWnd={hwnd} PID={pid} visible={win32gui.IsWindowVisible(hwnd)} '
                  f'rect={win32gui.GetWindowRect(hwnd)} text="{win32gui.GetWindowText(hwnd)}"')
win32gui.EnumWindows(enum_cb, None)
```

## References

- `references/electron-windows-rebuild.md` — Windows Electron rebuild/start verification notes
- `references/electron-window-never-appears.md` — Detection technique for headless renderers
- `references/airi-desktop-window-troubleshooting.md` — AIRI-specific: beat-sync only, main window missing, 170s init delay, CDP-seeded renderer