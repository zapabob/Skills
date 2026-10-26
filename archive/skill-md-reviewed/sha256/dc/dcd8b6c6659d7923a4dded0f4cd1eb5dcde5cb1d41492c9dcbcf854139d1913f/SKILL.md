---
name: numpy-pil-cv2-video-qc
description: Render MP4 from numpy/PIL/cv2, with text layout pre-checks, vision look-test, contact sheet, and frame-diff QC.
version: 0.1.0
author: Hermes
metadata:
  hermes.tags:
    - Video
    - QC
    - Render
    - Windows
---

# Numpy/PIL/OpenCV Video Render + QC

Create MP4 movies from code-rendered frames using numpy, Pillow, OpenCV, and ffmpeg, with cheap text-layout checks, a single look-test vision inspection, and frame-diff QC. This skill does not cover TTS or social posting.

## When to Use

- "レンダリング前のテキストレイアウトだけ先に確認したい"
- "1枚だけlook-testフレームを作って画像検査したい"
- "フルレンダ後のQCにコンタクトシートとフレーム差分が欲しい"
- "numpy/PIL/cv2/ffmpegでMP4をゼロから作る"

## Prerequisites

- Python `.venv` with `numpy`, `pillow`, `opencv-python-headless`
- `ffmpeg` and `ffprobe` on PATH
- Windows font fallbacks available under `C:\Windows\Fonts\` if CJK text is used

## How to Run

Use the `terminal` tool. On Windows, quote paths with spaces; use absolute paths.

## Quick Reference

| Task | Tool | Notes |
|------|------|-------|
| Font candidate check | `vision_analyze` | Inspect rendered text sample |
| Text layout check | `python render_compare.py` | Must print `LOOKTEST:` |
| Full render | `python render_compare.py` | Must print `MASTER MP4:` |
| Twitter encode | ffmpeg recipe in Procedure | Baseline H.264 + faststart |
| Stream probe | `ffprobe ...` | Verify h264 + aac |
| Contact sheet | `render_compare.py` | Writes `qc/contact_sheet.png` |
| Frame diffs | `render_compare.py` | Writes `qc/*_frame_diff.png` |

## Procedure

### 1. Cheap text layout pre-check

Render one small sample image with the candidate fonts. Avoid full-scene renders until font behavior is confirmed.

```bash
python - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (960, 320), (10, 10, 10))
d = ImageDraw.Draw(img)
for name, size, y in [
  ('NotoSansJP-VF', 28, 40),
  ('meiryo', 28, 100),
  ('msgothic', 28, 160),
]:
  p = Path(rf'C:\Windows\Fonts\{name}.ttf')
  if not p.exists():
    p = Path(rf'C:\Windows\Fonts\{name}.ttc')
  font = ImageFont.truetype(str(p), size) if p.exists() else ImageFont.load_default()
  d.text((40, y), f'{name}: 日本語テスト Hermes 0.19.0 × fork', font=font, fill=(240,240,240))
img.save('%USERPROFILE%/Documents/New project/hermes-agent/output/hermes-compare/qc/font_preview.png')
PY

vision_analyze(image_url='%USERPROFILE%/Documents/New project/hermes-agent/output/hermes-compare/qc/font_preview.png', question='Which rows show full Japanese text without tofu? List exact font names.')
```

### 2. Single look-test scene render

Render one representative scene only. Confirm with `vision_analyze` before committing to a full render.

```bash
python render_compare.py
```

Expected output:
- `LOOKTEST: ...\looktest_scene_<name>.png`

```bash
vision_analyze(image_url='%USERPROFILE%/Documents/New project/hermes-agent/output/hermes-compare/looktest_scene_official.png', question='Is CJK text fully readable without tofu or missing glyphs? Report exact bad rows/glyphs.')
```

Iterate font fallbacks if needed:
- Prefer NotoSansJP-VF, then meiryo/msgothic
- Wrap `ImageFont.truetype()` in `try/except` and fall through candidates

### 3. Full background render

Once the look-test passes, run the full render in the background terminal.

```bash
python render_compare.py
```

Expected output:
- `Rendered NNN frames`
- `MASTER MP4: ...\hermes_0190_vs_fork.mp4`

### 4. Twitter-compatible encode

If the master MP4 is not yet Twitter-ready, re-encode with this recipe.

```bash
ffmpeg -y -i INPUT.mp4 \
  -movflags +faststart \
  -profile:v baseline -level 3.0 -pix_fmt yuv420p \
  -c:v libx264 -b:v 5000k -maxrate 5000k -bufsize 10000k \
  -c:a aac -b:a 256k -ar 44100 -ac 1 \
  OUTPUT.mp4
```

### 5. Verify streams

```bash
ffprobe -v error -show_entries format=format_name:stream=codec_name,codec_type,sample_rate,channels \
  -of default=noprint_wrappers=1 OUTPUT.mp4
```

Expected:
- `format_name=mov,mp4,m4a,3gp,3g2,mj2`
- `codec_name=h264`
- `codec_name=aac`, `sample_rate=44100`, `channels=1`

### 6. Contact sheet + frame-diff QC

Re-run the render script after QC checks are enabled. It writes:
- `qc/contact_sheet.png`
- `qc/intro_frame_diff.png`
- `qc/official_frame_diff.png`
- `qc/fork_frame_diff.png`
- `qc/sidebyside_frame_diff.png`
- `qc/takeaway_frame_diff.png`

## Pitfalls

- `segoeui` and `arial` do not contain Japanese glyphs; they produce tofu even when loaded successfully.
- Some `.ttc` files can throw on `truetype()` for certain sizes; always continue to the next candidate on exception.
- `opencv-python-headless` is sufficient for frame stitching; GUI backends are not required.
- Keep ffmpeg writes atomic with `-y` and separate output filenames when comparing encodes.

## Verification

```bash
cd PROJECT_ROOT/output/hermes-compare && python -m py_compile render_compare.py
ffprobe -v error -show_entries format=format_name:stream=codec_name,codec_type,sample_rate,channels -of default=noprint_wrappers=1 master/hermes_0190_vs_fork.mp4
```

Success:
- `py_compile` exits 0
- `ffprobe` shows `mov,mp4,m4a,3gp,3g2,mj2`, `h264`, `aac`, `44100`, `1`
