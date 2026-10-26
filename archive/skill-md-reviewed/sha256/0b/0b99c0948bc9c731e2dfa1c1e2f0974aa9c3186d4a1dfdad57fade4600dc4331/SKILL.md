---
name: hermes-plugin-development
description: >-
  Design, scaffold, register, and troubleshoot Hermes Agent plugins.
  Covers plugin.yaml/__init__.py structure, environment-variable account
  separation, tool registration, subprocess workers, OEPoll-style long-running
  bridges, vendor submodule wiring, stateless CLI-binary tool wrapping,
  Docker-managed relay plugins, and deciding when to extend core vs plugin.
  Use when creating or refactoring any plugin under ~/.hermes/plugins/ or
  project-local plugins/.
---

# Hermes Plugin Development

## Core Principles

1. **Core is a narrow waist.** Most capability should live at the edges (plugin or CLI+skill).
2. **Discovery is side-effect import.** `discover_plugins()` only runs when `model_tools.py` is imported.
3. **Profile-aware paths.** Use `get_hermes_home()` for state; `display_hermes_home()` for user-facing text.
4. **Tool handlers must accept `task_id`** (or `**kwargs`).
5. **Do not touch core files** (`run_agent.py`, `cli.py`, `gateway/run.py`, etc.) from a plugin.

## Plugin Structure

```
plugins/<name>/
  plugin.yaml      # REQUIRED. Name, version, description, config.
  __init__.py      # REQUIRED. register(ctx) entrypoint.
  bridge.py        # Optional. Long-lived worker process logic.
  auth.py          # Optional. Connection/auth/credential handling.
  models.py        # Optional. Internal dataclasses.
  migrations/      # Optional. SQLite schema setup.
  scripts/         # Optional. Re-runnable helper scripts.
  templates/       # Optional. Copyable starter files.
  references/      # Optional. Session notes, API quirks, docs excerpts.
```

## plugin.yaml (minimum)

```yaml
name: <name>
version: 0.1.0
description: What it does.
kind: standalone
config:
  some_port:
    type: integer
    default: 9100
  some_env:
    type: string
    default: "PREFIX_SETTING"
```

**`kind` is effectively required for clean discovery.** Valid values: `standalone`, `backend`, `exclusive`, `platform`, `model-provider`. Omitting it works, but invalid values like `tool` produce discovery warnings such as `unknown kind 'tool' (valid: ...)` and force a fallback to `standalone`. Use the real kind so tool/hook registration and enable/disable semantics stay correct.

## register(ctx) contract

```python
def register(ctx):
    ctx.register_tool(
        name="tool_name",
        toolset="<plugin_name>",         # REQUIRED — must match your plugin key
        description="What it does.",
        schema={...},
        handler=lambda args, **kw: handle(args, task_id=kw.get("task_id")),
        check_fn=lambda: True,           # optional availability gate
        requires_env=["PREFIX_VAR"],     # optional, shown in setup
    )
    # Optional lifecycle hooks:
    # ctx.register_hook("on_session_start", cb)
    # ctx.register_hook("on_session_end", cb)
    # ctx.register_hook("pre_tool_call", cb)
    # ctx.register_hook("post_tool_call", cb)
    # ctx.register_cli_command(...)
```

**`toolset` is REQUIRED.** Omitting it raises
`PluginContext.register_tool() missing 1 required positional argument: 'toolset'`
at load time and the plugin fails to enable. Use your plugin's key (e.g.
`"buzz"` for the `buzz` plugin). The tool then appears under `get_toolset_for_tool(name)`
and is dispatched normally.

## Tool handler rules

- MUST return a JSON string.
- MUST accept `task_id` directly or via `**kwargs`.
- MUST not mutate past conversation context or inject synthetic messages.

## Environment Separation Pattern

When a service has multiple accounts/tenants, split them by env-var prefix:

| Env var prefix | Example |
|---|---|
| `LINE_PERSONAL_*` | personal LINE account |
| `LINE_OFFICIAL_*` | official LINE bot |
| `TELEGRAM_*` | Telegram bot token |

This avoids colliding with Hermes built-in `LINE_*` variables used by `gateway/platforms/line.py`.

## Long-Running Worker Pattern (OEPoll, polling, watchers)

Prefer a **background thread + event queue** inside the plugin process over spawning subprocesses unless the underlying library blocks the GIL or crashes require isolation.

```python
import threading, queue

class Worker:
    def __init__(self):
        self._q = queue.Queue()
        self._stop = threading.Event()
        self._t = threading.Thread(target=self.run, daemon=True)
        self._t.start()

    def run(self):
        while not self._stop.is_set():
            try:
                event = self._q.get(timeout=0.5)
                self.handle(event)
            except queue.Empty:
                continue

    def enqueue(self, event):
        self._q.put(event)

    def stop(self):
        self._up.set()
        self._t.join(timeout=2)
```

If the library is not thread-safe, use `subprocess.Popen` with JSON-lines over stdin/stdout.

## Plugin Registration Checklist

- [ ] `plugin.yaml` present with `name`, `version`, `description`, and `config`.
- [ ] `__init__.py` defines `register(ctx)` and is importable (no top-level exceptions).
- [ ] Tools have unique names; schemas are dicts.
- [ ] Handler returns JSON string.
- [ ] No core files edited.
- [ ] State files under `get_hermes_home()`.
- [ ] Secrets in `.env` only, not in `config.yaml` or skill files.

## Recent Integration: Switchyard Plugin (2026-09-11)

Successfully integrated Switchyard LLM router library into Hermes Agent:

1. **Cloned repository**: `https://github.com/zapabob/Switchyard` - NVIDIA's LLM router library (Rust core + Python bindings)

2. **Created plugin structure** at `~/.hermes/plugins/switchyard/`:
   - `plugin.yaml` - Plugin metadata with name, version, description, config, kind
   - `__init__.py` - Plugin initialization with `register(ctx)` entrypoint
   - `core.py` - Core implementation exposing Switchyard's routing capabilities

