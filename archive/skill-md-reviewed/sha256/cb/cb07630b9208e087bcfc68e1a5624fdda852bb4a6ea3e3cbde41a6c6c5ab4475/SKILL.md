---
name: petdex
description: Install, import, and select animated pet mascots for Hermes.
version: 1.0.0
author: Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [petdex, mascot, display, cli, tui, desktop]
    category: productivity
    homepage: https://petdex.dev
---

# Petdex Skill

Browse and select animated "pet" mascots from the public
[petdex](https://github.com/crafter-station/petdex) gallery, and **import
spritesheets that are not in that gallery** (ChatGPT shared pets, hand-made
atlases). An installed pet reacts to agent activity (idle, running a tool,
reviewing, error, done) across the Hermes CLI, TUI, and desktop app.

This skill drives the `hermes pets` CLI, the `display.pet` config, and one
import script. It does **not** generate sprites from a model — for that, see the
in-tree `agent/pet/generate/` path.

## When to Use

- The user wants a desktop/terminal mascot or asks about "pets" / petdex.
- The user wants to change, preview, or disable the active pet.
- The user shares a **ChatGPT pet link** (`chatgpt.com/s/sharepet_<id>`) or any
  other external spritesheet and wants it as a Hermes pet.
- Diagnosing why a pet isn't showing (terminal graphics support, config).

## Prerequisites

- Network access to `petdex.dev` for the gallery/manifest (read-only, no auth).
- Pillow (a core Hermes dependency) for sprite decoding — already installed.
- For full-fidelity terminal rendering: a graphics-capable terminal (kitty,
  Ghostty, WezTerm, iTerm2, or sixel). Otherwise a truecolor Unicode
  half-block fallback is used automatically.

## How to Run

Use the `terminal` tool to run `hermes pets <subcommand>`.

## Quick Reference

| Goal | Command |
| --- | --- |
| Browse the gallery | `hermes pets list` (add a substring to filter: `hermes pets list cat`) |
| List installed pets | `hermes pets list --installed` |
| Install a pet | `hermes pets install <slug>` (add `--select` to make it active) |
| Set the active pet | `hermes pets select <slug>` (omit slug for a picker) |
| Resize the pet everywhere | `hermes pets scale <factor>` (e.g. `0.5`, clamped 0.1–3.0) |
| Preview/animate in terminal | `hermes pets show [slug] [--cycle] [--state run]` |
| Disable the pet | `hermes pets off` |
| Remove a pet | `hermes pets remove <slug>` |
| Diagnose setup | `hermes pets doctor` |
| Preview one state | `hermes pets show --state run` (once: `--once`; cycle: `--cycle`) |
| Import a non-gallery sheet | `python scripts/import_spritesheet_pet.py --url <url> --slug <slug> --dry-run` |

## Procedure

1. Find a pet: `hermes pets list <query>` and note its `slug`.
2. Install + activate: `hermes pets install <slug> --select`.
3. Preview it: `hermes pets show` (Ctrl+C to stop).
4. Confirm setup: `hermes pets doctor` — shows the resolved pet, configured
   render mode, detected terminal graphics protocol, and effective mode.

Pets install into `<HERMES_HOME>/pets/<slug>/` (profile-aware). Selecting a pet
writes `display.pet.slug` + `display.pet.enabled` to `config.yaml`.

## Importing a non-gallery spritesheet

`hermes pets install <slug>` **cannot** do this. `agent/pet/store.py::install_pet`
calls `_is_petdex_host()` on both the manifest entry and the asset URLs, and
raises `PetStoreError("refusing non-petdex spritesheet host for ...")` for any
host that is not `petdex.dev` or `*.petdex.dev`. That pin is a deliberate
anti-SSRF control — do not work around it by editing the source; write the pet
into the store directly instead.

There is no `import_pet` CLI. `export_pet()` produces a "re-importable" zip,
but nothing in the tree reads one back — verified by search.

Use the bundled script (stdlib + Pillow only):

```
python scripts/import_spritesheet_pet.py \
  --url "<sprite-url>" --slug hakua \
  --display-name "Hakua" --description "..." --source "<page-url>" --dry-run
```

Drop `--dry-run` to write, then `hermes pets select <slug>`.

### The atlas contract (`agent/pet/constants.py`)

| Constant | Value | Consequence |
| --- | --- | --- |
| `FRAME_W` / `FRAME_H` | 192 / 208 | Sheet dims must be exact multiples, or the grid is undecidable |
| `FRAMES_PER_STATE` | 6 | Only the **first 6 columns** ever animate (petdex CSS `steps(6)`) |
| `CODEX_STATE_ROWS` | 9 rows | Used when `row_count >= 9` — the current shape, 1536x1872 |
| `LEGACY_STATE_ROWS` | 8 rows | Fallback for older sheets |

Row names map to Hermes activity states through `STATE_ALIASES`
(`wave`→`waving`, `jump`→`jumping`, `run`→`running`). A sheet with **more**
rows than the taxonomy still renders: `state_rows_for_grid()` returns
`CODEX_STATE_ROWS` for any `row_count >= 9`, so extra trailing rows are simply
never played. Truncating to 9 keeps the asset byte-comparable with the other
installed pets.

`pet.json` keys: `id`, `displayName`, `description`, `spritesheetPath`, and
`createdBy`. **Leave `createdBy` empty for an imported pet** — the value
`"generator"` is what `register_local_pet()` stamps on locally-hatched pets and
`InstalledPet.generated` keys off it.

Encode the spritesheet **lossless**: `format="WEBP", lossless=True, quality=100,
method=6, exact=True`, matching `store.py::_write_spritesheet`. Gallery pets are
1.0–2.2 MiB; a sub-500 KiB file means you saved lossy and silently degraded the
art.

### Fetching a ChatGPT shared pet

The share page is a React Router app whose pet metadata is **not** in static
HTML — read it from the server-injected loader payload
`__reactRouterContext.streamController.enqueue(...)`, which carries
`spritesheet_url`, `name`, and `description`. Use `web_extract` on the page and
search for `spritesheet_url`.

The spritesheet endpoint returns **403 `text/html`** to a bare request. Sending
a browser header set (`User-Agent`, `Accept: image/*`, `Referer:
https://chatgpt.com/`, `Sec-Fetch-Dest: image`, `Sec-Fetch-Mode: no-cors`,
`Sec-Fetch-Site: same-origin`) returns **200 `image/png`**. Verified.

**The 403 body is HTML.** A `.png` filename does not make it one — check the
magic bytes (`\x89PNG`) before handing bytes to Pillow, or you get
`cannot identify image file` with no useful cause.

### Verifying an imported sheet

Measure, don't eyeball:

- **Per-row non-empty frame count** — a row below `cols` is normal. Some
  animation frames are intentionally blank (a waving cycle resting between
  arm positions, a jump's airborne peak). Only an all-empty row is a defect.
- **Per-row uniqueness of the first 6 frames** — this catches copied placeholder
  art. **Hash RGBA, never RGB**: a transparent frame and a second transparent
  frame are identical in RGB after alpha is dropped, so an RGB hash reports
  spurious collisions on perfectly correct sheets.
- **A repeated frame that is *empty* is padding, not a duplicate animation
  pose.** Both hash and `getbbox() is None`. Sheet tails are routinely padded to
  `FRAMES_PER_STATE` with blank cells; that is not a bug and needs no repair.

An 11-row ChatGPT sheet measured `5/6 unique` on the `waving` row for exactly
this reason — columns 4 and 5 are both fully transparent. Reporting that as "a
duplicated frame" is a false positive.

For a human check, render a contact sheet (states x frames) with Pillow and open
it via `open_preview`.

## Configuration

Under `display.pet` in `config.yaml`:

- `enabled` (bool) — master on/off.
- `slug` (str) — active pet; empty = first installed.
- `render_mode` — `auto` (detect) | `kitty` | `iterm` | `sixel` | `unicode` | `off`.
- `scale` (float) — on-screen size of the native 192×208 frames (default 0.33,
  clamped 0.1–3.0). One knob resizes every surface; set it with
  `hermes pets scale <factor>`, the `/pet scale` slash command, or the desktop
  Appearance slider.
- `unicode_cols` (int) — width in columns for the Unicode fallback.

## Pitfalls

- A pet only shows once one is installed AND selected (`enabled: true`).
- Inside a pipe/redirect (no TTY) terminal rendering is disabled by design.
- The petdex npm CLI installs to `~/.codex/pets`; Hermes uses its own
  profile-scoped `<HERMES_HOME>/pets/` instead — install through `hermes pets`.
- `hermes pets install` rejects non-petdex hosts by design; use the import
  script rather than loosening `_is_petdex_host`.
- A sheet whose dimensions are not a multiple of 192x208 has no inferable grid —
  the script exits rather than guessing.
- Blank frames inside a row are normal; blank *rows* are not.
- Uniqueness must be measured on RGBA. On RGB, transparent frames collide.
- Lossy WebP silently degrades the art. Gallery pets are 1.0-2.2 MiB.
- `vision_analyze` can fail with `Connection error` on local files. When visual
  confirmation is the last step, open the image with `open_preview` and let the
  user look, rather than looping on a failing tool.

## Verification

`hermes pets doctor` reports `✓ ready` when a pet is installed, selected,
enabled, and Pillow is importable. For an import, the script's own frame table
is the check: every row non-empty, and the first 6 columns unique per row.
Confirm the write landed by reading back the dimensions:

```
python -c "from PIL import Image; print(Image.open('<HERMES_HOME>/pets/<slug>/spritesheet.webp').size)"
```

Expect a multiple of `(192 * 8, 208 * 9)` = `(1536, 1872)` after normalization.
