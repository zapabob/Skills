---
name: city-destruction-simulation
description: Create a procedural city destruction animation in Blender 5.2 LTS using Python scripting (bpy/bmesh) and compositor nodes for bloom/glare effects.
version: 1.4.0
requires: Blender 5.2.0 LTS
author: agent
platforms: [windows, macos, linux]
tags: [blender, bpy, bmesh, simulation, destruction, explosion, compositor, animation, voicevox, ffmpeg]
---

# Blender City Destruction Simulation

Generate procedural explosion sequences over city grids ranging from small blocks to wide skyline-scale layouts, with layered shock fronts, delayed collapse, crater formation, smoke, and optional narration. Prefer deterministic keyed geometry over expensive full-physics solves when repeatability and resume-safe rendering matter.

## When to Use
- Educational visualizations of explosion effects
- Parameterized destruction sequences for varied yields/distances
- Asset generation via script rather than manual modeling
- Targeting Blender 5.2 LTS (where `scene.node_tree` → `scene.compositing_node_group`)

## Prerequisites
- Blender 5.2.0 LTS accessible via TCP JSON-RPC on port 9876 (use `blender_cmd` helper) **or** run script in Text Editor
- Python 3.11+ with `bpy`/`bmesh` access (when running inside Blender)
- Write permissions for output directory (`./render_frames` relative to blend file)
- A narration backend selected for the project: Irodori TTS (`hakua`) or VOICEVOX when explicitly required
- AKARI Video for deterministic edit/lint/plan/render verification when narration and timing need integration
- `lm-twitterer` environment for publishing; final media must be placed under its approved media directory

## Workflow Overview

1. **Scene Setup** – render settings, output path, enable compositing
2. **Compositor Nodes** – `Render Layers` → `Glare (Bloom)` → `AlphaOver (fade to white)` → implicit composite/output
3. **Geometry** – ground, 5x5 house grid (cube + roof), bomb, fireball, shockwave, mushroom cloud, smoke emitter
4. **Materials** – principled/emission for ground, buildings, fire, shockwave, mushroom, smoke
5. **Animation** – keyframe transforms/materials over 180 frames (24 fps = 7.5s) in five phases:
   - Phase 1 (0-30s): Bomb fall & camera pullback
   - Phase 2 (30-50s): Fireball expansion & emission
   - Phase 3 (50-90s): Shockwave → building collapse (offset/rotation/scale)
   - Phase 4 (90-130s): Mushroom growth & smoke emission
   - Phase 5 (130-180s): Camera retreat + white-out fade
6. **Render** – PNG sequence via `bpy.ops.render.render(animation=True)`
7. **Post-process** – PNGs → MP4 (ffmpeg), concat with implosion, add narration
8. **Publish** – copy the verified artifact to `~/.hermes/lm-twitterer/media/`, dry-run, publish once, then read back the returned status URL

## Production Reliability Pattern

For long city-destruction jobs, separate **scene build → representative probe frames → full render → media assembly**. Do not combine all stages into one Blender socket call.

- Prefer deterministic procedural geometry and keyed collapse over a full rigid-body/fluid solve when repeatability and recovery matter.
- Avoid any huge smoke/volume object that encloses the camera; use bounded clustered smoke forms or compositing instead.
- Probe at least five phases before full rendering: start, ignition, shockwave/collapse, late smoke, final frame.
- Render per frame and skip already-valid PNGs so a timeout or Blender restart can resume rather than restart.
- After completion, verify exact frame count and first/last frame numbers before encoding.
- Blender 5.2 compatibility checks: use the engine identifier exposed by the running build (commonly `BLENDER_EEVEE`), do not assume a world named `World`, use `Principled Volume`, do not use removed `SceneEEVEE.use_gtao`, and do not traverse legacy `Action.fcurves` directly without checking the slot-based Action API.
- If compositor APIs vary, keep the Blender render simple and apply controlled colour curves, glow, and screen blending in ffmpeg after representative-frame review.

For the narration/edit/publish handoff, follow `references/akari-irodori-x-pipeline.md`.

For wide-city shock-front geometry, crater readability, implosion flash matching, and narration-duration handling, follow `references/megascale-wave-crater-timing.md`. In particular, compensate animated curve `bevel_depth` inversely to ring radius and never combine a stretched `setpts` sequence with an output `-frames:v` cap.

