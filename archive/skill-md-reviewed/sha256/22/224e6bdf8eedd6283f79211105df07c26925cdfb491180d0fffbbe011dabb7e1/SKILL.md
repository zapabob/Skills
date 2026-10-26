---
name: blender-nuclear-simulation-video
description: Create educational nuclear airburst simulation videos with Blender, GPU rendering, VOICEVOX narration, and ffmpeg assembly.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Blender, VOICEVOX, ffmpeg, Simulation, Video]
---

# Blender Nuclear Simulation Video

Create educational nuclear airburst simulation videos using Blender 5.2+ (Eevee/Cycles GPU), synthetic Tokyo terrain heightmaps, crater/ground shockwave effects, VOICEVOX narration, and ffmpeg post-processing. Outputs MP4 ready for X/Twitter via `lm-twitterer`.

## When to Use

- Produce educational nuclear detonation simulations with terrain, crater, and shockwave visualization
- Need GPU-accelerated Blender rendering (Eevee or Cycles) with consistent settings
- Want automated VOICEVOX narration (春日部つむぎ speaker 8) + ffmpeg assembly
- Target platform is X/Twitter via Hermes `lm-twitterer` plugin

## Prerequisites

- **Blender 5.2 LTS** installed (default path `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe` or Steam)
- **VOICEVOX Engine** running at `http://127.0.0.1:50021` (speaker 8 = 春日部つむぎ)
- **ffmpeg** in PATH
- **Python 3.10** for Blender socket communication (`%USERPROFILE%/AppData/Local/Programs/Python/Python310/python.exe`)
- **MCP Blender addon** on port 9876 (optional; can also use `--background --python`)
- **Hermes `lm-twitterer` plugin** configured for X posting
- Tokyo heightmap: `render_frames/tokyo_heightmap.png` (512x512 16-bit PNG, packed)

## How to Run

1. Prepare Blender scene with terrain, crater, shockwave via MCP9876 or background script
2. Render 180 frames (24fps = 7.5s) to PNG sequence via Eevee GPU
3. `ffmpeg` PNG → MP4 (H.264/CRF18/yuv420p)
4. Generate narration via VOICEVOX `speaker=8`
5. `ffmpeg` combine video + audio → final MP4
6. Copy to `~/.hermes/lm-twitterer/media/` and post via `hermes lm-twitterer post`

## Quick Reference

| Step | Command / Action |
|------|------------------|
| Send scene setup to Blender | `python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1',9876)); s.sendall(code.encode())"` |
| Background render | `blender --background scene.blend --python-expr "import bpy; bpy.ops.render.render(animation=True,write_still=True)"` |
| PNG → MP4 | `ffmpeg -framerate 24 -i frame_%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4` |
| VOICEVOX TTS | `curl -s -X POST "http://127.0.0.1:50021/audio_query?speaker=8" -d "text=..." \| curl -s -X POST "http://127.0.0.1:50021/synthesis?speaker=8" -H "Content-Type: application/json" -d @- -o narration.wav` |
| Combine audio+video | `ffmpeg -i video.mp4 -i narration.wav -c:v copy -c:a aac -shortest final.mp4` |
| Post to X | `hermes lm-twitterer post --text "..." --media "final.mp4" --live` |

## Procedure

### 1. Generate Tokyo heightmap (once)
```bash
python render_frames/gen_tokyo_heightmap.py
# Creates tokyo_heightmap.png (512x512 16-bit, west=Musashino terrace 20-40m, east=lowland 0-5m)
```

### 2. Build Blender scene via MCP9876
Send Python code to `127.0.0.1:9876` that:
- Creates `TokyoTerrain` plane + Displace modifier (heightmap, strength=35, subdiv=200, texture_coords=OBJECT)
- Adds `Crater` cone at ground zero (frame 48+ visible, dark burned material)
- Adds `GroundShockwave` torus ring (frame 42-92 expand, emissive material, fade)
- Sets Eevee: 64 samples, soft shadows, AO, bloom
- Sets output to `render_frames/tokyo_airburst_crater/frame_`
- Frame range 1-180