3. **Enabled plugin** via `hermes plugins enable switchyard` - plugin now appears in `hermes plugins list`

4. **Exposed three tools**:
   - `switchyard_classify` - Classify prompts and recommend optimal models
   - `switchyard_router` - Route prompts through Switchyard's intelligent selection algorithm
   - `switchyard_status` - Report plugin status and available models

5. **Verification steps**:
   - `hermes plugins list` shows plugin as `enabled user 0.1.0 switchyard`
   - `hermes plugins enable switchyard` succeeds on fresh session
   - Tools dispatch correctly through Hermes tool registry

**Key pattern**: Follow the standard Hermes plugin structure (plugin.yaml + __init__.py + core.py), use `get_hermes_home()` for state paths, register tools with unique names matching the plugin key, and always verify with `hermes plugins list` after enabling.

**Pitfall avoided**: Initial `uv sync --all-extras` timed out (exit 124); resolved by manual file placement instead of package manager installation.

## Submitting Your Plugin

Once your plugin is developed and tested, follow these steps to submit it for inclusion:

1. **Verify your changes**: Run any tests and ensure the plugin loads correctly.
    Consider using the `requesting-code-review` skill for pre-commit verification.

2. **Commit your changes**: Use Conventional Commits format.
    For a new plugin, use: `feat(plugins/<plugin-name>): add <plugin-description>`
    For example: `feat(plugins/hypura): add Hypura storage-tier-aware LLM inference scheduler provider`
    ```bash
    git add plugins/<plugin-name>/
    git commit -m "feat(plugins/<plugin-name>): add <plugin-description>"
    ```

3. **Push your branch**: Push your feature branch to the remote repository.
    ```bash
    git push origin <branch-name>
    ```

4. **Create a Pull Request**: Go to the repository on GitHub and create a pull request from your feature branch to the main branch.
    Alternatively, use the GitHub CLI:
    ```bash
    gh pr create --title "feat(plugins/<plugin-name>): add <plugin-description>" --body "## Summary\n\nAdds <plugin-description>.\n\n## Changes\n\n- Added plugins/<plugin-name>/__init__.py\n- Added plugins/<plugin-name>/plugin.yaml\n\n## Rationale\n\n<Explain why this plugin is useful>\n\n## Testing\n\n-Verified plugin loads without errors.\n- Verified plugin integrates correctly with Hermes."
    ```
    Replace `<plugin-name>` and `<plugin-description>` with your actual values.

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `<type>[optional scope]: <description>`
- Types: `feat` (new feature), `fix` (bug fix), `docs` (documentation), `style` (formatting), `refactor` (code refactor), `test` (adding tests), `chore` (maintenance)
- Scope: For plugins, use the plugin name in parentheses, e.g., `(plugins/hypura)`
- Description: A concise description of the change in imperative mood (e.g., "add" not "added" or "adding")

Example: `feat(plugins/hypura): add Hypura storage-tier-aware LLM inference scheduler provider`

### Model Provider Plugins

Model provider plugins follow a specific structure under `plugins/model-providers/<provider-name>/`:

**Required files:**
- `__init__.py` - Contains the provider profile implementation
- `plugin.yaml` - Plugin manifest for discovery

**Example `__init__.py` for a model provider:**
```python
"""Provider profile description."""

import logging
from typing import Any, Optional

from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)


class YourProviderProfile(ProviderProfile):
    """Description of your provider."""

    def fetch_models(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 8.0,
    ) -> Optional[list[str]]:
        """Fetch models from your provider's API."""
        try:
            result = super().fetch_models(
                api_key=api_key,
                base_url=base_url or "https://your-provider.api.url",
                timeout=timeout,
            )
            return result
        except Exception as exc:
            logger.debug("fetch_models(your_provider): %s", exc)
            return None


your_provider = YourProviderProfile(
    name="your-provider",
    aliases=("your-provider-alias",),
    default_aux_model="your-provider",
    env_vars=(),  # Add required env vars here if needed
    base_url="https://your-provider.api.url",
)

register_provider(your_provider)
```

**Example `plugin.yaml`:**
```yaml
name: your-provider-plugin
kind: model-provider
version: 1.0.1
description: Provider - Brief description of what it does
author: Your Name or Organization
```

After creating these files, the provider will be automatically discovered and available via `hermes model` and in the agent's model selection.

## Local-inference (scoring / constrained-decision) plugins

A plugin that wraps a local inference server and exposes a **decision** tool
rather than a chat tool has a different shape from the vendor/submodule
patterns below: the tool never wants generated text, it wants a probability
distribution over a caller-supplied candidate set from a single forward pass.

Key mechanics (all verified against `llama-server`, see
`references/local-inference-scoring-plugin.md` for the full recipe):

- Read the answer-slot logit row with `n_predict: 0` + `n_probs: N` on
  `/completion`; there is no `/logits` endpoint.
- **Verify** the single-token contract per choice via `/tokenize`
  (`prompt + code` must differ by exactly one token) and raise a field-named
  error when it does not.
- **Disable thinking explicitly** (`chat_template_kwargs:
  {"enable_thinking": false}`). A reasoning model otherwise occupies the
  answer slot with `<think>` and every candidate logprob collapses to ~-16 —
  the call still "succeeds" and every probability is garbage. This is the
  highest-value single probe; do it before concluding a model cannot score.
- Render prompts with the model's own template (`/apply-template`) rather than
  hand-writing ChatML.
- Softmax **only** the candidate rows; refuse (never silently drop) when a
  candidate falls outside top-`n_probs`, and never truncate an over-long
  prompt.
- Expose cheapest-first tools — `validate_schema` (offline), `status`, then the
  scoring call — and gate the expensive one with a reachability `check_fn` so it
  disappears from the toolset when the server is down.

