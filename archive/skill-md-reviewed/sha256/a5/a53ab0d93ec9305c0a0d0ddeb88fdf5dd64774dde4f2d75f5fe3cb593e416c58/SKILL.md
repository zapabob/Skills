---
name: airi-desktop-diagnostics
description: Use when AIRI reports healthy but no desktop window appears, OR the window renders but a subsystem is broken — blank icon panel (UnoCSS), chat that sends but gets no AI response, provider/auth errors, TTS, or window geometry.
category: Autonomous-ai-agents
version: 0.1.0
author: Hermes Curator
platforms: [windows]
metadata:
  hermes:
    tags: [AIRI, Electron, Windows, Debugging, CDP, Troubleshooting, chat, provider, icons]
---

# AIRI Desktop Diagnostics

Diagnose and fix AIRI desktop window rendering failures on Windows — when the worker reports `healthy: true` / `running: true` but the Electron/Vue window never appears on screen.

## When to Use

- User says "AIRI desktop is blank / not showing" or "動かないしうまくうつってない"
- User says the panel/buttons render but are blank white — "パネルが真っ白で何もない" or asks for icons (Scenario G: UnoCSS icon collections not resolving)
- User says "チャットで反応が返ってこない" / chat sends a message but no AI reply appears (Scenario H: chat request → Hermes not completing)
- `airi_status` reports `healthy: true` but the main window is absent
- CDP lists only `beat-sync.html` — the main `index.html` (Vue app) is missing
- The Electron process is running but no renderer target appears for the main app
- Need to distinguish "renderer crashed" from "renderer healthy but window hidden by show:false"

## Prerequisites

- Windows host with AIRI started (via `airi_start` or directly via `pnpm dev:tamagotchi`)
- CDP port 9455 accessible (`curl -s http://localhost:9455/json/list`)
- For WebSocket CDP inspection: Node.js v18+ (native `WebSocket` class)

## Diagnostic Flow

### 1. Check CDP Target List

```bash
curl -s http://localhost:9455/json/list
```

Interpret the targets:

| Target title | URL pattern | Meaning |
|---|---|---|
| `BeatSync - AIRI` | `beat-sync.html` | Background page — OK, shows worker is running |
| `localhost:5173/#/...` | `index.html` hash routes | **Main window** — this MUST exist. If absent, main renderer never started |
| `DevTools` | `devtools://...` | DevTools window — only appears with `MAIN_APP_DEBUG=1` |
| `...duckdb...worker.js` | Web Worker | Data processing engine — OK sign the app initialized |
| `(empty)` / unnamed | Worker | DuckDB or other — OK |

**If no main window target exists:** the Electron process's main window renderer creation failed. Stop AIRI, kill all `electron.exe`, and restart with `MAIN_APP_DEBUG=1` (see Debug Mode below).

### 2. Check Vite Dev Server

```bash
curl -s -m 5 http://localhost:5173/ | head -5
```

Should return the `index.html` with `<div id="app">` and `<script type="module" src="./main.ts">`. If this fails, the Vite dev server crashed — restart the whole process.

### 3. Check AIRI Electron Logs

Log files are at:
```
~/.hermes/airi/userdata/logs/airi-tamagotchi-*.log
```

Key pattern: look for `BEFORE RUN provide: windows:main()` followed by `RUN provide: windows:main() in Xs`. If X > 60 seconds, the main window renderer took very long to load (common: 170s in some sessions). If `RUN` never appears, the main window creation hung or threw.

### 4. Inspect Renderer via CDP WebSocket

If the main window target exists in CDP, connect directly to inspect console logs:

```bash
# Get the main page WebSocket URL
curl -s http://localhost:9455/json/list | node -e "
const http = require('http');
let data = '';
process.stdin.on('data', d => data += d);
process.stdin.on('end', () => {
    const targets = JSON.parse(data);
    const main = targets.find(t => t.url.includes('localhost:5173') && !t.url.includes('beat-sync'));
    console.log(main?.webSocketDebuggerUrl || 'NONE');
});
"
```

