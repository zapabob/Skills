---
name: npm-monorepo-verification
description: Verify npm workspaces post-ci or upstream lockfile merge.
---

# npm-monorepo-verification

Use when a JS/TS project uses npm **workspaces** (`"workspaces": ["packages/*","apps/*"]`) and you must confirm it still builds/tests/lints before merging an upstream `package-lock.json`, or after `node_modules` is absent and you ran `npm ci`.

## When to use
- Upstream adopted/changed `package-lock.json` and you must integrate → run the full verification before declaring done.
- Fresh checkout / CI image with no `node_modules`.
- A previous "build/lint/test unverified" status needs closing with real evidence.

## Steps
1. **Install reproducibly** from the lockfile (NOT `npm install`):
   `npm ci` — fails if the lockfile is out of sync with `package.json`; that mismatch is itself a finding.
2. **Inventory scripts per workspace** before running, so you know what exists:
   `for d in packages/* apps/*; do test -f "$d/package.json" && node -e "const p=require('./$d/package.json'); console.log(p.name, JSON.stringify(p.scripts||{}))"; done`
3. **Run build/lint/test across all workspaces** with `--if-present` so missing scripts don't abort:
   `npm run build --workspaces --if-present`
   `npm run lint  --workspaces --if-present`
   `npm run test  --workspaces --if-present`
   `--workspaces` aggregates; a single workspace failure makes the whole command exit non-zero. Capture per-workspace output.
4. **Triage failures**: separate "real code break" from "environment/tooling break" (see Pitfalls).

## Pitfalls
### npm install-scripts gating (this machine)
`npm ci` may emit: `N packages had install scripts blocked because they are not covered by allowScripts`.
Native/postinstall binary fetches are SKIPPED for: `electron`, `sharp`, `puppeteer`, `onnxruntime-node`, `keytar`, `node-pty`, `msgpackr-extract`, `native-keymap`, `drivelist`, `@theia/ffmpeg`, `@parcel/watcher`, `@vscode/windows-ca-certs`, `@google/genai`.
Consequence: any workspace `build`/`test` needing those binaries (e.g. Theia/electron `apps/shell`, `sharp` image ops, `puppeteer` e2e) FAILS not because of code but because the binary was never fetched.
**Not all tools break** — `esbuild` still works because the platform binary ships inside `@esbuild/<platform>` (e.g. `@esbuild/win32-x64`); its `postinstall` is only a fallback. Verify with `node_modules/.bin/esbuild --version` (returns a version) and `ls node_modules/@esbuild/`. If the platform package dir exists, the tool is functional despite the warning.
**Diagnostic BEFORE concluding "broken"**: for each suspected tool run `<tool> --version` / `ls node_modules/@<scope>/<platform>`. If the platform package dir exists, the tool is functional despite the warning.
**Fix** (when you actually need the native dep): `npm install-scripts approve <pkg>` then `npm rebuild <pkg>` (or re-run `npm ci`). See references/npm-install-scripts-gating.md.

### Local `.npmrc` `allow-scripts=true` workaround
For a **local-only** development machine where you control the environment, adding `allow-scripts=true` to `.npmrc` (gitignored or untracked) lets `npm ci` run all install scripts. This is a machine-level choice, NOT a repo-level fix — do not commit it to the repo.
- After adding `.npmrc`, re-run `npm ci` or `npm rebuild <pkg>` for specific packages (e.g. `electron`, `@theia/ffmpeg`).
- Remember: this is a **local development convenience only**. Upstream CI must still handle install-scripts via explicit `npm install-scripts approve <pkg>` in the pipeline.

### npm run test hangs (bash pipe delay)
`npm run test --workspaces --if-present` can hang for 30+ minutes on Windows when run via `bash | tail` — the pipe buffers stdout and the process never terminates visibly. **Mitigation:** run `npm run test -- --` (add `--` to terminate npm options parsing) or run individual workspace tests (`npm run test --workspace=<name>`). For parallel builds, run lint and test in parallel; if either hangs >10 min, kill and retry per-workspace.

### Root has no build/lint/test
The root `package.json` often only declares `workspaces` + a few helper scripts. Do NOT run `npm run build` at root expecting the whole monorepo — use `--workspaces --if-present`.

### Windows path gotchas
- Run from git-bash with POSIX paths (`/c/Users/downl/...`); here `node` is v24.x, `npm` 12.x.
- Theia/electron builds pull `node-gyp` native deps → expect long runtimes + a C++ toolchain.
- `node` invoked from git-bash may resolve `process.cwd()` paths differently than raw Windows paths (e.g. `/c/Users/...` → `C:\c\Users\...` inside `resolve()`). Prefer `process.cwd()` over hardcoded paths in verification scripts.

### npm run test hangs (bash pipe delay)
`npm run test --workspaces --if-present` can hang for 30+ minutes on Windows when run via `bash | tail` — the pipe buffers stdout and the process never terminates visibly. **Mitigation:** run `npm run test -- --` (add `--` to terminate npm options parsing) or run individual workspace tests (`npm run test --workspace=<name>`). For parallel builds, run lint and test in parallel; if either hangs >10 min, kill and retry per-workspace.

## Verification evidence to keep
For each workspace: script name, exit code, first/last output lines. Record which failures are real vs gating-induced. Save to `_docs/YYYY-MM-DD_<topic>_<agent>.md` per the project AGENTS.md convention.

## References
- references/npm-install-scripts-gating.md — full blocked-package list, diagnostic commands, approve/rebuild fix.
- references/windows-symlink-fallback-pattern.md — 3-tier symlink fallback for workspace `file:` deps (symlink → mklink /J → xcopy).
- references/local-npmrc-allow-scripts.md — local `.npmrc` `allow-scripts=true` workaround for local development.