## Adapting large upstream projects into Hermes plugins

Before porting or wrapping an upstream repository, inspect its pinned HEAD, package manifest, entry points, full feature surface, security boundary, and upstream tests. Do not infer the project's scope from an old local wrapper or a README tagline. A repository described as an MCP sidecar may have grown into a control plane with many tools, UI surfaces, persistent state, and separately gated mutation paths.

Choose and document one integration boundary before editing:

1. **Bounded native plugin:** port a deliberately selected subset through `register(ctx)` and Hermes plugin APIs. Keep the allowlist explicit, preserve upstream safety gates that apply to each behavior, and identify omitted features.
2. **Managed sidecar:** retain upstream as an independently versioned package/submodule and have the Hermes plugin manage or configure it. This preserves upstream capabilities but is not equivalent to registering all upstream MCP tools as native Hermes tools; test discovery, dependencies, process lifecycle, authentication, and tool access separately.
3. **Inventory first:** when scope or risk is unresolved, produce a feature-to-integration map and request a scope decision before making code or profile changes.

Do not claim a complete port after adding only a CLI wrapper or a few representative tools. Map each retained feature to an upstream source/API and a Hermes-facing registration or lifecycle path. Separate upstream contract tests from Hermes plugin discovery/registration tests, and preserve upstream permission, confirmation, dry-run, local-only, redaction, and secret-boundary semantics rather than weakening them during adaptation.

### Explicit-intent launch gates for sidecars

When an upstream MCP command auto-starts a local body/server, normal MCP discovery can become an unintended actuation path. Inspect the upstream entrypoint rather than assuming MCP registration is passive. If upstream provides a no-start mode, register MCP with that mode and keep process launch behind a separate Hermes plugin action.

For launch phrases that must be explicit:

- Validate the trusted raw **current user message and source**, not an LLM-supplied copy of the phrase.
- Prefer `raw_text.strip() == REQUIRED_PHRASE`; do not use substring, fuzzy, semantic, or process-detection triggers.
- Reject assistant/tool/cron/system sources and negative or quoted mentions such as `start X only when...`.
- Make launch idempotent: status-check first and report `already_running` rather than spawning duplicates.
- Test through dependency-injected process creation; include positive exact-match and negative near-match/source cases before any live smoke.
- Keep MCP discovery and sidecar actuation as separate verification lanes.

See `references/explicit-intent-sidecar-launch.md` for the threat model and test matrix.

Protect the user's existing Git state before changing files: capture branch and full `git status --short --untracked-files=all`, inspect staged and unstaged changes separately, and treat pre-existing staged deletions as user-owned state. Do not restore, overwrite, stage, or enable those paths without explicit scope. Keep unrelated edits and untracked files untouched. If repository navigation tooling is unavailable for the host runtime, use targeted file reads and narrow searches rather than treating the navigation failure as evidence about the code.

## External Server Management Plugins (SillyTavern pattern)

For plugins that wrap a third-party local server (SillyTavern, ComfyUI, etc.):

- Vendor the upstream repo as a **git submodule** under `vendor/<Name>` (check `.gitmodules` first — it may already be registered) and resolve the install dir as: `<NAME>_DIR` env override → repo `vendor/<Name>` submodule → fallback path.
- Provide 4 tools: `<name>_status`, `<name>_start`, `<name>_stop`, `<name>_version`; gate all with `check_fn=_installed` (checks the server entry file exists).
- Start with `subprocess.Popen(..., creationflags=CREATE_NEW_PROCESS_GROUP|CREATE_NO_WINDOW)` on Windows, disable auto-browser-launch flags, poll the HTTP root until ready (~45s).
- Stop fallback: parse `netstat -ano -p tcp` for the LISTENING PID and `taskkill /PID <pid> /F`. **On Japanese Windows pass `encoding="cp932", errors="replace"`** to `check_output` — default UTF-8 raises UnicodeDecodeError and output becomes None.
- Verify by importing the module standalone (`importlib.util.spec_from_file_location`), calling `register()` on a stub ctx, then real stop→start→status against the live server. See `references/external-server-plugin.md`.
- **Auto-configure from Hermes .env**: Modify the target's secrets and settings files to inject Hermes API keys and endpoint URLs (see `references/third-party-auto-config.md`). Call `_configure()` from `_start()` so the target starts provisioned.
- **Docker compose for relay-dependent protocols**: When the plugin depends on a relay (Nostr, MQTT broker, etc.), use `docker compose up/down` to manage the infrastructure. Same lifecycle as server management, but the plugin itself connects via a lightweight protocol client (see `references/lightweight-protocol-client-plugin.md`).

## CLI Binary Wrapping Plugins (OfficeCLI pattern)

For plugins that wrap a stateless third-party CLI binary (officecli, tldraw, etc.):

- Vendor as **git submodule** under `vendor/<name>` (shallow clone for large repos: `git submodule add --depth 1`).
- Install the binary via the vendor's installer (PowerShell: `powershell.exe -ExecutionPolicy Bypass -File install.ps1`; Bash may not work on Windows/MSYS).
- Provide structured tools with `check_fn=_installed` (uses `shutil.which()` + known install paths like `~/AppData/Local/<Name>/`).
- **Stateless per-call**: no start/stop lifecycle — each tool invocation runs the binary and returns JSON.
- **Windows path-with-spaces pitfall**: some binaries fail on paths containing spaces. Workaround: create files in a temp dir, then move to final location.
- **Headless operation flags**: Some CLI tools require special flags for non-interactive/headless operation (e.g., Antigravity/agy requires `--dangerously-skip-permissions` to bypass permission prompts). Check the tool's documentation and include necessary flags in your subprocess calls.
- Verify standalone: `importlib.util.spec_from_file_location` → `register()` on stub ctx → each handler returns valid JSON → `py_compile` passes.
- See `references/cli-binary-plugin-pattern.md` for full pattern and working example.