Then connect via Node.js native WebSocket:

```bash
node -e "
const WS_URL = 'ws://localhost:9455/devtools/page/...ID...';
const ws = new WebSocket(WS_URL);
const msgs = [];
ws.addEventListener('open', () => {
    ws.send(JSON.stringify({id:1, method:'Console.enable'}));
    ws.send(JSON.stringify({id:2, method:'Runtime.enable'}));
    ws.send(JSON.stringify({id:3, method:'Runtime.evaluate',
        params:{expression:'console.log(\"CDP_TEST\")'}}));
});
ws.addEventListener('message', (event) => {
    const msg = JSON.parse(event.data.toString());
    if (msg.method === 'Console.messageAdded')
        console.log('['+msg.params.message.level+']:', msg.params.message.text?.substring(0,300));
    if (msg.method === 'Runtime.consoleAPICalled')
        console.log('API ['+msg.params.type+']:',
            msg.params.args?.map(a => a.value ?? a.description ?? '').join(' ').substring(0,300));
    if (msg.id === 3) { setTimeout(() => ws.close(), 500); }
});
setTimeout(() => process.exit(1), 8000);
"
```

**Healthy renderer signs:**
- `🍍 "...store" installed 🆕` — Pinia stores register
- `PixiJS ... WebGL 2 ✰` — WebGL rendering works
- `Live2D Cubism SDK Core Version 5.0.0` — Live2D initialized
- `[vite] connected.` — HMR active
- Console warning about `[chat-sync] WS skipped: anonymous user` is normal before settings sync

**Unhealthy signs:**
- `Uncaught TypeError` or `ReferenceError`
- WebGL context creation failure
- Import errors from module resolution
- Endless loading spinners with no store initialization

## Debug Mode (MAIN_APP_DEBUG)

When the main window is absent from CDP or the window never appears despite healthy renderer logs:

1. Stop AIRI via `airi_stop`.
2. Kill remaining electron processes: `taskkill /F /IM electron.exe`
3. **Note**: `MAIN_APP_DEBUG=1` cannot be passed through `airi_start`. Start manually:
   ```bash
   cd /c/Users/downl/Documents/New\ project/hermes-agent/vendor/airi
   export MAIN_APP_DEBUG=1
   pnpm dev:tamagotchi -- --remote-debugging-port=9455 --remote-allow-origins=*
   ```
4. Wait 30-60s. Check CDP for a `DevTools` target page. The DevTools window opens detached on the desktop.
5. Once visible, inspect the Console tab for errors and Elements tab for Vue component mounting.
6. After debugging, stop the manual process and restart via `airi_start` for normal operation.

