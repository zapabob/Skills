---
name: windows-game-install-safety
description: Verify Windows game installs without weakening security.
version: 0.1.0
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Windows, Gaming, Security, Verification]
    category: security
---

# Windows Game Installation Safety

Use this skill to distinguish an installer that merely reports success from a game that is complete, authentic, safe, and actually launchable. It does not bypass licensing, antivirus, driver-signature enforcement, Secure Boot, VBS, or anti-cheat protections; use an official storefront when an untrusted package requires those changes.

## When to Use

- “Install this Windows game and confirm it is playable.”
- “The installer succeeded, but the game executable is missing.”
- “This launcher asks me to disable VBS, DSE, Secure Boot, or antivirus.”
- “Verify whether this repack or unsigned installer is safe.”
- “Confirm that a Steam game is fully installed.”

## Prerequisites

- Windows user access to the intended install drive.
- For a licensed title, the user must complete storefront login, purchase, and payment interactions personally.
- Do not request or handle passwords, payment data, 2FA codes, or license keys.
- Keep Windows Security, Secure Boot, VBS, and driver-signature enforcement enabled during inspection.

## How to Run

Use `read_file` for launcher scripts and installer logs, `search_files` for expected executables and manifests, and the `terminal` tool for read-only process, registry, signature, and system-state checks. Use `computer_use` only for ordinary application controls; never click UAC, permission, payment, password, or security-disable prompts.

## Quick Reference

- Inno completion marker: `Installation process succeeded.`
- Steam manifest: `steamapps/appmanifest_<APPID>.acf`
- Steam launch URI: `steam://run/<APPID>`
- VBS state: `Win32_DeviceGuard`
- Hypervisor state: `Win32_ComputerSystem.HypervisorPresent`
- Authenticode state: `Get-AuthenticodeSignature`
- Installed-app registry: `HKLM/HKCU ... CurrentVersion\Uninstall`

## Procedure

1. **Identify the package and expected official source.**
   - Verify the exact title, publisher, storefront, and app ID from the publisher or storefront.
   - Treat search results as leads; prefer first-party publisher and storefront pages.
   - Do not assume that a familiar installer brand or matching file name establishes authenticity.

2. **Inventory without executing.**
   - Use `search_files` to locate the installer, archives, manifests, launchers, logs, and expected game executable.
   - Use `read_file` on text launchers such as `.bat`, `.cmd`, `.ini`, and installer logs.
   - Record installer signature status, publisher, hashes, archive sizes, target free space, and existing install locations.
   - Never add antivirus exclusions merely to make an unsigned installer run.

3. **Separate four completion gates.**
   - **Installer gate:** installer exited and logged completion.
   - **Payload gate:** expected executable and substantial game data exist.
   - **Authenticity gate:** publisher/storefront ownership and signatures are consistent.
   - **Playability gate:** the official executable launches to a stable menu without weakening OS security.
   - Passing the installer gate alone is never enough.

4. **Inspect launch scripts before running them.**
   - Confirm the working directory and executable path exist.
   - Treat references to missing executables as an incomplete payload, not as evidence that “first launch will generate it.”
   - Do not infer undocumented extraction behavior from leftover temporary files.

5. **Stop at security-boundary violations.**
   - Do not continue if a package asks to disable VBS, DSE, Secure Boot, antivirus, or Windows Hello to load an unsigned or test-signed kernel driver.
   - Do not run scripts that change BCD, Device Guard, credential isolation, anti-cheat services, or kernel-driver policy for a game crack.
   - If a security-changing menu is waiting for input, select its documented Exit option or ask the user to close it; do not select Continue.
   - Read-only verification that `HypervisorPresent=True` is useful evidence that the change has not yet taken effect.

6. **Contain active untrusted processes carefully.**
   - Enumerate process IDs, names, start times, paths, command lines, and window titles.
   - Stop only processes attributable to the inspected package; never terminate every `setup.exe` or `cmd.exe` by name.
   - Elevated processes may require the user to close their windows manually. State that blocker plainly rather than escalating privileges or guessing.

7. **Switch to the official installation route.**
   - Check for the official storefront manifest before claiming the game is installed.
   - Open the exact official storefront page for the verified app ID.
   - The user completes login, ownership, purchase, and payment.
   - Install into a storefront-managed library on the target drive, then use the storefront’s verify/repair function.

8. **Verify playable state.**
   - Confirm the official manifest is present and reports a completed install.
   - Confirm the expected signed executable exists in the storefront library.
   - Check that no security-disable script or unsigned kernel driver is required.
   - Launch through the official storefront and verify a stable main menu; do not claim completion from process creation alone.

9. **Report with explicit status.**
   - Use `Complete`, `Incomplete`, or `Blocked`.
   - List verified evidence, unresolved blockers, and the single next user action.
   - Never label an incomplete or security-degrading package a “normal installation.”

## Pitfalls

- Inno Setup can report success after installing only a launcher, uninstaller, redistributables, or placeholder files.
- A small installed size, missing primary executable, and absent storefront manifest are strong incomplete-install signals.
- Temporary `FreeArc`, `srep`, or similarly named files do not prove that extraction will resume on first launch.
- An uninstall registry entry proves registration, not authenticity or playability.
- Repeatedly launching a failed installer can leave duplicate elevated processes and multiple security-change prompts.
- Do not turn antivirus detection into a troubleshooting obstacle to “work around”; it is part of the risk assessment.
- `computer_use` must not approve UAC or security-permission dialogs. Ask the user when direct approval is required.
- For the detailed unsigned-hypervisor-loader pattern, load `references/unsigned-hypervisor-loader-case.md` with `skill_view`.

## Verification

The skill has succeeded only when the official storefront manifest and signed game executable exist, storefront verification passes, OS security remains enabled, and the game reaches a stable main menu.