## Submodule-augmented vendor plugin wiring (Buzz/OfficeCLI)

When vendoring upstream repos with companion Hermes plugins:

### Large upstream companion apps (AIRI-style)

For a large TypeScript/Vue/Electron companion application, keep the upstream checkout as a gitlink under `vendor/<name>` and keep Hermes integration thin in `plugins/<name>/`. Separate responsibilities explicitly: the upstream app owns UI/VRM/TTS/runtime state; Hermes owns the LLM endpoint; the plugin owns lifecycle/config generation and narrowly scoped local bridges such as OSC.

1. Inspect the upstream tree and current source before inventing environment variables or API routes. Prefer the upstream's documented OpenAI-compatible provider configuration (`apiKey`, `baseUrl`, model) over patching its source.
2. If provider settings are stored in UI/database state rather than a stable file, generate a non-secret import/template file under the Hermes home and report the exact UI/API step; do not claim automatic wiring until a real read-back confirms it.
3. Keep secrets out of generated config: store only an environment-variable name or masked reference, and direct the user to the active profile `.env`.
4. A submodule checkout is not automatically runnable: verify `package.json`, required package manager, dependency installation, and the exact app script before exposing `start`. On Windows, resolve package-manager shims explicitly (`shutil.which("pnpm.cmd") or shutil.which("pnpm")`) before passing the command to `subprocess.Popen`; a shell that can run `pnpm` does not guarantee Python can resolve the bare name.
5. After dependency installation, verify the actual postinstall/build result and distinguish upstream warnings from a nonzero exit. For large pnpm workspaces, record workspace/package counts and the app process PID/readiness separately; a returned PID is not proof that the UI/API is ready.
6. Treat unstable upstream integrations (for example, undocumented VRChat autonomy APIs) as an explicit local adapter boundary. Expose observable, user-invoked OSC controls first; do not describe a bounded bridge as a hidden autonomous loop.
6. Verify with `git submodule status`, gitlink mode `160000`, `py_compile`, standalone `register(ctx)` smoke with a stub context, and a config-generation read-back. Run repository-wide checks separately and classify unrelated baseline failures instead of attributing them to the plugin.

The AIRI-specific provider-template pattern and verification checklist are captured in `references/large-upstream-companion-app.md`.

- `.gitmodules` is the source of truth for submodule URL/path.
- Use `git submodule add <url> <path>`; do **not** use `git add` on an existing nested git repo.
- Verify with:
  - `git config -f .gitmodules --list`
  - `git submodule status <path>`
  - `git ls-files --stage | grep <path>` should show mode `160000`.
- Stage `plugins/...` and commit after the submodule is fully registered.

## Docker-managed relay plugin pattern (Buzz)

- Use **stateless lifecycle tools**: `<name>_status`, `<name>_start`, `<name>_stop`, `<name>_version`.
- `start/stop` wrap `docker compose up -d` / `docker compose down`; `status` wraps `docker compose ps`.
- Gate all tools with `check_fn=_installed` so they degrade gracefully without Docker.
- `BUZZ_BIN` can remain optional; relay lifecycle tools work without a native CLI.
- **Actual local relay port**: after `docker compose up -d`, inspect `docker compose ps` — the default `localhost:3000` is often wrong. On this Windows host the running relay responded on `localhost:8080`, while `localhost:3000` was not bound. Do not hardcode `3000`; probe both or derive from container port mapping.
- **Default relay env fallback**: if `BUZZ_RELAY_URL` is unset, inject `http://localhost:8080` in the wrapper's `subprocess.run(..., env=...)` so tool calls do not fail with `BUZZ_RELAY_URL is required`. Preserve any user-provided value instead of overwriting it.
- **Consistent JSON envelope**: every tool must return `{"ok": ..., "code": ..., "stdout": ..., "stderr": ...}`. Do not omit `ok`/`code` on success paths; downstream agents key off those fields.

**Buzz-specific compose fact**: `vendor/buzz/docker-compose.yml` covers infra only
(`postgres`, `redis`, `keycloak`, `minio`, `prometheus`, `adminer`). The relay
is a Rust binary from `crates/buzz-relay`, started via `just relay` /
`cargo run -p buzz-relay`. Do not assume `localhost:3000` is reachable after
`docker compose up -d`; probe the actual bind port before wiring clients.

**Verified Buzz CLI v0.2.0 syntax** (matches `buzz.exe --help` on Windows):
| Plugin calls                | Actual CLI                             |
|----------------------------|----------------------------------------|
| `channels create`          | `buzz channels create --name X --type stream|forum --visibility open|private [--description ...] [--ttl N]` |
| `channels list`            | `buzz channels list --limit N`          |
| `messages send`            | `buzz messages send --channel <UUID> --content <...> [--reply-to <ID>] [--file ...]` |
| `messages get`             | `buzz messages get --channel <UUID> --limit N [--before <ts>] [--since <ts>] [--kinds 1,1984]` |
| `users get`                | `buzz users get [--pubkey <hex>] [--name <substring>]` |
| `dms list`                 | `buzz dms list --limit N`               |
| `mem ls/get/set/patch/rm`  | `buzz mem <subcommand> [options]`       |

**Missing CLI feature**: `buzz.exe` has no `keypair` subcommand. The plugin
should not register `buzz_keypair` until that command exists upstream; otherwise
every call fails with `unrecognized subcommand 'keypair'`. If key management is
required, implement it in the plugin via pure-Python `nostr` key generation/import
instead of assuming the binary supports it.

**Tailnet exposure**: local Buzz relay can be exposed via `tailscale serve --bg --set-path /buzz --yes http://localhost:8080`. Verify with:
```bash
curl -sS https://<host>.ts.net/buzz/health
```