**Closing DevTools via CDP:** To close the detached DevTools window programmatically:
```bash
# Find the DevTools target ID from CDP target list
# Then connect and call window.close():
node -e "
const ws = new WebSocket('ws://localhost:9455/devtools/page/<DEVTOOLS_PAGE_ID>');
ws.addEventListener('open', () => {
    ws.send(JSON.stringify({id:1, method:'Runtime.evaluate', params:{expression:'window.close()'}}));
});
"

## Root Cause: show:false — ready-to-show Gap

The main window uses this pattern (in `setupMainWindow`):
```ts
const window = new BrowserWindow({ show: false, type: 'panel', ... })
window.on('ready-to-show', () => window!.show())
```

This means:
- The BrowserWindow is created but **invisible**
- It stays hidden until the renderer emits `ready-to-show`
- `ready-to-show` fires after the FIRST paint
- On Windows with `type: 'panel'`, the first paint may never fire if the page is still initializing
- With heavy initialization (Pinia stores, PixiJS WebGL 2, Live2D, DuckDB, plugin host), this can take 170+ seconds or never fire

**Healthy renderer but no window:** If CDP shows the main app target AND console inspection shows normal initialization (all stores, WebGL, Live2D), the issue is the `show: false` + `ready-to-show` gap. The window is created but never becomes visible.

**Workaround for diagnosis:** Start with `MAIN_APP_DEBUG=1` — the DevTools window opens regardless of `ready-to-show` and gives a visual anchor.

## Common Scenarios

### Scenario A: Only BeatSync in CDP, main window missing
Cause: The main window renderer process was never spawned. Check:
1. Log file ends at `BEFORE RUN windows:beat-sync()` — process hung during BeatSync init
2. Log shows `windows:main() took 170s+` — renderer crashed silently during load
3. No error overlay or DevTools — the error is masked by `show:false`

Fix: Stop AIRI, `taskkill /F /IM electron.exe`, restart with `MAIN_APP_DEBUG=1`.

### Scenario B: Healthy renderer logs but window invisible
Cause: `ready-to-show` event never fires because the page takes too long for first paint, or the paint is suppressed by `type: 'panel'` on Windows.

Diagnosis: CDP shows `localhost:5173/#/...` target. Node.js WebSocket inspection shows all stores + WebGL + Live2D initialized successfully.

Fix: Currently requires source modification (change `show: false` to `show: true` in `setupMainWindow`) or wait 170+ seconds. This is a known Electron + Windows panel window limitation.

### Scenario C: Renderer crashes with JavaScript error
Cause: Missing module, import resolution failure, unsupported API in Electron renderer.

Diagnosis: CDP WebSocket console inspection shows `Uncaught` errors.

Fix: Fix the import or module issue in the AIRI source code.

### Scenario D: cua-driver session dead
When `computer_use` keeps failing with `session has ended`:

**Try `list_windows` first (revives the session):**
```bash
computer_use(action='list_windows')
```
This often revives the dead session without needing to kill any processes. If the session was expired but the cua-driver process is still alive, `list_windows` re-establishes the connection for subsequent `capture` calls.

**If that fails:**
1. Check remaining cua-driver processes: `ps -W | grep -i cua`
2. Kill stale instances: `taskkill /F /IM cua-driver.exe`
3. If the main Hermes-owned cua-driver PID can't be killed (access denied), the tool stays broken until Hermes Desktop restarts
4. Fall back to browser tool and CDP WebSocket for screen-independent diagnosis

### Scenario E: Windows taskbar icon darkened/desaturated

When AIRI's window is visible but the taskbar icon appears dark, dimmed, or desaturated:

**Root cause:** The app icon (`resources/icon.png`) was a 1024×1024 RGBA PNG (color type 6). Windows taskbar has trouble rendering large RGBA PNGs with alpha, causing a desaturation/darkening effect.

**Diagnostic signal:** In the AIRI worker state (`~/.hermes/airi/worker-state.json`), look for:
```json
"icon": {
  "repaired": false,
  "png_color_type_before": 6,
  "mode_after": "ok"
}
```
`png_color_type_before: 6` = RGBA. `repaired: false` means the automatic color-mode fix didn't trigger because the icon was already RGBA.

**Fix:**
1. Check if a second, saved icon exists (common in the repo):
   ```
   ls -la vendor/airi/apps/stage-tamagotchi/resources/icon*.png
   ```
   Look for `icon-512.png` (512×512, Indexed color type 3 — no alpha).

2. If it exists, swap it in:
   ```bash
   cd vendor/airi/apps/stage-tamagotchi/resources
   cp icon.png icon.png.rgba-bak     # backup the large RGBA
   cp icon-512.png icon.png           # use the indexed version
   ```

3. Restart AIRI. The taskbar icon should now display at full brightness.

**Why this works:**
- `icon-512.png` uses PNG color type 3 (Indexed) — no alpha channel.
- Windows taskbar handles indexed/8-bit PNGs correctly.
- The actual icon content is identical; only the color encoding differs.

