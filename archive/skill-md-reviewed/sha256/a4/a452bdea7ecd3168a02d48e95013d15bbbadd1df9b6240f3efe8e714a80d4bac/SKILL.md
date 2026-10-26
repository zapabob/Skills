---
name: desktop-theme-background-integration
description: "Use for Hermes Desktop image skin backgrounds."
version: 1.0.0
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [desktop, themes, skins, wallpaper, packaging, verification]
    related_skills: [hermes-themes, hakua-desktop-themes, hermes-runtime-operations]
---

# Desktop Theme Background Integration

Use this class-level workflow when a Hermes Desktop theme should display an image, especially a user/Hakua GPT-image background. A YAML setting alone is not proof that the installed Desktop renderer can display it.

## Core workflow

1. **Inspect before editing.** Trace the complete path:
   - skin YAML under `$HERMES_HOME/skins/`
   - Python skin model and backend `resolve_skin()` payload
   - shared `HermesSkin` type
   - Desktop skin converter (`skinToDesktopTheme`)
   - theme context/application
   - actual mounted backdrop component
   - Electron filesystem bridge (`readFileDataUrl`)
   - packaged and installed Desktop artifact
2. **Keep image keys top-level.** Use:
   ```yaml
   background_image: "twilight-hakua-portrait-bg.png"
   background_image_fit: "cover"
   background_image_position: "center"
   background_overlay: "#1a1030aa"
   ```
   Resolve relative names to an absolute path in the backend payload when possible. Keep the relative form valid for CLI/TUI consumers.
3. **Render through the existing bridge.** Do not widen the renderer to Node/Electron APIs. Convert the image path through `window.hermesDesktop.readFileDataUrl`, then render a non-interactive `<img>` layer behind chat content. `cover` is the default for desktop wallpaper; use a contrast overlay for busy artwork.
4. **Provide a narrow compatibility fallback.** If an older backend has not broadcast extended skin fields, the renderer may use a known local fallback path on the target machine. Do not silently fall back from a failed authoritative image read to an unrelated remote URL.
5. **Build the renderer and package the Desktop app.** `npm run build` proves the renderer/package build. For the actual Windows executable use:
   ```bash
   hermes desktop --build-only --force-build
   ```
6. **Synchronize the artifact actually launched.** The source/repo release path and LocalAppData installed path may differ. On Windows, stop Hermes completely before copying; a running `Hermes.exe` can lock the executable and leave the old app active. Then synchronize the packaged `win-unpacked` directory to `%LOCALAPPDATA%\hermes\hermes-agent\apps\desktop\release\win-unpacked`. Verify the destination `Hermes.exe` timestamp/hash or packaged asset contents before launching.

## Verification gates

Run all applicable gates, not just one:

- `hermes config get display.skin`
- load the skin through Python and assert `background_image`, `fit`, `position`, and overlay
- Desktop typecheck: `npm run typecheck`
- targeted renderer tests for skin conversion/backend sync
- Python skin tests (`tests/hermes_cli/test_skin_engine.py`)
- verify the image file exists and is non-empty
- verify the Windows wallpaper registry/current wallpaper only when the user explicitly requested the OS desktop wallpaper; do not confuse it with the Hermes app background
- after packaging, verify the launched artifact is the newly built copy

## Pitfalls

- **Most common false success:** the YAML and source build are updated, but the running Desktop uses a stale LocalAppData package. Always verify the launch path.
- **Second common false success:** image fields are present in the YAML but are dropped by `SkinConfig`, `resolve_skin()`, the shared type, or `skinToDesktopTheme`. Trace each boundary.
- A wallpaper file in `$HERMES_HOME/skins/` is not automatically bundled into the app; it should be read through the Electron bridge from the filesystem.
- A parent surface with an opaque background or a wrong stacking context can hide the image. Keep the image layer inside the mounted chat surface, behind content but above the parent background.
- Do not claim the image is visible solely because tests pass. Test output proves code paths, not the user's current window; inspect/relaunch the actual installed app when possible.
- On Windows, `robocopy` exit codes 0–7 are non-fatal; code 3 commonly means a copy succeeded with extras but a locked file prevented full mirroring. Treat that as incomplete until the lock is removed and the destination is rechecked.

## Supporting detail

See `references/verified-windows-recipe.md` for the concrete path and verification recipe from the validated workflow.
