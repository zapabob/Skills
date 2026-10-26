---
name: unity-cli-install
description: Install Unity CLI with channel selection on Windows.
version: 0.1.0
author: Hermes
platforms: [windows]
tags: [Windows, Unity, Installation, DevOps]
metadata:
  hermes:
    tags: [Windows, Unity, Installation, DevOps]
---

# Unity CLI Install (Windows)

Installs Unity's official CLI (`unity.exe`) for managing Unity editor installations, builds, projects, and modules from the command line. Supports stable, beta, and alpha release channels. The installer downloads a self-contained binary, verifies its SHA-256 checksum, and adds it to the User PATH.

## When to Use

- User says "install Unity CLI" or "setup unity cli"
- User needs `unity` commands for editor management on Windows
- User specifies a particular channel (stable / beta / alpha)
- User is setting up CI/CD tooling that requires Unity CLI

## Prerequisites

- Windows x64 or ARM64 system
- Internet access to `public-cdn.cloud.unity3d.com`
- Running from Hermes on Windows (`computer_use` or `terminal` with `powershell.exe`)

## How to Run

The installer is a PowerShell script piped from `invoke-webrequest` (irm). When run from Hermes' bash terminal, `$env:UNITY_CLI_CHANNEL` must be escaped with a backslash so bash does not expand it.

## Quick Reference

| Purpose | Command |
|---------|---------|
| Install latest beta | `\$env:UNITY_CLI_CHANNEL='beta'` + irm + iex |
| Install latest alpha | `\$env:UNITY_CLI_CHANNEL='alpha'` + irm + iex |
| Install latest stable | Omit channel env var (default) |
| Install pinned version | Replace `latest` with version string |
| Binary location | `%LOCALAPPDATA%\Unity\bin\unity.exe` |

## Procedure

### 1. Set the channel (optional)

The env var `UNITY_CLI_CHANNEL` selects the version manifest. Valid values: `beta`, `alpha`, or empty (stable). Set it **before** the install command:

```bash
# bash (from Hermes terminal) — escape $ so bash doesn't expand it
export UNITY_CLI_CHANNEL='beta'  # not consumed by bash, passed to PowerShell
```

Alternatively, set it in the PowerShell command itself (preferred — avoids bash/PS env confusion).

### 2. Run the installer

Invoke via `terminal`:

```bash
# Beta channel (escape $env)
powershell.exe -NoProfile -Command "\$env:UNITY_CLI_CHANNEL='beta'; irm https://public-cdn.cloud.unity3d.com/hub/prod/cli/install.ps1 | iex"

# Stable channel (no env var needed)
powershell.exe -NoProfile -Command "irm https://public-cdn.cloud.unity3d.com/hub/prod/cli/install.ps1 | iex"
```

The script:
- Detects x64 vs ARM64 architecture automatically
- Downloads the latest manifest from `latest-beta.json` (or `latest.json` / `latest-alpha.json`)
- Downloads the binary (~100 MB) to a temp path
- Verifies the SHA-256 checksum
- Moves it to `%LOCALAPPDATA%\Unity\bin\unity.exe`
- Adds the install directory to the User PATH

### 3. Verify installation

The installer confirms with a checkmark and version number. For additional verification:

```bash
# Run via full path (PATH may not be picked up in current session)
powershell.exe -NoProfile -Command "& '%LOCALAPPDATA%\Unity\bin\unity.exe' --help"

# Or from bash via MSYS path
/c/Users/$(whoami)/AppData/Local/Unity/bin/unity.exe --help
```

## Pitfalls

- **bash interprets `$env:`** — Always escape the dollar sign (`\$env:`) when running the PowerShell one-liner from within bash/MSYS. Without the backslash, bash expands `$env` to an empty string and the channel selection is silently dropped (defaulting to stable).
- **PATH not visible in current shell** — The installer broadcasts `WM_SETTINGCHANGE` so new GUI-launched processes pick up the PATH, but already-open terminal sessions (including this bash shell and any PowerShell spawned from it) retain their original PATH. Either restart the terminal or use the full path.
- **Channel manifest naming** — Stable: `latest.json`, beta: `latest-beta.json`, alpha: `latest-alpha.json`. All hosted at `https://public-cdn.cloud.unity3d.com/hub/prod/cli/`.
- **Script execution policy** — The default `irm | iex` pattern works in most environments. If execution policy blocks it, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.
- **`-NoProfile` is recommended** — Avoids loading user PowerShell profile modules that may interfere.

## Verification

```bash
powershell.exe -NoProfile -Command "& '%LOCALAPPDATA%\Unity\bin\unity.exe' --version"
```

Expected output: `1.0.0-beta.3` (or the installed version), confirming the binary runs and reports its version.