### 3. Verify in Blender GUI
- Switch 3D Viewport to **Rendered** mode (top-right sphere icon)
- Confirm crater depression and expanding shock ring visible
- Adjust object positions/keyframes if needed

### 4. Render animation (GPU)
**Option A: GUI** → `Render → Render Animation` (Eevee auto GPU)
**Option B: CLI**:
```bash
blender --background tokyo_airburst_destruction.blend \
  --python-expr "import bpy; bpy.ops.render.render(animation=True, write_still=True)"
```
**Option C: Cycles GPU** (if higher quality needed):
```bash
blender --background -- --cycles-device OPTIX ...
```

### 5. Verify frames
```bash
ls render_frames/tokyo_airburst_crater/frame_*.png | wc -l
# Should output 180
```

### 6. PNG → MP4
```bash
ffmpeg -y -framerate 24 -i render_frames/tokyo_airburst_crater/frame_%04d.png \
  -c:v libx264 -crf 18 -pix_fmt yuv420p \
  render_frames/tokyo_airburst_crater.mp4
```

### 7. Generate VOICEVOX narration
```bash
# audio_query
curl -s -X POST "http://127.0.0.1:50021/audio_query?speaker=8" \
  -d "text=これは教育目的のシミュレーションです。実験棟のタワーから高度100メートルで原子爆弾が空中炸裂しました。強烈な火球が発生し、衝撃波と熱風が広がります。東京の地形を再現した都市で、建物が次々と破壊され、キノコ雲が立ち上る様子をご覧ください。" \
  -o /tmp/query.json

# synthesis
curl -s -X POST "http://127.0.0.1:50021/synthesis?speaker=8" \
  -H "Content-Type: application/json" \
  -d @/tmp/query.json \
  -o render_frames/tokyo_narration_tsumugi.wav
```

### 8. Combine video + audio
```bash
ffmpeg -y -i render_frames/tokyo_airburst_crater.mp4 \
  -i render_frames/tokyo_narration_tsumugi.wav \
  -c:v copy -c:a aac -shortest \
  render_frames/tokyo_airburst_tsumugi_final.mp4
```

### 9. Deploy to lm-twitterer
```bash
cp render_frames/tokyo_airburst_tsumugi_final.mp4 ~/.hermes/lm-twitterer/media/
hermes lm-twitterer post --text "東京の地形を再現した都市で、高度100m空中炸裂をシミュレーション。実験棟タワーからの定点カメラ視点です。春日部つむぎナレーション付き。教育目的 #hermesagent はくあ" --media "tokyo_airburst_tsumugi_final.mp4" --live
```

## Pitfalls

- **Heightmap not packed**: Blender loses external image on reload → always `height_img.pack()` after load
- **Displace strength too low**: Terrain looks flat gray → use strength 30-35, subdiv 200
- **Camera object has no materials**: Skip non-MESH objects in material loops (`if obj.type != 'MESH': continue`)
- **VOICEVOX not running**: Port 50021 must respond; fallback to `text_to_speech` tool if needed
- **C: drive full**: Clean temp/cache before large renders (180 frames × 4K+ PNGs = several GB)
- **MCP9876 not listening**: Start Blender, enable MCP addon, verify `netstat -ano | findstr 9876`
- **Eevee bloom missing in 5.2**: Use Compositor Glare node instead of `scene.eevee.use_bloom`

## Verification

```bash
# 1. Frames exist
test $(ls render_frames/tokyo_airburst_crater/frame_*.png 2>/dev/null | wc -l) -eq 180 && echo "Frames OK"

# 2. MP4 created and playable
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 render_frames/tokyo_airburst_tsumugi_final.mp4
# Should show: 1920,1080,7.5 (or similar)

# 3. Audio track present
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,duration -of csv=p=0 render_frames/tokyo_airburst_tsumugi_final.mp4
# Should show: aac,7.5

# 4. File in lm-twitterer media
test -f ~/.hermes/lm-twitterer/media/tokyo_airburst_tsumugi_final.mp4 && echo "Deployed OK"
```