**Alternative:** Create a multi-resolution `.ico` file with proper Windows sizes (16×16, 32×32, 48×48, 256×256) for best compatibility.

### Scenario F: Window exists but is a collapsed strip (corrupted bounds in app-config.json)

**Symptom:** `airi_status` reports healthy, CDP shows the main page target, renderer is fully initialized (Vue mounted, stores loaded), but the window is invisible or appears as a thin sliver at the bottom of the screen. Windows API shows `TITLE=AIRI` with `VIS=False` (or a tiny RECT).

**Root cause:** `~/.hermes/airi/userdata/app-config.json` persists window bounds on every move/resize. A bad drag/resize (or multi-monitor change) can save absurd values, e.g. `{"windows":[{"title":"AIRI","tag":"main","x":218,"y":756,"width":1844,"height":39}]}` — wider than the screen and 39px tall, hidden behind the taskbar. The window is *shown* but effectively invisible.

**Diagnosis:**
```bash
cat ~/.hermes/airi/userdata/app-config.json
```
Look for `width`/`height` values that make no sense for the current monitor.

**Fix:**
1. Back up and reset the config:
   ```bash
   cp ~/.hermes/airi/userdata/app-config.json ~/.hermes/airi/userdata/app-config.json.bak-$(date +%Y%m%d-%H%M%S)
   echo '{"windows":[]}' > ~/.hermes/airi/userdata/app-config.json
   ```
2. Restart AIRI (`airi_stop` then `airi_start`).
3. Verify with `airi_status` (new PID) and Windows window enumeration: `TITLE=AIRI` should now be `VIS=True` with a sane RECT (default 450x600).

**Why this works:** `setupMainWindow` uses `mainWindowConfig?.width ?? 450.0` — with the corrupt entry removed, the window falls back to the default size/position.

**Note:** The window is created with `show: true` (fixed in commit 213437e4c) plus a `ready-to-show` handler, so a *missing* window after a fresh start is usually a renderer crash, not the show-gap. Check the collapsed-strip case above first when the renderer is healthy.

### Scenario G: Panel renders but icons are blank white boxes (UnoCSS presetIcons collections)

**Symptom:** Window and character (VRM) render fine, but the controls-island buttons are empty white circles — no icons. User reports 「パネルが真っ白で何もない」/ asks to "機能を記号化してアイコンに" (symbolize features as icons). The icons ARE declared in the Vue templates (`i-solar:settings-minimalistic-outline` etc.) but never paint.

**Root cause:** In the repo-root `uno.config.ts`, `presetIcons({ collections: { ... } })` — **specifying the `collections` option disables preset-icons' automatic `@iconify-json/*` resolution**. If only custom collections (`lobe-icons`, `iconify-meteocons`) are listed, every standard collection silently fails: `i-solar:` (used 541× in this codebase), `i-ph:`, `i-lucide:`, `i-carbon:` etc. generate ZERO CSS rules and render as empty boxes. No build error — it fails silently.

**Diagnosis (fast, no full rebuild):**
1. CDP DOM check — icon elements exist but have no mask:
   ```js
   // Runtime.evaluate on the main page target
   const el = document.querySelector('[i-solar\\:alt-arrow-up-line-duotone]')
   getComputedStyle(el).webkitMaskImage // 'none' => icon not painted
   ```
   Note: icons use **attributify** (`i-solar:xxx` as an attribute, not a class), so `querySelectorAll('[class*="i-solar"]')` finds nothing — match attributes via `[...el.attributes].some(a => a.name.startsWith('i-'))`.
2. Live stylesheet rule count (via CDP): count selectors containing `.i-solar` across `document.styleSheets` → `0` when broken.
3. Built CSS check: `grep -o "i-solar" out/renderer/assets/main-*.css` → 0 matches (custom collections like `lobe-icons` / `iconify-meteocons` WILL be present — confirms only standard resolution is dead).

