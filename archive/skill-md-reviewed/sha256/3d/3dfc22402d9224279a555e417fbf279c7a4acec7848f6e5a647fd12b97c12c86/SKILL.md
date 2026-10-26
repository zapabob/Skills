---
name: buzz-project-operations
description: Build/test/deploy BUZZ Nostr relay/CLI on Windows MSVC.
category: devops
---

# BUZZ Project Operations

Class-level skill for building, testing, deploying, and operating the BUZZ (block/buzz) Nostr relay, desktop, mobile, and CLI project on Windows with MSVC.

## Build Environment Setup

### MSVC Toolchain Selection
**Critical**: Use Visual Studio 2022 **Community** (stable), not Insiders. The Insiders MSVC (14.50.x) has compatibility issues with ring/aws-lc-sys.

```bash
# Verify correct MSVC is selected
rustup show
# Should show stable-x86_64-pc-windows-msvc (not Insiders)

# If pinned to Insiders via rust-toolchain.toml, override:
rustup override set stable
```

### Environment Variables
```bash
# Disable sccache wrapper (breaks on Windows in this env)
export RUSTC_WRAPPER=""
export SCCACHE_DISABLE=1

# Use 4-core parallel builds
export CARGO_BUILD_JOBS=4

# Target directory WITHOUT spaces (Windows path issue)
export CARGO_TARGET_DIR="/c/buzz_target"  # or /tmp/buzz_build
```

### VS 2022 Developer Command Prompt
Always run cargo inside `vcvars64.bat` environment:
```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cargo build --release -j 4 -p buzz-cli
```

## Cargo Workspace Build Workarounds

### 1. OUT_DIR Bug (Cargo 1.95+ on Windows)
Build scripts for `serde_core`, `aws-lc-sys`, `ring` fail with "file not found" because Cargo doesn't create `out/` directories.

**Workaround**: Build problematic crates serially first:
```bash
# Phase 1: Build problematic crates serially
cargo build --release -j 1 -p serde_core -p serde -p getrandom -p cc

# Phase 2: Full parallel build
cargo build --release -j 4 -p buzz-cli
```

### 2. Windows Path Spaces
Project path contains spaces (`New project`) → breaks `target/release` creation.

**Solution**: Set `CARGO_TARGET_DIR` to path without spaces:
```bash
export CARGO_TARGET_DIR="/c/buzz_target"
# or
export CARGO_TARGET_DIR="/tmp/buzz_build"
```

### 3. Native Dependencies (ring, aws-lc-sys, secp256k1)
These require working MSVC `cl.exe` with Windows SDK include paths. Ensure:
- Windows 10 SDK (10.0.22621.0+) installed
- `INCLUDE` and `LIB` env vars set by `vcvars64.bat`

### 4. MSYS2 / git-bash `cmd.exe` Argument Translation Trap (**CRITICAL on this host**)
Running `cmd.exe //c "<bat> <args>"` (or `.bat` files with paths) from the Hermes
terminal (git-bash / MSYS2) is **unsafe**: MSYS2 path translation rewrites paths like
`C:\Users\...` into `/c/Users/...`, then `cmd.exe` re-translates them further, producing
nested garbage dirs like `/c/c/Users/...` and recursive `cmd.exe` spawns that never
terminate (empty build log, 35+ hung `cmd.exe` processes, exit 0 but no output).

**Symptom**: `build_log.txt` is empty, many `cmd.exe` processes in Task Manager, cargo
never actually compiles, exit code 0.

**Workaround that works — drive the build from a Python script via `subprocess`** (no
shell-level `cmd.exe` invocation, no MSYS path mangling). A known-good script lives at
`scripts/buzz_build.py`. It:
1. Runs `vcvars64.bat && set` via `subprocess.run(..., shell=True)` to capture MSVC env
   vars, parsing `KEY=VALUE` lines and merging them into `os.environ`.
2. Sets `RUSTUP_TOOLCHAIN=stable` + `CARGO_TARGET_DIR` to a space-free path + clears
   `RUSTC_WRAPPER`/`SCCACHE_DISABLE`.
3. Uses `encoding="utf-8", errors="replace"` — vcvars64 emits cp932 bytes that crash a
   naive `utf-8` decode (`UnicodeDecodeError: byte 0x81`), so never decode stdout as
   strict utf-8.
4. Phase 1: serial build of `serde_core`, `serde`, `cc`, and **all three getrandom
   versions explicitly** (see §5). Phase 2: `cargo build --release -j 4 -p buzz-cli`.

Run it with a **plain Windows path** (do NOT route through MSYS):
```bash
py -3 '%USERPROFILE%\Documents\New project\hermes-agent\tmp\buzz_build.py' > '<log>.log' 2>&1
```
Note: `py -3 /c/Users/...` in git-bash converts to `/c/c/Users/...` and fails with
"can't open file". Always quote the **backslash-Windows** path.