## Detailed Steps

### 1. Scene & Render Settings
```python
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 180
scene.render.fps = 24
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.use_compositing = True  # ⚠ NOT scene.use_nodes — that API is removed in 5.2

# CRITICAL: Save .blend first so relative paths resolve correctly
# Blender's CWD is its install dir, not the project dir
bpy.ops.wm.save_mainfile(filepath=project_dir + '/city_destruction.blend')

# Use absolute paths for reliability
frames_dir = "C:/path/to/your/project/render_frames"
import os; os.makedirs(frames_dir, exist_ok=True)
scene.render.filepath = frames_dir + '/frame_'
```

### 2. Compositor Node Tree (Blender 5.2 API)
```python
# Create compositor node group (NOT scene.node_tree — that's removed in 5.2)
cg = bpy.data.node_groups.new('CityDestructionComp', 'CompositorNodeTree')
scene.compositing_node_group = cg

# Nodes
rl = cg.nodes.new('CompositorNodeRLayers')
rl.location = (-600, 0)

glare = cg.nodes.new('CompositorNodeGlare')
glare.location = (-200, 0)
# Blender 5.2: ALL Glare params are set via INPUT SOCKETS, not properties
# Socket names: Strength, Size, Iterations, Highlights Threshold
# ⚠ Do NOT use glare.type, glare.quality, glare.mix, glare.threshold — they don't exist
glare.inputs['Strength'].default_value = 1.5
glare.inputs['Size'].default_value = 0.6
glare.inputs['Iterations'].default_value = 4
glare.inputs['Highlights Threshold'].default_value = 0.8

# White RGB constant (⚠ output socket is 'Color', NOT 'Image')
rgb_node = cg.nodes.new('CompositorNodeRGB')
rgb_node.location = (-200, -300)
rgb_node.outputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)  # RGBA

# AlphaOver for white-out fade (⚠ socket names: Background/Foreground/Fac)
# MixRGB node does NOT exist in Blender 5.2
alpha_over = cg.nodes.new('CompositorNodeAlphaOver')
alpha_over.location = (200, 0)

# ⚠ IMPORTANT: Do NOT use CompositorNodeOutputFile for PNG output
# The file_output_items[i].format only accepts 'OPEN_EXR_MULTILAYER'
# and out.format.file_format = 'PNG' also fails with enum error.
# Instead: remove OutputFile node and let scene render path handle PNG output.
# Blender 5.2 compositor auto-applies the node tree to the render result
# — no terminal node (Composite or OutputFile) is required.

# Links
cg.links.new(rl.outputs['Image'], glare.inputs['Image'])
cg.links.new(glare.outputs['Image'], alpha_over.inputs['Background'])
cg.links.new(rgb_node.outputs['Color'], alpha_over.inputs['Foreground'])
# No terminal link needed — compositor modifies scene render result directly
```

### 3. Geometry
- **Ground**: `bpy.ops.mesh.primitive_plane_add(size=2000, location=(0,0,0))`
- **Houses** (5×5 grid, spacing=40):
  - Cube: `bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2))` → scale `(w/2, d/2, h/2)`
  - Roof: cone via cone`:1=0, =0, 0.4  → mesh → object → (x, y, h + h*0.2)`
- **Bomb**: UV sphere r=0.8 at (0,0,200)
- **Fireball**: UV sphere r=1 at (0,0,-100), start scale 0.01
- **Shockwave**: Circle NGON r=1 at (0,0,2), start scale 0.01
- **Mushroom Cloud**: 8 UV spheres (r=8-15, height 50+15*i), start scale 0.01
- **Smoke Emitter**: plane size=10 at (0,0,30) + particle system

### 4. Materials
```python
def emission_mat(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = (*color, 1.0)
    emit.inputs['Strength'].default_value = strength
    out.location = (300, 0)
    links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def principled_mat(name, base_color, rough=0.7, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return mat
```
- Ground: (0.15,0.12,0.1), rough 0.9
- Building: (0.25,0.22,0.2), rough 0.8
- Roof: (0.15,0.1,0.08), rough 0.9
- Debris: (0.2,0.18,0.15), rough 0.85
- Fireball: emission (1.0,0.4,0.05), strength 50
- Shockwave: emission (1.0,0.6,0.2), strength 20
- Mushroom: (0.15,0.12,0.1), rough 0.7
- MushroomEmit: emission (0.3,0.2,0.1), strength 5
- Smoke: (0.1,0.08,0.06), rough 0.9