**Fix:** add explicit `createExternalPackageIconLoader` entries for every standard collection used in the app, alongside the custom ones (keep in sync with `apps/stage-tamagotchi/package.json` devDependencies):
```ts
presetIcons({
  scale: 1.2,
  collections: {
    ...createExternalPackageIconLoader('@proj-airi/lobe-icons'),
    ...createExternalPackageIconLoader('@proj-airi/iconify-meteocons'),
    ...createExternalPackageIconLoader('@iconify-json/solar'),
    ...createExternalPackageIconLoader('@iconify-json/ph'),
    ...createExternalPackageIconLoader('@iconify-json/lucide'),
    ...createExternalPackageIconLoader('@iconify-json/simple-icons'),
    ...createExternalPackageIconLoader('@iconify-json/svg-spinners'),
    ...createExternalPackageIconLoader('@iconify-json/carbon'),
    ...createExternalPackageIconLoader('@iconify-json/eos-icons'),
    ...createExternalPackageIconLoader('@iconify-json/vscode-icons'),
    ...createExternalPackageIconLoader('@iconify-json/mingcute'),
    ...createExternalPackageIconLoader('@iconify-json/tabler'),
    ...createExternalPackageIconLoader('@iconify-json/material-symbols'),
    ...createExternalPackageIconLoader('@iconify-json/line-md'),
  },
}),
```

**Verification:**
- Rebuild, then count rules in the emitted CSS (minified = count matches, not lines): solar rules jump from 0 → ~138.
- Restart AIRI (Vite dev needs a full restart, page reload alone is not enough — the UnoCSS config is cached). Then CDP check: expanded panel shows `maskRendered` == total icon elements (13/13).
- Run `pnpm -F @proj-airi/stage-tamagotchi typecheck` and `pnpm lint` after touching `uno.config.ts`.

**Pitfall:** don't use `grep -c` on minified CSS to count rules — it counts *lines* (minified = 1). Use `grep -o ... | wc -l` or a Node regex `(css.match(/\\.i-solar[^,{]*\\{/g) || []).length`.

### Scenario H: Window + icons render, but chat gets no AI response

**Symptom:** AIRI desktop shows fine, controls-island icons paint, but typing in the chat box and pressing Enter shows the user message, then nothing — no assistant reply, or a toast/error like `No active chat provider or model configured`. CDP console shows `[chat-ws] ws error event` and/or `Error reading text stream: TypeError: Failed to fetch` from `@fs/.../packages/stage-ui/src/...`.

**Root-cause map (check in this order):**

1. **`No active chat provider or model configured`** — `localStorage['settings/consciousness/active-provider']` / `['settings/consciousness/active-model']` are empty. The `consciousness` Pinia store reads these; when empty, `executeIngest` throws before any network call. Cause: the `chat-sync` authority/follower lifecycle left the main (`#/`) window as a `follower` and no authority ever announced itself (or LocalStorage was wiped mid-debug). Fix: ensure the **main `#/` window is the authority** — open chat from the main window, or let the `chat-sync-lifecycle.ts` follower→authority fallback timer (5s) promote it. The CDP seed writes `openai-compatible` / `hermes-agent`, so after a clean `airi_stop`+`airi_start` these keys should be populated; verify with a CDP `Runtime.evaluate` reading `localStorage`.

2. **`Failed to fetch` / 401 on `POST http://127.0.0.1:8642/v1/chat/completions`** — the request reaches Hermes api_server but is unauthorized. The key used is `localStorage['settings/credentials/providers']['openai-compatible'].apiKey`, resolved at seed time from the `API_SERVER_KEY` env var the AIRI process inherited. If that key is stale/rotated, every chat request 401s (browser masks it as `Failed to fetch`). Verify the live key with a direct probe (see references file). Note: all processes in this setup share one `API_SERVER_KEY` (`hermes-airi-…`); if it 401s, the Hermes api_server key itself changed — restarting the api_server is the real fix, not editing AIRI.