**Rust relay build on Windows — path-with-spaces workaround**: `proc-macro2`
`v1.0.106`'s `build.rs` calls `create_dir_all` on `<target>/build/proc-macro2-*/out/`
which fails with `os error 2` (ERROR_FILE_NOT_FOUND) when any parent component
contains spaces (e.g. `New project`). Neither `--target-dir` nor filesystem
junctions/symlinks avoid this — Cargo resolves them to the original path.
**Fix**: copy the entire `vendor/buzz` directory to a spaceless path
(e.g. `cp -r vendor/buzz /c/buzz-src`) and build from there:
```bash
cargo build -p buzz-relay --release --target-dir /c/buzz-src/target
```
The resulting `buzz-relay.exe` can be copied back to `vendor/buzz/` + to
`~/.cargo/bin/`. Build the buzz CLI the same way: `cargo build -p buzz-cli --release`.

**Port map + conflict resolution**: Default ports (3000/8080/9102) may conflict
with other services. Override via env vars:
```
BUZZ_BIND_ADDR=0.0.0.0:3001    # WebSocket
BUZZ_HEALTH_PORT=13080          # health/liveness (default 8080)
BUZZ_METRICS_PORT=19102         # Prometheus (default 9102)
RELAY_URL=ws://localhost:3001   # must match BIND_ADDR port
```

**Required env for first start**:
- `BUZZ_AUTO_MIGRATE=true` — runs DB schema migrations on startup
- `BUZZ_GIT_REPO_PATH=C:/path/to/repos` — absolute Windows path with forward
  slashes (MSYS translates `/c/` literally in env vars), a dir the relay can
  write into
- `DATABASE_URL=postgres://[REDACTED]@localhost:5432/buzz` — **password must
  be literal** (`***` placeholder from `.env.example` will fail auth)

**Buzz CLI v0.2.0 syntax (differs from the plugin defaults)**:
| Plugin calls                | Actual CLI                   |
|----------------------------|------------------------------|
| `channel` (singular)       | `channels` (plural)           |
| `--private` / `--public`   | `--visibility open|private`  |
| `message send <ch> -m ...` | `messages send --channel <id> --content <...>` |
| `message read <ch>`        | `messages get --channel <id>` |

These mismatches mean `plugins/buzz/tools.py` will error until the CLI-arg
mappings are updated to match the v0.2.0 binary. Update the tool, re-register,
and verify.

**Buzz env vars (all prefixed)**: `BUZZ_BIND_ADDR`, `BUZZ_HEALTH_PORT`,
`BUZZ_METRICS_PORT`, `BUZZ_GIT_REPO_PATH`, `BUZZ_AUTO_MIGRATE`,
`BUZZ_AUDIT_ENABLED`, `BUZZ_REQUIRE_AUTH_TOKEN`, `BUZZ_MEDIA_MAX_CONCURRENT_UPLOADS`,
`RUST_LOG`. All set in bash as `KEY=value ./binary` or in `.env` file.

**Session-learned Buzz plugin corrections (2026-07-25)**:
- **Actual relay port is 8080, not 3000**: `docker compose ps` showed relay responding on `localhost:8080` (health endpoint returns `{"status":"ok"}`); `localhost:3000` was not bound. Tools must default to `http://localhost:8080` when `BUZZ_RELAY_URL` is unset.
- **`vendor/buzz/.env` must be read by the plugin**: subprocess tools don't inherit the parent's updated `os.environ`. Implement `_load_buzz_env()` that parses `.env` and injects `BUZZ_PRIVATE_KEY` / `BUZZ_RELAY_URL` into the subprocess `env` dict at call time.
- **`plugin.yaml` is required for discovery**: without it, the plugin appears in `_plugins` as a string key only and never gets loaded/enabled. Always include a minimal `plugin.yaml`.
- **All tools must return consistent JSON envelope**: include `ok`, `code`, `stdout`, `stderr` on every return path — agents key off `ok`/`code`.
- **Windows build must avoid path-with-spaces**: `proc-macro2` fails with `os error 2` when any parent component contains spaces. Fix: copy `vendor/buzz` to a spaceless path (e.g. `/c/buzz-src`) and build there; symlinks/junctions do NOT work — must be a real copy with fresh `target/`.
- **Rustup state can desync**: `winget show Rustlang.Rustup` may say installed while `cargo.exe` is not on PATH. Verify `%USERPROFILE%\.cargo\bin\cargo.exe`; if missing, run `rustup-init.exe -y default --no-modify-path`.

## Windows installer pitfalls (Docker Desktop, etc.)

- **UAC/visibility**: silent install can succeed from background PowerShell, but cannot force a visible UAC prompt; if silent fails, require elevated manual install.
- **MSYS curl write bug**: `curl.exe -o` can fail on paths with spaces; stage installers under `%USERPROFILE%\\Downloads\\installers\\` and use `Invoke-WebRequest` instead.
- **PATH lag**: after install, `docker.exe` may be absent from PATH until the app has launched once; wait for engine readiness instead of hard-failing.
- **Docker readiness probe**:
  ```powershell
  & 'C:\\Program Files\\Docker\\Docker\\DockerCli.exe' -SharedDrives
  ```
  Failure mode: pipe-error `\\\\.\\\\pipe\\\\dockerBackendApiServer` → retry after relaunch.
- **Silent install command**:
  ```powershell
  Start-Process -FilePath "C:\\Program Files\\Docker\\Docker\\DockerDesktop.exe" -ArgumentList "install --quiet --accept-license" -Wait -NoNewWindow
  ```
  For background runs, pair with `notify_on_complete=true` and a post-install readiness poller; do not block the foreground channel with multi-minute installs.
