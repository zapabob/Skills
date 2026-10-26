---
name: hakua-desktop-themes
description: "Create Hakua GPT-image-2 desktop skins with character art."
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [theme, skin, hakua, desktop, gpt-image2, background-image, character]
    related_skills: [hermes-themes]
---

# Hakua Desktop Themes Skill

Create Hermes Desktop skins featuring **はくあ** character portraits generated via **GPT-image-2**, with cinematic twilight/atmospheric backgrounds and coordinated color palettes.

## When to Use

- User wants a Hakua-themed desktop skin with character portrait background
- User requests "GPT-image-2 style" or "cinematic" themes for Hermes Desktop
- User wants twilight/dusk/sunset atmospheric themes with Hakua character

## Prerequisites

- Hermes Desktop installed and running
- `~/.hermes/skins/` directory exists (create if needed)
- GPT-image-2 / FAL.ai access for image generation (via `image_generate` tool)
- SillyTavern character images at `vendor/SillyTavern/data/default-user/characters/はくあ.png`

## Workflow

### 1. Generate Character Background Image

Use `image_generate` with portrait/landscape prompts featuring Hakua:

```python
# Portrait (9:16) for vertical character focus
image_generate(
    aspect_ratio="portrait",
    prompt="Anime girl Hakua (silver-white hair, gentle expression, golden eyes). Background: deep indigo-purple twilight sky to warm coral-amber horizon. Soft god rays, atmospheric haze. Cinematic anime art, 9:16 portrait."
)

# Landscape (16:9) for desktop wallpaper
image_generate(
    aspect_ratio="landscape",
    prompt="Hakua character integrated into cinematic twilight desktop wallpaper. Silver-white hair, gentle expression. Deep indigo to coral-amber gradient sky. 16:9, high quality anime illustration."
)
```

Download via `curl` to `~/.hermes/skins/<theme>-bg.png`.

### 2. Copy Character Image

```bash
cp "vendor/SillyTavern/data/default-user/characters/はくあ.png" \
   "~/.hermes/skins/hakua-character.png"
```

### 3. Create Skin YAML with Background Image Keys

Add these **top-level keys** (not under `colors:`):

```yaml
background_image: "twilight-hakua-portrait-bg.png"
background_image_fit: "cover"
background_image_position: "center"
background_overlay: "#1a1030aa"  # 8-digit hex ARGB for UI readability
```

### 4. Design Coordinated Color Palette

Extract dominant colors from generated image (Python/PIL analysis):

```python
# Sample script extracts average, dominant colors
# Use to set: background, ui_accent, ui_accent_alt, ui_accent_tertiary
# Text colors: warm off-whites for readability over dark backgrounds
```

**Twilight Palette Example:**
| Role | Color | Source |
|------|-------|--------|
| Background | `#1a1030` | Deep indigo (image top) |
| Primary Accent | `#e87a5a` | Coral horizon glow |
| Secondary Accent | `#ffb84d` | Golden amber sunset |
| Tertiary Accent | `#a87ae8` | Lavender sky mid-tones |
| Text Primary | `#ffe8d0` | Sunlit warm white |
| Text Secondary | `#e8d8c8` | Pale warm |
| Success | `#6ecf8a` | Night breeze green |
| Warning | `#ffb84d` | Amber |
| Error | `#e85a7a` | Warm coral (not harsh red) |

### 5. Add Hakua Branding

```yaml
branding:
  agent_name: "はくあ"
  prompt_symbol: "❯"
  welcome: "黄昏時だね、パパ。今日もお疲れ様。"
  goodbye: "おやすみ。いい夢見てね。"
  help_header: "🌅 コマンド一覧"
tool_prefix: "┊"
```

### 6. Write Skin File & Activate

```bash
# Write to ~/.hermes/skins/twilight-hakua.yaml
hermes config set display.skin twilight-hakua
```

The gateway's skin watcher repaints all surfaces (CLI, TUI, Desktop) live.

## Background Image Configuration Reference

| Key | Values | Notes |
|-----|--------|-------|
| `background_image` | filename.png | Relative to `skins/` dir |
| `background_image_fit` | `cover` \| `contain` \| `fill` \| `scale-down` | `cover` recommended |
| `background_image_position` | `center` \| `top` \| `bottom` \| `left` \| `right` \| `%` | `center` default |
| `background_overlay` | `#RRGGBBAA` | 8-digit hex ARGB, semi-transparent for text contrast |

## Color Extraction Helper

```bash
# Quick dominant color analysis
python3 -c "
from PIL import Image
import numpy as np
from collections import Counter
img = Image.open('skins/twilight-hakua-portrait-bg.png').convert('RGB')
arr = np.array(img)
h, w = arr.shape[:2]
grid = []
for y in range(0, h, h//20):
    for x in range(0, w, w//20):
        if y < h and x < w:
            c = arr[y, x]
            grid.append('#{:02x}{:02x}{:02x}'.format(*c))
from collections import Counter
for c, n in Counter(grid).most_common(15):
    print(f'  {c}: {n}')
"
```

## Examples Created

| Theme | Background | Palette |
|-------|------------|---------|
| `twilight-hakua` | `twilight-hakua-portrait-bg.png` + `hakua-character.png` | Deep indigo → coral → amber → lavender |
| `gpt-image2-warm` | (none) | Warm neutral grays, beige/gold accents |
| `hakua-cyber` | (none) | Cyberpunk magenta/cyan on deep indigo |

## Pitfalls

- **Image path**: Must be in `~/.hermes/skins/` (not subdirs) for current Desktop GUI
- **Overlay opacity**: Use `aa` (170/255) for readable text over busy character images
- **Contrast**: Test `background` color as fallback — CLI/TUI don't show background image
- **Naming**: Avoid built-in skin names (`mono`, `slate`, `cyberpunk`, `nous`, `midnight`, `ember`)

## Verification

1. `read_file ~/.hermes/skins/<theme>.yaml` — valid YAML, all keys present
2. `hermes config get display.skin` — reports `<theme>`
3. Restart Hermes Desktop — background image + coordinated palette visible
4. CLI/TUI — palette applied (background color used, not image)