**Fast diagnosis (no rebuild):** open the `#/chat` page over CDP, type + Enter, and watch `Network` for `POST .../v1/chat/completions`. A `200` with a rendered assistant bubble = working. A `401` + console `Failed to fetch` = key problem. See `references/chat-no-response-diagnosis.md` for the full CDP script recipe (target-ID discovery, localStorage key checks, the direct curl/node probe, and the authority-vs-follower pitfall).

**Pitfall — authority window:** `InteractiveArea.vue` `handleSend()` → `chatSyncStore.requestIngest()` runs `executeIngest` **locally only when `mode === 'authority'`**; a `follower` window dispatches a command to the authority window instead. If the authority window never initialized (e.g. you opened `#/chat` directly as the only window, or killed the main window), the follower command silently times out / errors. Always drive chat from the main `#/` window, or confirm the main window is alive in the CDP target list.

**Pitfall — reload wipes seeded state:** writing `localStorage` via CDP `Runtime.evaluate` and then calling `Page.reload` re-runs app init, which can reset `useLocalStorageManualReset` values back to empty if the provider wasn't also set in the credentials store. Set BOTH `settings/consciousness/active-provider`/`active-model` AND `settings/credentials/providers['openai-compatible'].apiKey`, then navigate (not reload) the chat route.

**Confirmed fix path (2026-07-31):** when Scenario H coincides with Scenario G (icons were also blank), the LocalStorage wipe from repeated restarts during icon debugging is the link. The confirmed fix is: (1) apply the `uno.config.ts` icon fix (Scenario G), (2) `airi_stop`, (3) back up and delete `~/.hermes/airi/userdata/Local Storage/leveldb` entirely, (4) `airi_start` — the CDP seed writes `openai-compatible` / `hermes-agent` and the correct `API_SERVER_KEY` into fresh LocalStorage, (5) open chat FROM the main `#/` window (NOT a standalone `#/chat` URL — the main window must be the authority), (6) CDP Network watch confirms `POST .../v1/chat/completions` → `200`, and the assistant bubble renders the AI reply. End-to-end success verified: Hermes replied「こんにちは、ボブにゃん。応答テスト、ちゃんと届いてるよ。何か手伝おうか？」.

## Provider/TTS Persistence and Crash Recovery

AIRI's provider settings are not proven by a provider file alone. After every start or recovery, verify the live Hermes `/v1/models` probe, CDP readback, and irodori health together. The canonical wiring is:

- AI: AIRI `openai-compatible` → Hermes `http://127.0.0.1:8642/v1/` → model `hermes-agent`
- Speech: AIRI `openai-compatible-audio-speech` → local irodori `/v1/` → model `irodori-tts`, voice `hakua`
- Seed credentials through CDP/localStorage merge; never replace the whole provider map and never print the API key.
- If AIRI crashes, run the existing start path again so provider/TTS sync and CDP readback happen as part of recovery.
- For unattended recovery, use a quiet no-agent watchdog at a short interval. It should start irodori first when its health endpoint is down, then start/reseed AIRI, emit output only on recovery/failure, and re-check final health.

See `references/provider-tts-auto-recovery.md` for the reusable recovery contract and verification recipe.

## Driving AIRI via ComputerUse (Windows)

`computer_use` CAN drive the AIRI desktop window, but the window is not auto-discovered: `list_windows` / `capture(app='AIRI')` fail because cua-driver does not resolve the Electron window title. You must supply BOTH `pid` and `window_id` explicitly.