### 5. Animation
Use `set_keyframe(obj, prop, frame, value)`: set attr then `keyframe_insert`.

#### Camera Keyframes
| Frame | Location | Rotation |
|-------|----------|----------|----------|
| 1 | (0,-150,80) | (1.1,0,0) |
| 15 | (0,-80,100) | (1.0,0,0) |
| 30 | (0,-200,180) | (0.7,0,0) |
| 40 | (0,-220,200) | (0.6,0,0) |
| 50 | (0,-250,220) | (0.5,0,0) |
| 70 | (0,-300,250) | (0.4,0,0) |
| 90 | (0,-350,280) | (0.3,0,0) |
| 110 | (0,-400,300) | (0.25,0,0) |
| 130 | (0,-420,320) | (0.2,0,0) |
| 150 | (0,-450,340) | (0.15,0,0) |
| 180 | (0,-480,350) | (0.1,0,0) |
Set interpolation to `BEZIER` with `AUTO_CLAMPED`.

#### Bomb Fall
- F1: (0,0,200) → F30: (0,0,2) → F31: (0,0,-10)

#### Fireball
| Frame | Scale | Emission Strength |
|-------|-------|-------------------|
| 30 | 1 | 0 |
| 35 | 30 | 80 |
| 40 | 80 | 120 |
| 45 | 120 | 100 |
| 50 | 150 | 50 |
| 60 | 180 | 10 |
| 70 | 200 | 1 |
Keyframe `scale` and emission node Strength.

#### Shockwave
| Frame | Radius | Strength |
|-------|--------|----------|
| 30 | 1 | 25 |
| 40 | 100 | 30 |
| 50 | 250 | 25 |
| 60 | 400 | 15 |
| 70 | 550 | 5 |
| 80 | 700 | 1 |
| 90 | 850 | 0 |
Keyframe uniform scale (X/Y) and emission Strength.

#### Building Collapse (shockwave-driven)
- Speed: 10 m/frame → `arrival = 30 + int(dist/10)`
- `collapse = arrival + randint(2,8)`
- `end = collapse + randint(10,20)`
  - At `arrival`: keyframe original loc/rot
  - At `collapse`: offset (±size*0.5 XY, -height*0.3 Z) + random rot
  - At `end`: scale (size*0.2, size*0.2, height*0.1)
  Roof: larger offset/rotation, scale (0.3,0.3,0.05)

#### Mushroom Cloud
Sphere `i`: base_z = 50 + i*15
- F50-60: scale 0.01→0.2
- F60-70: →0.5
- F70-80: →0.8
- F80-90: →1.0
- F90-100: →1.2
- F100-110: →1.4
- F110-120: →1.5
- Hold 1.5 to F180
- From F70: Z += (frame-70)*0.5

#### Smoke Particles
- Emit F50-F130, lifetime 80, volume, size 0.5, brownian 2.0, drag 0.1, gravity 0.05
- Keyframe `settings.frame_start` (F50) and `settings.frame_end` (F130)

#### Compositor Animation
- **Glare Strength**: 0.5 (F1-30) → 2.0 (F35) → 3.0 (F45) → 1.5 (F60) → 0.5 (F90) → 0.0 (F130)
- **AlphaOver Factor**: 0.0 (F1-120) → 0.0 (F130) → 0.3 (F140) → 0.6 (F150) → 0.85 (F160) → 1.0 (F180)

### 6. Render

⚠ **`animation=True` timeout risk**: `bpy.ops.render.render(animation=True)` is a single blocking call. On heavy scenes with compositor (180 frames × Eevee), it can take >90s and the JSON-RPC socket may timeout or Blender may crash silently. Use the **per-frame approach** for reliability, especially for first-time renders.

#### Method A (recommended) — Per-frame with health check
```python
import time

for frame_num in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame_num)
    bpy.ops.render.render(write_still=True)
    if frame_num % 30 == 0:
        print(f'✅ Frame {frame_num}/{scene.frame_end}')

print(f'Render complete. Frames saved in {scene.render.filepath}')
```

**Benefits**: survives Blender crashes (last good frame known), supports progress paging, verified per-frame compositor output.