### 5. `getrandom` Version Ambiguity Error (Cargo.lock has 0.2.17 / 0.3.4 / 0.4.3)
`buzz` pulls three `getrandom` major versions. A bare `cargo build -p getrandom` can
fail with "multiple packages named `getrandom`" ambiguity. Build each pinned version
explicitly in Phase 1:
```bash
cargo build --release -p getrandom@0.2.17 -p getrandom@0.3.4 -p getrandom@0.4.3
```
All three compile in ~2s and unblock the full `buzz-cli` build.

## BUZZ CLI Binary

**Name**: `buzz` (not `buzz-cli`)
**Location**: `$CARGO_TARGET_DIR/release/buzz.exe`

## Build Automation Script

`scripts/buzz_build.py` is a known-good, copy-and-run driver that bakes in every
workaround above (vcvars64 env capture, getrandom 3-version build, MSYS trap
avoidance, utf-8 error-tolerant decode). Copy it to a space-free path and run with a
**backslash-Windows** path:
```bash
py -3 "%USERPROFILE%\Documents\New project\hermes-agent\tmp\buzz_build.py" > build.log 2>&1
```
Edit `SRC`, `VCVARS`, `TARGET_DIR` at the top if your layout differs.

### Key Commands for Hermes Agent Communication
```bash
# Configuration
export BUZZ_RELAY_URL="ws://localhost:3000"
export BUZZ_PRIVATE_KEY="<hex-or-nsec>"
# Optional NIP-OA auth
export BUZZ_AUTH_TAG='***'

# Agent/channel management
buzz agents draft-create --name "hermes-agent" --owner <pubkey>
buzz channels create --name "hermes-swarm" --topic "Task coordination"
buzz channels add-member --channel <uuid> --member <agent-pubkey>

# Messaging
buzz messages send --channel <uuid> --content "Task completed" --mentions <pubkey>
buzz messages get --channel <uuid> --limit 50

# Direct messages
buzz dms open --members <pubkey1>,<pubkey2>
buzz dms list

# Workflows (multi-agent orchestration)
buzz workflows create --file coordination.yaml --channel <uuid>
buzz workflows trigger --workflow <uuid>
buzz workflows runs --workflow <uuid>

# Presence & profiles
buzz users set-presence --status online
buzz users set-status --text "Processing task #42"
```

## BUZZ SDK Integration (Rust)

```rust
use buzz_sdk::{builders::build_message, Client, Config};

// Build events programmatically
let event = build_message(
    channel_id,
    "Hermes Agent: Task completed",
    None,           // thread_ref
    &[other_agent_pubkey], // mentions
    false,          // broadcast
    &[],            // media_tags
)?;

// Send via client
let client = Client::new(Config::from_env()?);
client.publish(event).await?;
```

### Agent Observer Frames (Encrypted Telemetry)
```rust
use buzz_sdk::builders::build_agent_observer_frame;

// NIP-44 v2 encrypted telemetry to owner
let frame = build_agent_observer_frame(
    owner_pubkey,
    agent_pubkey,
    "telemetry",  // or "control"
    encrypted_payload,  // NIP-44 v2 ciphertext
)?;
```

## Common Pitfalls & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `sccache: file not found` | RUSTC_WRAPPER=sccache but sccache broken | `export RUSTC_WRAPPER="" SCCACHE_DISABLE=1` |
| `failed to create directory target/release` | Path contains spaces | Set `CARGO_TARGET_DIR` to space-free path |
| `stddef.h not found` / `cl.exe` errors | Wrong MSVC (Insiders) or missing Windows SDK | Use VS 2022 Community + `vcvars64.bat` |
| `OUT_DIR not found` in build.rs | Cargo 1.95 Windows bug | Build serde_core/aws-lc-sys/ring serially first |
| `buzz-cli not found` | Binary is named `buzz` | Use `buzz.exe` or `cargo run -p buzz-cli` |
| Empty build log + many hung `cmd.exe` procs, exit 0 | MSYS2 `cmd.exe //c` path translation trap (`/c/c/...` nesting, recursive cmd spawns) | Never shell-invoke `cmd.exe`/`.bat` from git-bash. Drive cargo from `scripts/buzz_build.py` (Python subprocess) with a **backslash-Windows** path |
| `multiple packages named \`getrandom\`` | Cargo.lock pins 0.2.17 + 0.3.4 + 0.4.3 | Build each explicitly: `-p getrandom@0.2.17 -p getrandom@0.3.4 -p getrandom@0.4.3` (Phase 1) |
| `UnicodeDecodeError: byte 0x81` reading vcvars64 output | vcvars64 emits cp932 bytes | Decode subprocess stdout with `encoding="utf-8", errors="replace"` |

## Testing & Verification

```bash
# Quick smoke test
cargo run --release -p buzz-cli -- --help

# Check relay connectivity
buzz users get --pubkey <your-pubkey>

# Run integration tests (needs Postgres + Redis)
just test
```

## Relay Deployment (Docker Desktop)

`buzz relay` needs Postgres + Redis (per `docker-compose.yml`):
```bash
cd vendor/buzz
docker compose -f deploy/compose/compose.yml --env-file deploy/compose/.env up -d
# relay container runs /usr/local/bin/buzz relay — listens on :3000
```

### Relay boot-stuck fixes (verified 2026-08-08)