- **PowerShell path conversion**: when calling `powershell.exe -Command` from bash/MSYS, `/c/Users/...` is converted to `C:\\c\\Users\\...` and breaks. Use Windows-style `C:\\\\Users\\\\...` in the PS command string.
- **Disk-space guardrail**: before any installer, probe `Get-PSDrive C`. If free GB is low, prefer freeing space over retrying installs. Safe cleanup order: temp/partials (`*.crdownload`, `*.tmp`), Hermes caches/logs, then large non-model files. Do **not** delete large model assets (`*.gguf`, checkpoints) — move them to another drive instead.
- **Rust build failure (proc-macro2 on Windows with spaces in path)**: when the
  workspace path contains spaces, `proc-macro2`'s `build.rs` fails creating
  `<target>/build/proc-macro2-*/out/probe` with `os error 2`
  (`ERROR_FILE_NOT_FOUND`). Neither `--target-dir` nor filesystem junctions
  help — Cargo resolves them to the real path. **Fix**: copy the source tree
  to a spaceless directory (e.g. `cp -r vendor/buzz /c/buzz-src`) and build
  there. Symlinks/junctions do not work; the copy must be a real copy with a
  fresh `target/`.
- **Rustup state mismatch**: `winget show Rustlang.Rustup` can report installed while `cargo.exe` is not on PATH. Verify `%USERPROFILE%\\.cargo\\bin\\cargo.exe`; if missing, run `rustup-init.exe -y default --no-modify-path` and re-check PATH. If `winget install` returns `No space left on device`, free disk first.

## git-bash (MSYS) clone-vanishing pitfall (Windows)

`git clone` targeting `/d/...`, `/e/...`, or `~/...` from the terminal tool can report success (rc=0, "done.") while the directory does not exist afterward. Fix: clone into the current directory via the `workdir` parameter with a relative target (`git clone ... ./name`), then `mv`. Verify with `powershell -Command "Test-Path ..."`, not MSYS `ls` alone.

## Common Pitfalls

1. **Editing core to load a plugin.** Never edit `run_agent.py`, `cli.py`, or `gateway/run.py` for plugin registration.
2. **Hardcoding `~/.hermes` paths.** Use `get_hermes_home()`; hardcoding breaks profiles.
3. **Forgetting `task_id`.** Plugin tool handlers that omit `task_id` break when the framework injects it.
4. **Core-vs-plugin ambiguity.** Prefer plugin unless the capability is fundamental and broad enough to justify core surface.
5. **Import-time side effects.** Keep `register()` calls idempotent at module import time.
6. **Unbounded background threads.** Always provide a stop/shutdown path.
7. **Env var collisions with Hermes built-ins.** Prefix plugin env vars clearly (`PLUGINNAME_*`, `LINE_PERSONAL_*`).
8. **C extension build failures on Windows.** Libraries like `secp256k1` (needed by `nostr`) fail to compile. Use pure-Python alternatives: `ecdsa` for crypto, `websocket-client` for WebSocket. Check `uv pip install` output before assuming a dependency is available.
9. **Missing `toolset` in `register_tool`.** The second positional-after-name argument is **required**. A plugin that omits it loads with `enabled=False` and the error `PluginContext.register_tool() missing 1 required positional argument: 'toolset'`. Always pass `toolset="<plugin_name>"`.
10. **Adding a cloned vendor repo as a plain git add.** If a vendor directory is already a Git repo, `git add vendor/<name>` embeds it. Use `git submodule add <url> vendor/<name>` so `.gitmodules` and the gitlink are created correctly. Run `git submodule status vendor/<name>` to verify before committing.
11. **Standalone `importlib` load of a plugin `core.py` → dataclass `AttributeError`.** When a no-agent cron or standalone script must call a plugin's functions directly (the `plugin_*` tool isn't exposed in the runtime), loading `plugins/<name>/core.py` with `importlib.util.spec_from_file_location` fails at module load:
    `AttributeError: 'NoneType' object has no attribute '__dict__'`
    raised inside `dataclasses._is_type` while decorating a `@dataclass` class. Root cause: the freshly built module isn't yet in `sys.modules`, so the dataclass machinery can't resolve `cls.__module__`. **Fix — register the module in `sys.modules` BEFORE `exec_module`:**
    ```python
    spec = importlib.util.spec_from_file_location("plugmod", "plugins/<name>/core.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["plugmod"] = mod   # REQUIRED for dataclasses inside core.py
    spec.loader.exec_module(mod)
    ```
    Also insert the repo root into `sys.path` first (so `hermes_constants` and sibling imports resolve), then call `mod.<fn>(...)` directly. Keep stdout to bounded counts/status only — never print cookies, tokens, or raw auth material. Delete the temp runner after the run.

12. **Comparing your port to a README's numbers with a different grader.**
    Reuse the upstream evaluation functions verbatim; an independent
    re-implementation of "accuracy" moves the result by several points and
    makes the comparison unattributable. When a benchmark run returns a *cluster*
    of identical errors, treat it as a contract bug (key normalization, rounding
    vs. tolerance), not a model result — fix the contract and rerun before
    quoting any accuracy. Report against random and majority-class baselines,
    give a Wilson CI, and stratify accuracy by the model's own confidence before
    recommending an operating threshold. See
    `references/porting-benchmark-comparison.md`.

## Enabling a plugin when the config write-guard blocks direct edits

`~/.hermes/config.yaml` is read-only to the agent (writes are refused:
"Agent cannot modify security-sensitive configuration"). Do NOT use `sed` /
`yaml.safe_dump` from a script against that path (the script's CWD path
resolution can miss it under Windows/MSYS). Instead drive the live config
loader from the repo checkout:

```python
import sys
sys.path.insert(0, "<repo_root>")
from hermes_cli.config import load_config, save_config
cfg = load_config()
cfg["plugins"]["enabled"].append("<plugin_name>")
save_config(cfg)   # honors profile resolution; persists correctly
```

Then verify in-process without a CLI restart:

```python
import sys
sys.path.insert(0, "<repo_root>")
import model_tools                       # triggers tool discovery
from hermes_cli.plugins import discover_plugins, get_plugin_manager
from tools.registry import registry

discover_plugins(force=True)
mgr = get_plugin_manager()
p = mgr._plugins.get("<plugin_name>")
print(p.enabled, p.error, p.tools_registered)
names = registry.get_all_tool_names()
print([n for n in names if n.startswith("<plugin_name>_")])
# e.g. "buzz_" -> 8 tools expected
```