#### Method B (fast, short sequences only) — One-shot animation render
```python
print('Starting render (animation=True — may timeout on long scenes)...')
bpy.ops.render.render(animation=True, write_still=False)
print('Render complete.')
```

Use only for short sequences (≤30 frames) or after Method A confirmed scene stability.

### 7. Post-processing (ffmpeg)

#### PNG → MP4
```bash
ffmpeg -y -framerate 24 -start_number 1 -i render_frames/frame_%04d.png \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p city_destruction_raw.mp4
```

#### Concat with implosion video (both must have audio track)
```bash
# 1. If city_destruction_raw.mp4 has no audio, add silent track:
ffmpeg -y -i city_destruction_raw.mp4 -f lavfi -i anullsrc=r=44100:cl=mono \
  -shortest -c:v copy -c:a aac city_w_audio.mp4

# 2. Create concat list ⚠ Windows requires absolute paths:
#    ❌ echo "file render_frames/clip1.mp4"  (fails on Windows)
#    ✅ echo "file C:/Users/name/project/render_frames/clip1.mp4"
echo "file $(pwd -W 2>/dev/null || pwd)/render_frames/implosion_emc2_narrated_final.mp4" > concat_list.txt
echo "file $(pwd -W 2>/dev/null || pwd)/render_frames/city_w_audio.mp4" >> concat_list.txt

# 3. Concat (copy codec = no re-encode):
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy combined_final.mp4
```

**⚠ Windows concat pitfall**: The concat demuxer on Windows requires **absolute file paths** in the list file (`file C:/path/to/clip.mp4`). Relative paths (`file render_frames/clip.mp4`) silently produce an empty or broken output. Use `$(pwd -W)` (Git Bash) or the full absolute path.

#### VOICEVOX narration (春日部つむぎ speaker 3)
```python
import requests, wave

# VOICEVOX text→WAV via audio_query → synthesis
# Timing reference (実測値):
#   30 chars → 7.1s 例: 「衝撃波で家屋崩壊、キノコ雲発生。核兵器の威力を示す教育映像。」
#   33 chars → 7.2s 例: 「衝撃波到達、家屋崩壊、キノコ雲。教育目的の核爆発シミュレーション。」
#   34 chars → 5.6s (短い読みの場合)
#   196 chars → 39.1s (長文ナレーション)
# Target: ~7s for a 7.5s clip → aim for 30-33 characters

query = requests.post('http://127.0.0.1:50021/audio_query',
    params={'text': text, 'speaker': 3}).json()
audio = requests.post('http://127.0.0.1:50021/synthesis',
    params={'speaker': 3}, json=query).content

with open('narration.wav', 'wb') as f:
    f.write(audio)

with wave.open('narration.wav', 'rb') as w:
    duration = w.getnframes() / float(w.getframerate())
    print(f"Duration: {duration:.1f}s")
```

#### Timed narration overlay (adelay + amix)
Offsets the narration to start at a specific point in the combined video (e.g. 18.4s = end of implosion segment):
```bash
ffmpeg -y -i combined_final.mp4 -i narration.wav \
  -filter_complex "[1:a]adelay=18400|18400[nar];[0:a][nar]amix=inputs=2:duration=first[outa]" \
  -map 0:v -map "[outa]" -c:v copy -c:a aac combined_narrated.mp4
```
- `adelay=18400|18400`: stereo delay in ms (repeat for each channel)
- `amix`: overlay audio; `duration=first` keeps combined video length
- Use `-c:v copy` (no video re-encode) for speed

#### Loop video when narration longer than video
```bash
# Get exact frame count first:
ffprobe -v error -count_frames -select_streams v:0 \
  -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 input.mp4

ffmpeg -y -i input.mp4 -i narration.wav \
  -filter_complex "[0:v]loop=2:size=180,setpts=N/24/TB[v]" \
  -map "[v]" -map "1:a" \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k \
  -shortest -movflags +faststart output_narrated.mp4
```
- `loop=2:size=180`: repeat 2 extra times (3× total); `size` = exact frame count
- `setpts=N/24/TB`: maintain 24fps across all loop iterations
- `-shortest`: stop when audio ends

### Verification: Lightweight Compositor Check by Frame Size

After rendering, confirm the compositor pipeline is active without re-rendering:

```bash
# List frame files sorted by size (largest first)
ls -laS render_frames/*.png | head -5
echo "---"
ls -laS render_frames/*.png | tail -5

# If all frames are the SAME size → compositor NOT applied (OutputFile bypassed the tree)
# If sizes VARY → Glare bloom is working (image content changes affect PNG compression)
# If frames 130-180 are IDENTICAL → white-out fade is fully applied (solid white compresses uniformly)

# Quick stats:
python -c "
import os, glob, statistics
files = sorted(glob.glob('render_frames/*.png'))
sizes = [os.path.getsize(f) for f in files]
print(f'Frames: {len(files)}, sizes: {min(sizes)}-{max(sizes)} bytes')
distinct = len(set(sizes))
print(f'Distinct sizes: {distinct}/{len(files)} (ratio {distinct/len(files):.0%})')
if distinct < len(files) * 0.3:
    print('⚠ SUSPICIOUS: Most frames have identical size - compositor may not be active')
else:
    print('✅ Compositor appears active - frame content varies')
"
```

**Interpreting results:**
- **>70% distinct sizes** → Compositor is working, Glare bloom varies per frame
- **White-out frames identical** (472 KB typical) → Normal, expected (solid white compresses perfectly)
- **All frames identical size** → Compositor bypassed (OutputFile node writing flat result; remove it)

### Blender Process Health Monitoring

During long renders, Blender may crash silently (especially with compositor + heavy geometry):

```python
import socket, time, json

def check_blender_alive(host='127.0.0.1', port=9876):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        s.sendall(b'{"type":"execute_code","params":{"code":"import bpy; print(CHECK_ALIVE)"}}\\n')
        resp = b''
        try:
            while True:
                chunk = s.recv(1024)
                if not chunk: break
                resp += chunk
        except socket.timeout:
            pass
        s.close()
        return 'CHECK_ALIVE' in resp.decode()
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False

# In render loop:
for frame_num in range(1, 181):
    if not check_blender_alive():
        print(f'❌ Blender died at frame {frame_num}!')
        break
    # ... send render command ...
    time.sleep(0.5)  # avoid flooding
```

See `references/blender_crash_recovery.md` for full recovery procedures (restart Blender, re-send scene config, resume from last frame).

### 8. Publishing
```bash
mkdir -p ~/.hermes/lm-twitterer/media
cp city_destruction_narrated.mp4 ~/.hermes/lm-twitterer/media/
lm_twitterer_post(
    text="核爆発のメカニズムを都市規模でシミュレーション。爆風・熱線・放射能の被害範囲を可視化。 #はくあ #Blender3D #核兵器",
    media_paths=["city_destruction_narrated.mp4"],
    dry_run=False  # True for test
)
```
> **Note**: `media_paths` must resolve to files under `~/.hermes/lm-twitterer/media/`. Use an absolute path inside that approved directory, verify the copied file's SHA-256, dry-run first, and publish only once after approval.