1. **`invalid BUZZ_RELAY_PRIVATE_KEY` restart loop**: `.env` ships with a
   zero-filled key (`000...0`), which the relay rejects at startup and restarts
   forever. Generate a real one:
   ```bash
   KEY=$(openssl rand -hex 32)
   sed -i "s/^BUZZ_RELAY_PRIVATE_KEY=.*/BUZZ_RELAY_PRIVATE_KEY=$KEY/" deploy/compose/.env
   ```
2. **`RELAY_OWNER_PUBKEY` zero-filled → owner bootstraps as pubkey `0000...`**:
   the owner pubkey must be the pubkey *derived* from `BUZZ_RELAY_PRIVATE_KEY`,
   not a placeholder. Derive with coincurve:
   ```bash
   PUB=$(py -3 -c "import coincurve,re; env=open('deploy/compose/.env').read(); priv=re.search(r'^BUZZ_RELAY_PRIVATE_KEY=(\S+)',env,re.M).group(1); print(coincurve.PrivateKey(bytes.fromhex(priv)).public_key.format(compressed=True).hex())")
   sed -i "s/^RELAY_OWNER_PUBKEY=.*/RELAY_OWNER_PUBKEY=$PUB/" deploy/compose/.env
   ```
   (Requires `py -3 -m pip install coincurve`.)
3. Restart the relay: `docker compose -f deploy/compose/compose.yml --env-file deploy/compose/.env up -d relay`.
   Healthy log line to wait for: `buzz-relay TCP listening addr 0.0.0.0:3000` + container status `(healthy)`.

### Client-side env for Hermes plugin / CLI

The Hermes buzz plugin reads `BUZZ_RELAY_URL` / `BUZZ_PRIVATE_KEY` from
`~/.hermes/.env` (also `vendor/buzz/.env`, `vendor/buzz/deploy/compose/.env`).
Point it at the running relay:
```bash
echo 'BUZZ_RELAY_URL=http://localhost:3000' >> ~/.hermes/.env
echo "BUZZ_PRIVATE_KEY=$(grep '^BUZZ_RELAY_PRIVATE_KEY=' deploy/compose/.env | cut -d= -f2)" >> ~/.hermes/.env
```
Then verify a full round-trip with the CLI:
```bash
export BUZZ_RELAY_URL=http://localhost:3000 BUZZ_PRIVATE_KEY=<key>
buzz channels list                     # [] on a fresh relay
buzz channels create --name ai-external --type stream --visibility open
buzz messages send --channel <uuid> --content "hello"
buzz messages get --channel <uuid>     # read the message back
```
Note: the flag is `--content` for `messages send` (not `--text`), and reading is
`messages get` (not `list`/`read`).

### Exposing the relay to external AI agents

Docker alone gives a local-only relay. For *external* agents to reach it, expose
with ngrok (Tailscale serve unavailable on this host):
```bash
ngrok http 3000 --log=stdout          # background process
curl -s http://127.0.0.1:4040/api/tunnels | python -c "import json,sys; print(json.load(sys.stdin)['tunnels'][0]['public_url'])"
# e.g. https://remedial-joline-unrash.ngrok-free.dev
```
The free ngrok URL is **session-dependent** — it changes on ngrok restart, so
re-fetch it before sharing. External agents then connect to
`https://<ngrok-url>` and join the open channel.

**Docker Desktop engine won't start → diagnose a WSL hang FIRST (verified 2026-08-08, no admin needed).**

Symptom cluster observed on this host:
- `docker info` times out forever; Docker Desktop log shows `backend exited before becoming ready`
- `wsl -l -v` / `wsl --shutdown` also hang (WSL service wedged)
- Docker Desktop electron log: `DockerDesktop/Wsl/CommandTimedOut: wsl.exe -l -v --all`
- Often aggravated by **C: drive nearly full** (~10GB free) — WSL2 VHDX can't expand

Recovery that works from a non-admin Hermes terminal:
```bash
# 1. Kill every Docker/WSL-launch process (some need /T for trees)
taskkill /F /IM docker-desktop.exe /T
taskkill /F /IM com.docker.backend.exe /T
taskkill /F /IM "Docker Desktop.exe" /T
taskkill /F /IM wslrelay.exe /T

# 2. Shut WSL down; retry after the taskkills — give it ~45s
wsl --shutdown

# 3. Relaunch via PowerShell — MSYS `start` mangles the space in
#    "Docker Desktop.exe" into `docker: unknown command: docker Desktop.exe`
powershell.exe -NoProfile -Command "Start-Process -FilePath 'C:\Program Files\Docker\Docker\Docker Desktop.exe'"

# 4. Poll until the daemon answers (up to ~5 min; docker-desktop distro should show Running)
for i in {1..100}; do docker info >/dev/null 2>&1 && echo READY && break; sleep 3; done

# 5. If C: is <15GB free, free space first (Temp/npm/pip caches, see
#    windows-di[REDACTED_TOKEN]) before relaunching.
```
Only if the WSL-recovery path fails repeatedly should you ask the user to launch
Docker Desktop manually — do not silently loop-retry the launch.