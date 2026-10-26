---
name: windows-codex-chrome-computer-use-recovery
description: Use when Chrome Plugin or Computer Use is unavailable in Codex on this Windows PC and the user wants the real blocker diagnosed or a minimal verification-only proof path.
argument-hint: "[workspace-path]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Windows Codex Chrome Plugin / Computer Use Recovery

## When to use

Use this on this Windows Codex machine when:
- Chrome Plugin is installed but not usable
- Computer Use fails to bootstrap
- the user asks why Chrome / Computer Use cannot be used
- the user wants a trusted-workspace retest after some separate local change
- the user wants read-only proof without exposing browser tab details or Windows app details

Non-goals:
- dumping sensitive Chrome tab titles, URLs, cookies, or local-storage state
- opening or operating Windows apps unless the user explicitly asks for it
- broad recursive scans across the whole user profile when bundled check scripts already exist
- assuming an old repair path is still valid before the current diagnosis proves it

## Inputs / context to gather

1. Confirm the relevant Codex surfaces.
- `%USERPROFILE%\.codex\config.toml`
- `%USERPROFILE%\.codex\plugins\cache\openai-bundled\computer-use\26.608.12217\scripts\computer-use-client.mjs`
- `%USERPROFILE%\AppData\Local\OpenAI\Codex\chrome-plugin-host\26.608.12217`

2. Confirm the expected Chrome/native-host identity.
- Chrome binary: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- extension ID on this machine: `hehggadaopoacecdllhhajmbjkdcmajg`
- native-host name: `com.openai.codexextension`
- registry key: `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.openai.codexextension`

3. Decide whether the task is diagnosis-only or read-only retest.
- If diagnosis-only, avoid changing config or registration.
- If read-only retest is requested, keep outputs to counts, booleans, and exact error strings only.

4. Check workspace trust context.
- note whether the current thread is projectless
- prefer a trusted workspace thread for post-fix retests when available

## Procedure

1. Start with the narrow bundled checks, not generic setup guesses.
- Run the plugin’s own Chrome checks first:
  - `chrome-is-running.js`
  - `installed-browsers.js`
  - `check-extension-installed.js --json`
  - `check-native-host-manifest.js --json`
- Record whether Chrome exists, whether the extension is enabled, and whether the native host is actually correct.

2. Do one live Chrome bridge check.
- Use the browser runtime and call `browser.user.openTabs()`.
- If the user asked for read-only proof, keep only the count and do not print titles or URLs.
- Finish with `browser.tabs.finalize({})`.

3. Interpret the Chrome failure shape.
- If the error is `privileged native pipe bridge is not available; browser-client is not trusted`, treat it as a native-host/trust problem, not a missing Chrome binary problem.
- If `check-extension-installed.js` is good but `check-native-host-manifest.js` is bad, the native host is the real blocker.

4. Check Computer Use bootstrap context before deep runtime debugging.
- Inspect the cached bundled client path and note the current trust/session shape.
- If the task only asks "why unavailable", prefer diagnosis over writing config changes from memory.

5. Use the canonical Computer Use bootstrap.
- If the task is a read-only re-enable verification, reset the JS session first so the bootstrap proof is clean.
- Import the client from the exact absolute path:
  - `file:///%USERPROFILE%/.codex/plugins/cache/openai-bundled/computer-use/26.608.12217/scripts/computer-use-client.mjs`
- Run `setupComputerUseRuntime({ globals: globalThis })`.

6. If bootstrap fails, keep diagnostics narrow.
- Capture the exact error string.
- Check only these booleans:
  - `nodeRepl.config`
  - `nodeRepl.nativePipe`
  - `nodeRepl.nativePipe.createConnection`
  - `nodeRepl.env.SKY_CUA_NATIVE_PIPE_DIRECTORY`

7. If the user asked for a trusted-workspace retest, rerun once there and keep the output contract tight.
- Do not trust an older projectless thread alone if the task is explicitly about a new retest.
- Re-run the standard bootstrap in the trusted workspace.
- If setup succeeds and the user allowed it, call `sky.list_apps()` exactly once and return only the count.
- If the user gave a success/failure output contract, keep that exact branch shape: on success return only the minimal proof; on failure return only the exact error plus the requested native-pipe booleans.

8. If the task included durable handoff/status, update the local status artifact.
- Capture the root cause, the fix, the trusted-workspace proof, and the minimal final success output.

## Efficiency plan

- Prefer the bundled check scripts over wide recursive scans.
- Separate Chrome Plugin problems from Computer Use problems early; they can fail independently.
- Stop Chrome diagnosis once static checks plus one live bridge check agree.
- Stop Computer Use diagnosis once bootstrap succeeds or the requested booleans plus error string isolate the blocker.
- Re-test in a fresh trusted workspace only when the user explicitly asked for that surface; do not loop in a stale projectless thread.

## Pitfalls and fixes

- Symptom: Chrome is present and the extension is enabled, but browser access still fails.
- Likely cause: native host registration/trust is missing.
- Fix: verify `check-native-host-manifest.js --json`, then do one live bridge check.

- Symptom: native-host installation fails with `EPERM`.
- Likely cause: the current path or registration surface is not writable/trusted.
- Fix: record that as the current blocker and verify the active host path before attempting any write-based repair.

- Symptom: Computer Use still fails after Chrome is fixed.
- Likely cause: the retest is happening in a stale/projectless thread, or the runtime surface still does not match the bundled client.
- Fix: inspect trust metadata plus the actual bootstrap error before proposing repair steps.

- Symptom: bootstrap fails with `Computer Use native pipe path is unavailable`.
- Likely cause: the session does not expose the native pipe.
- Fix: return the requested booleans and stop; do not waste time on app-level actions.

- Symptom: search commands keep timing out.
- Likely cause: the search scope is too broad.
- Fix: inspect the exact config file, bundled scripts, registry key, and canonical client path instead of scanning the whole profile.

## Verification checklist

- `check-extension-installed.js --json` confirms the Codex extension is enabled on the intended Chrome profile.
- `check-native-host-manifest.js --json` plus one live bridge check reduce Chrome failures to a concrete native-host/trust diagnosis.
- A live Chrome bridge check either works or fails with a precise trust/native-host error.
- `setupComputerUseRuntime({ globals: globalThis })` succeeds from the canonical absolute client path, or the failure is reduced to the exact error plus the four requested booleans.
- If `sky.list_apps()` was allowed, it is called once and only the count is returned; do not treat the count itself as durable state.