## Common Pitfalls & Fixes (Blender 5.2)
| Symptom | Cause | Fix |
**Pitfalls**:
- Giant luminous disc/white plane during shockwave expansion | Curve object scaling also scales `bevel_depth` | Keyframe bevel inversely to radius so world-space tube thickness remains constant; see `references/megascale-wave-crater-timing.md`.
- Crater disappears after ignition | Fireball keeps growing/holding or camera target follows only cloud height | Contract and hide the fireball before crater reveal, keep dust away from center, and keyframe camera target separately.
- Stretched clip is shorter than expected | `-frames:v` caps frames after `setpts`/`fps` filters | Remove the output-frame cap for finite image sequences and verify stream durations with `ffprobe`.
- Narration loses the final word | `-shortest` trims audio to a shorter video | Measure both durations first; preferably regenerate TTS at a moderate provider-side speed and leave a small visual tail.
- `AttributeError: 'Scene' object has no attribute 'node_tree'` | Using removed `scene.node_tree` | Use `scene.compositing_node_group` (create if None)
- Dark/black renders on large terrain + explosion | World/sky too dark + insufficient sun/area light | Boost world strength ≥1.5–2.0, sun energy ≥12–14, add opposing fill AREA light (energy 5k–8k). Always re-render a test range after lighting changes.
- Buildings/houses sink or float on Displace terrain | Objects created at z=0 before/without accounting for displacement | After adding Displace, lift all procedural objects by fixed offset (e.g. +2.5m) or query terrain height at placement time.
- Camera looks wrong / no movement in "fixed tower" shot | Quaternion tweaks too subtle or no explicit look-at | Use Vector look-at to detonation center; add only subtle test-film wobble. Re-aim after terrain changes.
- Fireball stays flat on ground | No location animation | After scale peak, keyframe location Z upward 10–15m for convection rise.
- Narration voice not 春日部つむぎ | fishaudio or default provider used | **Always** confirm VOICEVOX engine running on 50021 before generation. Force speaker=3. Reject non-VOICEVOX fallbacks. User explicitly requires つむぎ for X posts.
- User says "動画見てみて不自然な箇所を訂正して" | Agent skips frame review | **Mandatory step**: after first render, extract 1 fps JPEGs (ffmpeg -vf fps=1), inspect key phases (detonation, peak shockwave, mushroom, white-out). Log specific issues (lighting, scale, placement, timing) then patch script before final render.
| `bpy_struct: item.attr = val: enum "PNG" not found in ('OPEN_EXR_MULTILAYER')` | CompositorNodeOutputFile only supports OPEN_EXR_MULTILAYER | Remove OutputFile node. Set `scene.render.image_settings.file_format = 'PNG'` and render via scene path directly |
| Glare node params not working (not found attribute) | Blender 5.2 exposes Glare params via input sockets, not properties | Set via `glare.inputs['Strength'].default_value`, `glare.inputs['Size'].default_value`, `glare.inputs['Iterations'].default_value`, `glare.inputs['Highlights Threshold'].default_value`. Do NOT use `glare.type` or `glare.quality` — those properties don't exist |
| Output file not saving | Missing `directory`/`file_name` or `use_file_extension=False` | Set `node.directory = <abs_path>`, `node.file_name = "prefix_"`, `node.use_file_extension = True` |
| Keyframes missing | `keyframe_insert` before setting property | Always set attr first: `obj.location = (x,y,z); obj.keyframe_insert("location", frame=f)` |
| Particles not emitting | `frame_start`/`frame_end` not keyframed/set after creation | Create particle system, then immediately keyframe `settings.frame_start`/`frame_end` |
| `bm.to_mesh(mesh)` before `bm.free()` crash | Accessing freed BMesh | Call `bm.to_mesh(mesh)` **then** `bm.free()` |
| Pink/magenta materials | Missing/incorrect material assignment | Verify `obj.data.materials.append(<material>)` for each object |
| Black render | Compositor not outputting combined image | Ensure final node (AlphaOver) connected to output; render uses full tree output |
| FFmpeg "Invalid frame dimensions" | `loop` filter size mismatch with input frame count | Use `ffprobe` to get exact frame count, then `loop=N:size=FRAMECOUNT` |
| **Blender goes silent / process crash mid-render** | Heavy compositor load or timeout kills Blender | See `references/blender_crash_recovery.md` for detection + recovery |
| **ffmpeg concat fails on Windows** | Concat demuxer needs absolute file paths on Windows | Use absolute paths (e.g. `file C:/Users/name/project/clip.mp4`) instead of relative paths in the concat list file |
| **VOICEVOX returns 422 / HTTP error** | Text length or encoding issue | Retry with shorter text (30-33 chars ≈ 7s for 7.5s clip); 196 chars ≈ 39s. See `references/voicevox_duration.md` |

## Extending/Customizing
- Adjust `shockwave_speed` (m/frame) for faster/slower destruction
- Modify fireball color/strength/radius for different yields
- Add ground crater: displace plane with radial falloff driven by shockwave arrival
- Multiple bursts: duplicate bomb/fireball/shockwave chains with time offsets

## Associated Files
- `templates/city_destruction_sim.py` – ready-to-run script (omits narration/ffmpeg)
- `references/compositor_nodes_blender52.md` – node names, sockets, enum values for Blender 5.2
- `references/akari-irodori-x-pipeline.md` – resumable render handoff, Irodori narration, AKARI approval/verification, and one-shot X publishing
- `references/megascale-wave-crater-timing.md` – constant-width shock rings, crater/fireball readability, implosion flash matching, ffmpeg stretch pitfalls, and TTS duration fitting

---

**Author**: Hakua (ヘルメスエージェント)
**Version**: 1.4.0
**Created**: 2025-07-21
**Updated**: 2026-07-30