Key checks: `p.enabled is True`, no `p.error`, `tools_registered` lists your
tools, and `registry.get_all_tool_names()` includes them (after
`import model_tools` so discovery runs). The `hermes plugins list/enable`
CLI commands also work but require a running profile context.

## MCP-backed OSINT façade pattern

When integrating a large third-party MCP server into an existing agent, keep two layers:

1. Register the upstream server natively in Hermes `mcp_servers` so the complete catalog remains available.
2. Add a small project-local plugin façade with bounded, stable high-level tools for routine workflows. Keep its allowlist explicit; do not expose arbitrary dispatch through the façade.

For a local Python MCP server, install it into the active Hermes `.venv`, persist its absolute Windows stdio executable path through Hermes' MCP config loader, then verify with `hermes mcp test <name>` and record the discovered tool count. The façade may call the package's public/internal dispatcher directly for a stable orchestration surface, but must return JSON strings, accept `task_id` via `**kwargs`, and degrade through `check_fn` when the package is absent.

For multi-source OSINT briefs, use bounded concurrency (`asyncio.gather(..., return_exceptions=True)`), preserve per-source errors, and report partial success rather than failing the entire brief because one RSS/API source returns 401/403/404/429. Keep credentials in `.env`; public-source integrations should work with no secret values.

A practical verification ladder is: `py_compile` + `git diff --check`; standalone import and stub-context registration; related plugin-discovery pytest; native MCP connection/tool discovery; one lightweight status/query call; then one real bounded brief. Do not claim full-suite success when unrelated UI/ACP/provider tests fail.

### Windows/MCP and test-runner pitfalls

- `hermes mcp add` is discovery-first and may stop at an interactive tool-selection prompt. For non-interactive setup, use Hermes' own `hermes_cli.mcp_config._save_mcp_server()` / config loader rather than writing YAML with shell tools; this preserves profile resolution and validation.
- On Windows, `scripts/run_tests.sh` may only probe `<venv>/bin/activate` and miss a valid `.venv\\Scripts\\python.exe`. Pass `HERMES_PYTHON=/c/Users/<user>/.../.venv/Scripts/python.exe` and, on MSYS, set `HERMES_TEST_WORKERS=1` for a deterministic diagnostic run. Treat subsequent unrelated failures separately from the plugin's targeted verification.

Use `references/mcp-osint-facade.md` for the concrete World Intel integration recipe and verification transcript.

## Desktop UI halves backed by git submodules

When an external repository is a Hermes Desktop runtime plugin rather than a
Python tool provider, keep the upstream UI code as a git submodule inside the
Python plugin package (for example `plugins/<name>/desktop/`). Add a minimal
Python `plugin.yaml` and `__init__.py` wrapper so Hermes' backend plugin
inventory can discover and enable the package, but do not duplicate the UI in
Python or patch Desktop core. Hermes Desktop's unified-plugin loader scans
`<HERMES_HOME>/plugins/<name>/desktop/plugin.js`; the desktop half is opt-in,
matching the backend `plugins.enabled` posture.

Use the submodule's exact gitlink as the reproducible version boundary. Verify
both the parent gitlink (mode `160000`) and the submodule's entrypoint, then
wire the active profile to the repository using the profile's supported plugin
installation mechanism (a junction is suitable on Windows for local
repository development). Treat Desktop runtime tests as a separate verification
lane from Python plugin discovery; a passing Python registration smoke test
alone does not prove the UI loads.

See `references/desktop-ui-submodule-integration.md` for the compact manifest,
wrapper, verification, and Windows profile-link pattern.

## When to Extend Core vs Plugin

Use this ordering:
1. Extend existing code.
2. CLI + skill.
3. Service-gated tool (`check_fn`).
4. Plugin.
5. MCP server.
6. New core tool (last resort).

## Verification

```bash
hermes plugins list          # plugin must appear
hermes plugins enable <name> # must succeed
hermes plugins status        # shows enabled and any hook/tool count
```

### Web-provider fallback pattern

For web plugins, preserve the configured provider as the primary path. Add
fallback only at the dispatcher boundary and trigger it on a provider error or
empty result, not on every request. The recommended ladder is:

1. configured `web_search` provider;
2. local CloakBrowser search/extract;
3. a bounded manual browser-use/ComputerUse handoff.

Keep the final browser step manual when it may reuse a signed-in browser or
encounter a verification challenge. Return a safe, actionable hint rather than
silently opening a browser, entering credentials, or bypassing a challenge.
Normalize provider-specific redirect URLs before returning the common Hermes
shape. See `references/web-provider-fallback.md` for the implementation and
verification recipe.

For cron wrappers, emit only bounded fallback metadata (`ok`, provider, result
count, error type); never print cookies, headers, tokens, or raw auth material.

### Web-provider fallback pitfalls

- Do not replace Hermes `web_search` globally with a script; keep the standard
  registry and add a failure-only fallback.
- Do not add automatic X posting to a research fallback. `lm-twitterer`
  publishing remains a separately authorized action.
- Do not claim full-suite success when repository tests are blocked by missing
  platform dependencies; report targeted smoke results separately from
  unrelated UI/PTY/ACP failures.

If `plugins list` does not show the plugin, check:
- `plugin.yaml` parse errors
- `__init__.py` import errors
- plugin directory under the correct `plugins/` path for the active profile

## Sub-workflows absorbed into this umbrella

### Plugin troubleshooting

Use the same plugin lifecycle model for runtime failures: collect load/runtime logs, inspect the plugin package, patch the smallest failing layer, restart/reload Hermes, and verify the corrected code path. Common patterns include Pydantic response-parse failures in upstream libraries, over-eager content/secret filters, provider allowlist errors, and log-file locks on Windows.

