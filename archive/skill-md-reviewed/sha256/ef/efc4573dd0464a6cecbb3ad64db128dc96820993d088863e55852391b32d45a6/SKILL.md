---
name: airi-desktop-development
description: Use when implementing features in the AIRI Electron app.
version: 0.1.0
author: Hermes Curator
platforms: [windows]
metadata:
  hermes:
    tags: [AIRI, Electron, stage-tamagotchi, Eventa, IPC, TTS, i18n, feature-implementation]
---

# AIRI Desktop Development (stage-tamagotchi)

Implementing features in the AIRI Electron desktop app (`apps/stage-tamagotchi` in the `moeru-ai/airi` monorepo, vendored at `hermes-agent/vendor/airi`). Covers renderer↔main IPC patterns, local service access, UI entry points, and i18n.

## When to Use

- Adding a renderer feature that needs main-process capabilities (fetch to localhost services, fs, network)
- Wiring local TTS / audio playback into the chat or stage UI
- Adding controls-island buttons/toggles or settings entries
- Adding i18n keys for a new UI element
- Understanding why a renderer-side `fetch` to a local service fails

For **debugging** broken AIRI windows/icons/chat instead, use `airi-desktop-diagnostics`.

## Renderer Constraints (why IPC is required)

Measured in `apps/stage-tamagotchi` main window `webPreferences`:

- `sandbox: false`, preload present, **`nodeIntegration` disabled → no `fs`/`child_process` in renderer**
- CSP is commented out (no connect-src restriction) — but this does NOT grant CORS
- `webSecurity` default → `file://` audio playback from a dev `http` origin is blocked; **blob URL playback is the safe pattern**
- **Localhost services (irodori TTS :8088, Hermes API :8642) send NO CORS headers → renderer direct `fetch` is blocked.** The app standard is a main-process Eventa IPC bridge: main fetches → returns bytes → renderer plays.

## Eventa IPC Pattern (the app standard)

Contract file: `apps/stage-tamagotchi/src/shared/eventa/index.ts` — add with `defineInvokeEventa` from `@moeru/eventa`:

```ts
export const ttsSynthesize = defineInvokeEventa<Uint8Array, { text: string, voice: string }>('eventa:invoke:electron:tts:synthesize')
```

- Handler lives in main (`apps/stage-tamagotchi/src/main/services/electron/`); it fetches the local service and returns `Uint8Array` (structured-clone safe).
- Renderer side: `useElectronEventaInvoke(invoke)` from `@proj-airi/electron-vueuse` — **NO inject/context dependency** (resolves `window.electron.ipcRenderer` globally via `getElectronEventaContext()`), so it works directly **inside Pinia stores**, not just components. See `packages/electron-vueuse/src/composables/use-electron-eventa-context.ts`.
- Playback: main returns bytes → renderer `new Blob([bytes], { type: 'audio/wav' })` → `URL.createObjectURL` → `HTMLAudioElement`. Never try `file://` URLs.
- Real usage example: `apps/stage-tamagotchi/src/renderer/App.vue` (i18nGetLocale, electronGetServerChannelConfig, plugin events).

## Existing Speech Infrastructure (reuse, don't rebuild)

- `useSpeechStore` — `packages/stage-ui/src/stores/modules/speech.ts`. Provider-based TTS via `@xsai/generate-speech` (`generateSpeech`), voice lists, SSML, `speech()` returning `ArrayBuffer`. For cloud/OpenAI-compatible providers, not raw localhost.
- `useSpeechOutputControlStore` — `packages/stage-ui/src/stores/speech-output-control.ts`. `speechMuted` (localStorage `settings/speech/output-muted`) + `requestStopSpeaking(reason)` / `setSpeechMuted()` / `toggleSpeechMuted()`. **The mute flag a TTS hook must check before synthesizing.**
- Stop-speaking UI example: `apps/stage-tamagotchi/src/renderer/components/stage-islands/controls-island/controls-island-stop-speaking.vue` (ControlButton + ControlButtonTooltip + `useStopSpeakingButton`).

## UI Entry Points & i18n

- Controls-island: `apps/stage-tamagotchi/src/renderer/components/stage-islands/controls-island/index.vue` — buttons use Iconify attributify syntax (`i-solar:...`, `i-ph:...`, `i-carbon:...`).
- **Icons**: repo-root `uno.config.ts` `presetIcons.collections` disables automatic `@iconify-json/*` resolution — every standard collection used MUST have an explicit `createExternalPackageIconLoader('@iconify-json/<pkg>')` entry synced with `apps/stage-tamagotchi/package.json` devDependencies. Missing loader = blank icon box, silently (see `airi-desktop-diagnostics` Scenario G).
- **i18n**: 9 locales — `en es fr ja ko ru vi zh-Hans zh-Hant` — in `packages/i18n/src/locales/<locale>/tamagotchi/stage.yaml` under `'controls-island':`. Adding a UI string means adding the key to **all 9** files, not just ja/en.
- Settings pages: `apps/stage-tamagotchi/src/renderer/pages/settings/`, routes registered in `electron.vite.config.ts` / settings layout.

## Verification Commands

- `pnpm -F @proj-airi/stage-tamagotchi typecheck` (tsc + vue-tsc) — use the FULL package name; short forms can fail to resolve
- `pnpm lint` / `pnpm lint:fix` (formatting via ESLint)
- Targeted tests: `pnpm exec vitest run apps/stage-tamagotchi/src/renderer/stores/...`
- `pnpm -F @proj-airi/stage-tamagotchi build` (typecheck + electron-vite build)
- Live verification: CDP port 9455 (see `airi-desktop-diagnostics`) — `Page.enable` before `Page.captureScreenshot`; drive chat via `Runtime.evaluate` on the `#/chat` target.

## Hermes Gateway `/v1/runs` integration (AIRI chat ↔ Hermes agent)

When fusing AIRI's chat surface with the Hermes gateway's full agent run
(long-term memory + tools/skills), drive `POST /v1/runs` + `GET /v1/runs/{id}/events`
(SSE), NOT the stateless `/v1/chat/completions`. The **exact wire protocol differs
from OpenAI** and is easy to get wrong — read `references/hermes-gateway-runs-protocol.md`
before writing any client. Key traps: SSE frames are `data: ["event_name", {payload}]`
arrays (not `{"event":...}` objects); tool events use `message_id`/`tool_name`/`preview`/
`args`; and AIRI's `tool-error` StreamEvent reads `result` (not `error`). The `hermes`
provider + `streamViaHermesRun()` branch already exist in `packages/stage-ui`.

## References

- `references/local-tts-audio-pipeline.md` — irodori TTS measured endpoint/payload, the 400-encoding root cause, curl.exe MSYS path pitfall, and the chat TTS hook wiring plan
- `references/hermes-gateway-runs-protocol.md` — verified `/v1/runs` SSE contract: endpoints, request body, event catalog, and the 5 client-side mapping pitfalls that broke the first implementation