**Locate the window (every restart rotates PIDs):**
1. Renderer PIDs = `wmic process where "name='electron.exe' and CommandLine like '%type=renderer%'" get ProcessId`.
2. Main PID = parent of any renderer: `wmic process where "ProcessId=<renderer>" get ParentProcessId`.
3. Window handle = `powershell -Command "Get-Process -Id <mainpid> | Select-Object MainWindowHandle, MainWindowTitle"`. Title should be `AIRI`, `MainWindowHandle` non-zero.
4. Then `computer_use(action='capture', pid=<mainpid>, window_id=<MainWindowHandle>)`.

**What works:**
- `capture(mode='som')` on the main window renders the avatar + control-island; vision confirms icons paint.
- Clicking control-island buttons (chat, expand) fires the Vue handler. Verify the effect via CDP `curl localhost:9455/json/list` — a click on the chat button moves the route to `#/chat` (a new `page` target appears). The SOM verdict `unverifiable` does NOT mean the click failed; trust the CDP target list.
- For chat send/receive verification, drive text via CDP `Runtime.evaluate` (set textarea value + dispatch Enter) on the `#/chat` target, then `Page.captureScreenshot` (call `Page.enable` first) to get a PNG of the conversation. CDP screenshot on the chat target works; the main-window handle still shows `#/`.

**Pitfalls:**
- `list_windows` omits AIRI — don't rely on it; compute the handle as above.
- `Page.captureScreenshot` times out if called before `Page.enable` or on a stale/unloaded target. Enable the domain, wait ~1.5s, then shoot.
- The main window handle is stable across in-window route changes, but the chat VIEW is a separate CDP `page` target — screenshot the `#/chat` target, not the main handle, to see messages.
- `find-win*.ps1` EnumWindows P/Invoke scripts that hardcode a PID return empty (Electron main owns the window but the enum doesn't surface it reliably); use `Get-Process -Id <mainpid> | Select MainWindowHandle` instead.

## Operational Pitfalls

### Local bridge CORS and preflight

When AIRI's renderer calls a local OpenAI-compatible bridge directly from `http://localhost:5173`, a successful server-side POST is not sufficient: the bridge must answer the browser's `OPTIONS` preflight and include `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`. Verify the exact route before testing audio generation:

```bash
curl -i -X OPTIONS http://127.0.0.1:8765/v1/audio/speech \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type, authorization"
```

Expected result: HTTP 204 and the three CORS headers. Then perform a real `POST` and validate the returned bytes are a WAV (`RIFF` at byte 0 and `WAVE` at byte 8), not merely HTTP 200.

### Long-lived process ownership

Repeated AIRI/bridge starts can leave child processes behind. Before a manual relaunch, terminate only matching command-line patterns (`hakua_tts_bridge`, `dev:tamagotchi`, `start_hakua_airi`) and verify ports 8765, 9455, and 5173. Do not kill every `electron.exe` unless the user explicitly authorizes broad process termination. Use `references/windows-process-cleanup.md` for the deterministic psutil wrapper.

### Environment propagation

`pnpm dev:tamagotchi` starts Electron through `electron-vite`; shell-local environment assumptions can be lost or differ from the process that owns the renderer. Use a wrapper that explicitly passes `env=os.environ` and sets the intended Hermes base URL/model and TTS provider before invoking `pnpm.cmd`. Do not print API keys. The live port/CDP probes are authoritative when `airi_status` contains stale worker-state from an earlier PID.

## References

- `references/electron-cdp-debugging.md` — detailed Node.js CDP WebSocket session traces and command examples
- `references/provider-tts-auto-recovery.md` — Hermes/irodori provider seed, crash recovery, watchdog, and secret-safe verification
- `references/chat-no-response-diagnosis.md` — Scenario H: CDP script recipe for diagnosing chat-no-response (target discovery, localStorage key checks, direct API probe, authority/follower pitfall)
- `references/windows-process-cleanup.md` — deterministic Windows cleanup and launch-wrapper recipe for preventing orphaned AIRI/TTS processes and preserving environment propagation
- `references/local-bridge-cors.md` — CORS preflight and real WAV response verification for browser-facing local bridges