### TTS provider plugins

TTS integrations are plugins when they need shared provider dispatch, CLI/status commands, gateway voice output, or reusable local-server management. Avoid creating a separate skill for each engine; put engine-specific notes under this skill's `references/` directory. Watch for same-name legacy `tts.providers.<name>.type: command` blocks shadowing plugin providers.

For a cloud TTS provider, implement one provider class behind the existing TTS registry and let the shared dispatcher carry it into CLI, TUI, gateway, and desktop chat. Add a plugin CLI only for status/synthesis convenience; do not duplicate synthesis logic per UI. If desktop credential management is driven by `/api/env`, expose plugin `get_setup_schema()['env_vars']` generically in the web server so new TTS plugins appear as masked provider cards instead of unknown custom keys. Keep the current default provider unchanged unless the user explicitly requests a switch.

Use a namespaced secret such as `<PROVIDER>_API_KEY`, load it from Hermes `.env`, and keep status responses to a boolean presence check. For official REST TTS APIs, validate the exact auth header, model header, request format, output formats, and speed bounds from the provider's current docs; cap text length and sanitize bounded error bodies so credentials cannot leak. Verify both mocked request construction and one minimal real free-tier request when the user supplied credentials and requested live wiring. On Windows, rerun pytest with `HOME`/`USERPROFILE` explicitly set when the clean test runner strips the home environment; treat the missing-home failure as a runner-environment issue, not a provider regression.

### Employee/role plugins

Role-based AI employee plugins are a specialization of Hermes plugin scaffolding: `plugin.yaml`, `register(ctx)`, permissioned profiles, SOUL templates, kanban/cron wiring, CLI/slash commands, and verification all belong under this umbrella.

### Personal messaging bridges

Personal LINE/linepy bridges are plugin-or-helper integrations. Keep credential prefixes isolated (`LINE_PERSONAL_*` vs official bot vars), verify Thrift/auth connectivity before plugin work, and fall back to a standalone script only when plugin discovery cannot load the integration.

## Absorbed development workflows

### Hermes configuration troubleshooting

Treat malformed auth/config files as an operations branch of plugin development: identify the active profile home, validate syntax before editing, back up the file, make the smallest repair, reload Hermes, and verify the original failing operation. Never print credentials. See `references/config-troubleshooting.md`.

### Desktop app plugins

Desktop UI extensions are a plugin specialization: use the desktop SDK's single ESM file, registered areas, host state/RPC, scoped storage, theme variables, and reload verification. Do not confuse desktop app plugins with Python plugins under `~/.hermes/plugins/`. See `references/desktop-plugins.md`.

### Skill authoring

When a plugin workflow becomes reusable, author a class-level SKILL.md with valid frontmatter, trigger-focused description, actionable steps, linked references/templates/scripts, and checkable verification. Keep bulky or session-specific material out of the main body. See `references/skill-authoring.md`.

## Remote MCP endpoint exposure and ChatGPT connector setup

When making a local MCP server reachable from ChatGPT Web or another cloud-hosted client, distinguish private tailnet access from public internet access: Tailscale Serve is tailnet-only, while Funnel publishes an HTTPS listener publicly. First inspect `tailscale serve status` and `tailscale funnel status`; do not replace an existing Funnel listener or Serve route just to add the MCP path. Prefer a separately available supported Funnel port and preserve existing routes. Verify the exact public URL, TLS, OAuth discovery endpoints, and an authenticated MCP initialize/list-tools exchange before registering the connector. Never treat a running tunnel or a private `*.ts.net` Serve URL as proof that ChatGPT's cloud can reach the endpoint. Keep OAuth secrets in the active profile's secret environment, not repository config or chat. If ChatGPT Web presents a login wall or security challenge, stop and ask the user to complete it; do not guess credentials or bypass it. See `references/remote-mcp-chatgpt-tailscale.md` for the observed Windows routing/OAuth checks and unresolved deployment gates.

## References

- `references/local-inference-scoring-plugin.md` — wrapping llama.cpp for schema-driven scoring: `n_predict:0`+`n_probs` logits read, the single-token contract, `enable_thinking:false`, restricted softmax, boolean key normalization.
- `references/porting-benchmark-comparison.md` — benchmarking a port against upstream README claims with the upstream grader, resumable chunked runs, error triage, baselines/CI/calibration reporting.
- `references/ngrok-tunnel-situations.md` — ngrok ERR_NGROK_334 stale-session recovery patterns.
- `references/line-personal-bridge.md` — implementation notes for personal LINE account bridging via linepy as a plugin.
- `references/hermes-plugin-manifest.md` — canonical plugin manifest examples.
- `references/absorbed-plugin-troubleshooting.md` — lm-twitterer/Pydantic, reload, filter, and external-checkout troubleshooting notes.
- `references/absorbed-tts-plugin-providers.md` — TTS provider plugin dispatch, config, verification, and Windows pitfalls.
- `references/fish-audio-provider.md` — Fish Audio REST contract and the verified Hermes wiring pattern.
- `references/absorbed-employee-and-linepy-plugins.md` — role/employee plugin scaffolding and linepy bridge notes.
- `references/third-party-auto-config.md` — reading Hermes .env and writing third-party tool config (SillyTavern pattern).
- `references/cli-binary-plugin-pattern.md` — wrapping a third-party CLI binary (vendor submodule + check_fn + structured tool schemas); includes Windows path-with-spaces pitfall and stateless handler pattern.
- `references/windows-docker-desktop-setup.md` — Docker Desktop installation on Windows (UAC limitation from bash, winget install, Buzz relay Docker Compose startup).
- `references/buzz-plugin-session-notes.md` — session-learned Buzz plugin corrections (port 8080 vs 3000, .env parsing, plugin.yaml requirement, CLI v0.2.0 syntax, Windows build pitfalls, tailnet exposure, required env).
