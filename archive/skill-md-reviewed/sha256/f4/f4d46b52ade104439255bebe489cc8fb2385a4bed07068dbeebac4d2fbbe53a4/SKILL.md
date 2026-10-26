---
name: blender-procedural-modeling
description: Programmatic 3D modeling in Blender using bpy + bmesh — create polyhedra from vertex coordinates, extrude faces along normals, and build complex assemblies (implosion lenses, archimedean solids, custom meshes). Complements blender-mcp (connection/setup) by focusing on pure geometry construction.
version: 1.2.0
requires: Blender 4.3+ with addon server running
tags: [blender, bmesh, procedural, modeling, 3d, bpy, polyhedron]
author: agent
platforms: [windows, macos, linux]
---

# Blender Procedural Modeling via bpy + bmesh

Programmatic 3D modeling techniques using Blender's Python API. Designed for use with BlenderMCP (socket on port 9876) or direct `bpy` execution.

## Connecting

Use the robust helper via `execute_code`:

```python
import socket, json

def blender_cmd(code, host="localhost", port=9876, timeout=120):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        payload = json.dumps({"type": "execute_code", "params": {"code": code}}) + "\n"
        s.sendall(payload.encode("utf-8"))
        resp = b""
        s.settimeout(timeout)
        while True:
            try:
                chunk = s.recv(65536)
                if not chunk: break
                resp += chunk
                s.settimeout(1.0)
            except socket.timeout:
                break
        s.close()
        return json.loads(resp.decode()) if resp else {"status": "error", "message": "Empty"}
    except Exception as e:
        try: s.close()
        except: pass
        return {"status": "error", "message": str(e)}
```

## Key Techniques

### 1. Polyhedron from coordinates (convex hull + dissolve)

Many archimedean solids have known canonical coordinates. Generate vertices, then use `convex_hull` + `dissolve_limit` to build faces:

```python
import bpy, bmesh, math, itertools
from mathutils import Vector

# Generate vertices (example: truncated icosahedron)
phi = (1.0 + math.sqrt(5.0)) / 2.0
def ep(x, y, z):  # even permutations
    return [(x, y, z), (y, z, x), (z, x, y)]

raw = set()
for (xb, yb, zb) in [(0, 1, 3*phi), (1, 2+phi, 2*phi), (phi, 2, 2*phi+1)]:
    for sx, sy, sz in itertools.product([1, -1], repeat=3):
        for (i, j, k) in ep(sx*xb, sy*yb, sz*zb):
            raw.add((round(i, 12), round(j, 12), round(k, 12)))

coords = [Vector(v).normalized() * R for v in raw]

# Convex hull → merge coplanar triangles
tmp = bpy.data.meshes.new("Tmp")
tmp.from_pydata(coords, [], [])
bm = bmesh.new()
bm.from_mesh(tmp)
bmesh.ops.convex_hull(bm, input=bm.verts)
bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(5),
                         verts=bm.verts, edges=bm.edges)
bm.to_mesh(tmp)
bm.free()

obj = bpy.data.objects.new("Polyhedron", tmp)
bpy.context.collection.objects.link(obj)
```

**Result**: 60 vertices → 32 faces (12 pentagons + 20 hexagons for TI).

### 2. Face extrusion lens pattern

After building a polyhedron, create wedge segments by extruding each face along its normal:

```python
for f in bm.faces:
    normal = f.normal.normalized()
    verts_3d = [obj.data.vertices[v.index].co for v in f.verts]
    outer = [c + normal * height for c in verts_3d]

    lbm = bmesh.new()
    inner_v = [lbm.verts.new(c) for c in verts_3d]
    outer_v = [lbm.verts.new(c) for c in outer]

    lbm.faces.new(inner_v)                 # bottom cap
    lbm.faces.new(list(reversed(outer_v))) # top cap (reversed for correct normal)
    for i in range(len(inner_v)):          # side quads
        j = (i + 1) % len(inner_v)
        lbm.faces.new([inner_v[i], inner_v[j], outer_v[j], outer_v[i]])

    mesh = bpy.data.meshes.new(f"Lens_{fi}")
    lbm.to_mesh(mesh)
    lbm.free()
```

### 3. Implosion lens material assignment

- **Pentagons** (12 faces) → fast explosive: red/orange with emission
- **Hexagons** (20 faces) → slow explosive: yellow with emission

### 4. Scene setup for rendering

```python
# Camera
bpy.ops.object.camera_add(location=(7.5, -6.0, 5.0))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = cam

# Lighting (Area lights, energy in 500–2000 range for Cycles)
bpy.ops.object.light_add(type='AREA', location=(5, -5, 8))
key = bpy.context.active_object; key.data.energy = 2000; key.data.size = 3

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.cycles.samples = 128
scene.cycles.use_denoising = True
bpy.ops.render.render(write_still=True)
```

### 5. Animation & Keyframing (Blender 5.2+)

Animation is keyframed object-by-object across time. The pattern: set frame → modify object state → insert keyframe → advance frame.

#### 5.1 Implosion lens animation (convergence)

For multi-lens implosion, each lens needs to converge toward center simultaneously, with different timing per material group:

```python
import math, random
from mathutils import Vector

center = Vector((0.0, 0.0, 0.0))
scene = bpy.context.scene

# Group lenses by material (pentagon=fast, hexagon=slow)
fast_lenses = [o for o in bpy.data.objects if o.name.startswith('Lens_') and 'red' in (o.active_material.name if o.active_material else '')]
slow_lenses = [o for o in bpy.data.objects if o.name.startswith('Lens_') and 'yellow' not in (o.active_material.name if o.active_material else '')]

for lens in fast_lenses:
    start_pos = lens.location.copy()
    dir_vec = (center - start_pos).normalized()
    dist = start_pos.length

    for frame, t in [(1, 0.0), (5, 0.0), (20, 1.0)]:  # hold 5 frames then converge
        loc = start_pos + dir_vec * dist * t if t > 0 else start_pos
        lens.location = loc
        lens.keyframe_insert(data_path="location", index=-1, frame=frame)
```

**Timing strategy for multi-phase animation:**

| Phase | Frames | What happens |
|-------|--------|-------------|
| A. Implosion convergence | 1–30 | Lenses move toward center (fast group starts at frame 5, slow at frame 15) |
| B. Core compression + fission | 30–50 | Pu core scales 1→2.5, emission ramps from red→white |
| C. Detonation flash | 50–65 | Energy wave sphere 3→10 radius; all lenses scatter outward; full flash via plane with 100% emission |
| D. E=mc² text reveal | 65–100 | Text appears at center, energy wave fades, debris expands |
| E. Afterglow | 100–150 | Gradual fade, text remains centered |

#### 5.2 Core material animation

Animate Pu core emission color/strength over time to show temperature rise:

```python
core = bpy.data.objects.get("Pu_Core")
mat = core.active_material
mat.use_nodes = True
nodes = mat.node_tree.nodes
emission = next(n for n in nodes if n.type == 'EMISSION')

# Animate emission color
emission.inputs['Color'].keyframe_insert(data_path="default_value", frame=1)    # dark red
emission.inputs['Color'].default_value = (1.0, 0.9, 0.5, 1.0)  # white-hot
emission.inputs['Color'].keyframe_insert(data_path="default_value", frame=55)
```

#### 5.3 Explosion / City Destruction animation

For wide-shot city destruction animation (explosion, shockwave, mushroom cloud, white-out fade), see `references/city-destruction-simulation.md`. Key differences from lens implosion:

- **bmesh grid generation**: 5×5 wooden houses with triangular roofs
- **Shockwave**: Expanding UV sphere with scale keyframes (1→50×)
- **Fireball**: Emission material with color animation (red→white→fade)
- **White-out**: Compositor AlphaOver node Fac animated 0→1 (`MixRGB` はBlender 5.2で存在しない)
- **Camera pullback**: Multi-phase camera animation from close-up to wide to white-out
- **Blender 5.2 LTS specifics**:
  - Use `scene.compositing_node_group` (not `scene.node_tree` which was removed)
  - Glare node parameters set via input sockets: Strength, Size, Iterations, Highlights Threshold
  - Engine string: `'BLENDER_EEVEE'` (not `'BLENDER_EEVEE_NEXT'`)
  - PNG output via `scene.render.image_settings.file_format = 'PNG'` (not CompositorNodeOutputFile)

#### 5.6 Air-burst at 100m + Observation Tower + Tokyo-style Terrain (Test-site Footage Style)

**Use case**: Fixed-camera nuclear test footage style (not ground burst). Detonation at fixed altitude 100m from experimental tower.

**Key elements**:
- Detonation center at z=100 (e.g. (5, 5, 100))
- Bomb descends only to z=100
- Fireball / shockwave / mushroom all centered at z=100
- Observation tower (cylinder mast + cross braces) offset from ground zero
- Fixed camera at tower top with subtle motion
- Terrain via Displace + synthetic 16-bit heightmap (Tokyo: west high, east low, rivers)
- Mixed buildings (low wooden bmesh + taller concrete)

Full code (heightmap generator, tower, 100m centering, mixed buildings, timing) in `references/air-burst-tower-terrain.md`.

**Synthetic heightmap fallback** (no heavy GIS deps):
512×512 16-bit PNG with sigmoid + noise + valleys, loaded as Displace texture.

**Must pack the image** (see references/headless-heightmap-packing-and-fixed-blend-debug.md):
```python
height_img = bpy.data.images.load(HEIGHTMAP_PATH)
height_img.filepath = HEIGHTMAP_PATH
height_img.filepath_raw = HEIGHTMAP_PATH
height_img.pack()
height_img.use_fake_user = True
disp.strength = 18.0  # or 20.0 for visible Tokyo relief
```

**Narration**: Prioritize VOICEVOX speaker=3 (春日部つむぎ). Short Japanese text for 7.5s clips.

**Pipeline**:
1. Scene build (tower + z=100 air-burst + heightmap + mixed bldgs) → .blend
2. Render 180 frames
3. ffmpeg to MP4
4. VOICEVOX narration
5. Mux -shortest
6. Copy to ~/.hermes/lm-twitterer/media/
7. lm-twitterer post ("教育目的")

**Pitfalls**:
- Must center explosion elements at z=100
- Later destruction timing for air-burst
- Save .blend for path resolution
- Verify durations with ffprobe
- Headless re-render from _fixed.blend (after post-process lighting/placement/camera fixes) can produce very small files if emissives do not activate fully in background. Always extract preview frames (`ffmpeg -vf fps=1`) and inspect. GUI + limited frame range test recommended before full social output.
- VOICEVOX speaker ID for 春日部つむぎ is **8** (ノーマル). Confirm via /speakers on any new VOICEVOX version.
- Use direct Python requests for audio_query + synthesis when no jq/wrapper available.

See `references/air-burst-tower-terrain.md`, `references/iterative-fixed-render-voicevox.md`, and `references/headless-heightmap-packing-and-fixed-blend-debug.md`.

**Critical new pitfall (this session)**: Heightmap images must be `.pack()`ed (and absolute filepath set) before saving the .blend. Without it, Displace fails silently in `--background` renders → "gray only" flat terrain. Post-process `_fixed.blend` files can corrupt the scene (only Cube remains); re-run the clean build script as source of truth when visuals are broken. Always extract preview frames and verify packed image + object presence before mux/post. VOICEVOX speaker for 春日部つむぎ is 8 in this environment. User often disables MCP addon.

**Iterative Workflow (this session pattern)**: Build → render → extract previews → write fix_*.py (lights boost, object lift for terrain, camera aim, fireball rise) → run on .blend to produce _fixed → re-render from _fixed.blend (user direct command: "fixed.blend を開いて再レンダ") → mux with VOICEVOX speaker 8 narration.

**User command style for this task**: Short status ("レンダ完了", "つむぎ起動した", "fixed.blend を開いて再レンダ"). Respond with minimal status + next concrete action in concise Japanese.

#### 5.4 Energy wave sphere

Add a UV sphere, animate its scale for shockwave expansion:

```python
bpy.ops.mesh.primitive_uv_sphere_add(radius=3.0, location=(0,0,0))
wave = bpy.context.active_object
wave.name = "Energy_Wave"
wave.scale = (1.0, 1.0, 1.0)
wave.keyframe_insert(data_path="scale", frame=50)
wave.scale = (3.33, 3.33, 3.33)
wave.keyframe_insert(data_path="scale", frame=70)
```

#### 5.5 Text overlay (E=mc²)

```python
bpy.ops.object.text_add(location=(0, 0, 3.0))
txt = bpy.context.active_object
txt.name = "EMC2_Text"
txt.data.body = "E = mc²"
txt.data.size = 2.0
txt.data.align_x = 'CENTER'

# Animate opacity via material alpha
mat = bpy.data.materials.new("Text_Mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Alpha'].default_value = 0.0
bsdf.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=70)
bsdf.inputs['Alpha'].default_value = 1.0
bsdf.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=80)
```

### 6. Frame-by-Frame Render → Video Pipeline

For animation rendering, prefer Eevee (fast) over Cycles (slow per-frame):

```python
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 15

# Eevee (fast for animation — Blender 5.2 LTS uses 'BLENDER_EEVEE', NOT 'BLENDER_EEVEE_NEXT')
scene.render.engine = 'BLENDER_EEVEE'

# Or Cycles (quality, ~8× slower per frame)
# scene.cycles.samples = 128
# scene.cycles.use_denoising = True

import os
outdir = "C:/path/to/render_frames"
os.makedirs(outdir, exist_ok=True)

for frame in range(1, 151):
    scene.frame_set(frame)
    scene.render.filepath = f"{outdir}/frame_{frame:04d}.png"
    bpy.ops.render.render(write_still=True)
```

#### ffmpeg assembly to MP4

```bash
ffmpeg -y -framerate 24 -start_number 1 \
  -i "render_frames/frame_%04d.png" \
  -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p implosion_emc2.mp4
```

Performance reference (Blender 5.2, Eevee, 1920×1080):\n- **Eevee**: ~0.9s/frame → 150 frames in ~2 min → 1.8MB MP4 at CRF 18
- **Cycles 128spp**: ~70s/frame → only for single-frame hero shots

### 6.2 Narrated Output Pipeline (render → TTS → social posting)

After assembling the raw MP4, add Hakua-voice narration and prepare for X/Twitter posting via lm-twitterer.

#### 6.2.1 Generate narration (VOICEVOX)

When irodori TTS server is unavailable, use the running VOICEVOX engine:

```python
# Generate Hakua-style narration via VOICEVOX (speaker 3 = 春日部つむぎ — user preference)
result = aituber_onair_speak(
    text="Your Japanese narration text here.",
    provider="voicevox",
    voicevox_speaker=3,  # 春日部つむぎ（speaker 3）
    format="wav",
    output_path="C:/path/to/narration.wav"
)
# file_path and size_bytes are returned; "WS loopback push failed" error is harmless
```

#### 6.2.2 Loop video + mux narration (when video < audio)

When the rendered animation is shorter than the narration audio, loop the video to match:

```bash
# Measure both durations first
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 animation.mp4
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 narration.wav

# Loop video 2× extra (3 total) to cover narration length, mux audio
# loop=N: repeat N additional times (total = N+1)
# size=N: number of frames in the input (must match exactly)
ffmpeg -y -i animation.mp4 -i narration.wav \\
  -filter_complex "[0:v]loop=2:size=150,setpts=N/24/TB[v]" \\
  -map "[v]" -map "1:a" \\
  -c:v libx264 -preset fast -crf 23 \\
  -c:a aac -b:a 192k \\
  -shortest -movflags +faststart output_narrated.mp4
```

**Key parameters explained:**
- `loop=2:size=150` — repeat the input 2 extra times (3× total). `size` = total frame count of the input; must match exactly.
- `setpts=N/24/TB` — ensure playback speed stays at 24 fps across all loop iterations.
- `-shortest` — stop encoding when the shorter stream ends (typically audio).
- Always verify with `ffprobe` after encoding (duration, audio stream, codec).

**Simple mux** (when video is already long enough):
```bash
ffmpeg -y -i animation.mp4 -i narration.wav \\
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart output_narrated.mp4
```

**Key parameters explained:**
- `loop=2:size=150` — repeat the input 2 extra times (3× total). `size` = total frame count of the input; must match exactly.
- `setpts=N/24/TB` — ensure playback speed stays at 24 fps across all loop iterations.
- `-shortest` — stop encoding when the shorter stream ends (typically audio).
- Always verify with `ffprobe` after encoding (duration, audio stream, codec).

**Simple mux** (when video is already long enough):
```bash
ffmpeg -y -i animation.mp4 -i narration.wav \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart output_narrated.mp4
```

#### 6.2.3 Prepare for X/Twitter posting

lm-twitterer requires media files under its dedicated directory:

```bash
mkdir -p ~/.hermes/lm-twitterer/media
cp output_narrated.mp4 ~/.hermes/lm-twitterer/media/
```

Post via `lm_twitterer_post` with the relative filename only:
```
lm_twitterer_post(
    text="Animation narration with Hakua voice #blender3d #はくあ",
    media_paths=["output_narrated.mp4"],
    dry_run=True   # set False to publish
)
```

**Known pitfall**: `media_paths` must reference files under `~/.hermes/lm-twitterer/media/` by relative filename. Absolute paths or files in other directories are rejected with error code 3.

#### 6.2.4 Complete pipeline example

```python
# 1. Render frames (Blender via blender_cmd)
for frame in range(1, 151):
    scene.frame_set(frame)
    scene.render.filepath = f"{outdir}/frame_{frame:04d}.png"
    bpy.ops.render.render(write_still=True)

# 2. Assemble MP4 (terminal: ffmpeg)
subprocess.run(["ffmpeg", "-y", "-framerate", "24", "-start_number", "1",
    "-i", f"{outdir}/frame_%04d.png",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p", "animation.mp4"])

# 3. Generate narration (aituber_onair_speak with voicevox, speaker 3=春日部つむぎ)
narration = aituber_onair_speak(text="...", provider="voicevox", voicevox_speaker=3, ...)

# 4. Mux with loop if needed (terminal: ffmpeg)
subprocess.run(["ffmpeg", "-y", "-i", "animation.mp4", "-i", narration.file_path,
    "-filter_complex", "[0:v]loop=2:size=150,setpts=N/24/TB[v]",
    "-map", "[v]", "-map", "1:a",
    "-c:v", "libx264", "-c:a", "aac", "-shortest", "output_narrated.mp4"])

# 5. Copy to media dir
shutil.copy("output_narrated.mp4", os.path.expanduser("~/.hermes/lm-twitterer/media/"))

# 6. Post (lm_twitterer_post)
lm_twitterer_post(text="...", media_paths=["output_narrated.mp4"], dry_run=False)
```

## Reference Files

- `references/blender-5x-pitfalls.md` — Blender 5.x API quirks, compositor access (scene.compositing_node_group), Glare node input sockets, Principled BSDF input changes, keyframing patterns, particle system removals, render resume, MCP bridge behavior, ffmpeg color grading fallback
- `references/implosion-lens.md` — Truncated icosahedron lens geometry, face grouping, material assignments
- `references/city-destruction-simulation.md` — Procedural city destruction animation pipeline
- `references/air-burst-tower-terrain.md` — Air-burst at 100m with observation tower, synthetic heightmap, Tokyo-style terrain
- `references/iterative-fixed-render-voicevox.md` — Post-render fix cycle, VOICEVOX narration (speaker 8 = 春日部つむぎ), mux pipeline
- `references/headless-heightmap-packing-and-fixed-blend-debug.md` — Image packing requirement for Displace, _fixed.blend corruption, headless rendering pitfalls

## Common polyhedron coordinate sets

| Solid | Vertices | Canonical base coordinates |
|-------|----------|---------------------------|
| Truncated icosahedron | 60 | (0, ±1, ±3φ), (±1, ±(2+φ), ±2φ), (±φ, ±2, ±(2φ+1)) |
| Icosahedron | 12 | (0, ±1, ±φ), (±1, ±φ, 0), (±φ, 0, ±1) |
| Dodecahedron | 20 | (±1, ±1, ±1), (0, ±1/φ, ±φ), (±1/φ, ±φ, 0), (±φ, 0, ±1/φ) |

where φ = (1+√5)/2. Even permutations of all sign combinations.

## Pitfalls

- **CRITICAL** — `bm.to_mesh(mesh)` before `bm.free()`. Accessing a freed BMesh throws "BMesh data of type BMesh has been removed".
- `convex_hull` outputs **triangulated** faces — always use `dissolve_limit` after to merge coplanar tris into proper polygons.
- `dissolve_limit` angle is in **radians** (5° ≈ 0.087 rad).
- Face normals from hull faces point outward correctly. For inner/outer caps, reverse vertex order for the outer face.
- Cycles at 1920×1080 / 128 samples takes ~70s for medium scenes. Eevee: ~0.9s/frame.
- Area lights need sufficient energy (2000 for key light in Cycles).
- Always clear scene first: `bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()`
- Then clean up materials: `for m in bpy.data.materials: bpy.data.materials.remove(m)`
- **Blender 5.2 Eevee engine string**: use `'BLENDER_EEVEE'` (NOT `'BLENDER_EEVEE_NEXT'`). The NEXT suffix is for Blender 5.3+ only; 5.2.0 LTS uses `'BLENDER_EEVEE'`.
- **Bloom/Glare in Blender 5.2**: `scene.eevee.use_bloom` does NOT exist. Must set up Compositor nodes via `scene.compositing_node_group` (NOT `scene.node_tree` — that API is removed in Blender 5.2):

  ```python
  scene.use_nodes = True
  cg = scene.compositing_node_group
  if not cg:
      cg = bpy.data.node_groups.new('CompositingNodes', 'CompositorNodeTree')
      scene.compositing_node_group = cg

  rl = cg.nodes.new('CompositorNodeRLayers')
  glare = cg.nodes.new('CompositorNodeGlare')
  # Blender 5.2: Glare params are set via INPUT SOCKETS, not properties:
  glare.inputs['Strength'].default_value = 3.0
  glare.inputs['Size'].default_value = 10.0
  glare.inputs['Iterations'].default_value = 6
  glare.inputs['Highlights Threshold'].default_value = 0.2
  # ⚠ Do NOT use glare.type / glare.quality / glare.mix — they don't exist in 5.2

  # White-out: use AlphaOver (MixRGB doesn't exist in Blender 5.2)
  rgb = cg.nodes.new('CompositorNodeRGB')
  rgb.outputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
  alpha = cg.nodes.new('CompositorNodeAlphaOver')
  # Socket names in 5.2: Background/Foreground/Fac
  cg.links.new(rl.outputs['Image'], alpha.inputs['Background'])
  cg.links.new(rgb.outputs['Color'], alpha.inputs['Foreground'])

  # No terminal node needed — compositor auto-applies in Blender 5.2
  ```

- **PNG output from OutputFile**: `CompositorNodeOutputFile.file_output_items[i].format` only accepts `OPEN_EXR_MULTILAYER`. Set PNG via `scene.render.image_settings.file_format = 'PNG'` instead, and remove the OutputFile node from the compositor tree.

- **Absolute paths for render**: Blender's CWD is its install directory. Always use absolute paths, or save the `.blend` file in the project directory first to make relative paths resolve correctly.
- **Animation clearance**: before keyframing lens positions, ensure each object is at its correct rest position. Changing `location` then inserting keyframe works; changing `matrix_world` directly may not.
- **ffmpeg start_number**: `-start_number` must match the frame numbering in the file pattern. If frames are `frame_0001.png` to `frame_0150.png`, use `-start_number 1`.

## Live Blender 5.2 verification and connection fallback

- For a live Blender session, verify the artifact at the end rather than trusting the build response: query `bpy.app.version_string`, count the generated objects, confirm `scene.camera`, and confirm the absolute render filepath. Also check that the `.blend` and rendered image exist on disk.
- Blender 5.2 in this environment exposes `BLENDER_EEVEE` (not `BLENDER_EEVEE_NEXT`), has no `scene.node_tree`, and may not expose `CompositorNodeComposite`. Use `scene.compositing_node_group`; probe compositor socket names/types before assigning values. Do not assume the newer compositor API from memory.
- Keep live builds in small logical phases when using the catalog MCP tools: scene clear/base mesh, segment generation, materials/lighting, then save/render/verify. This makes bridge timeouts and version-specific API errors easy to isolate.
- If the catalog Blender MCP tools are not present but the user explicitly confirms a connected local bridge and port 9876 is reachable, use a short-lived terminal-side TCP client as a compatibility fallback. Keep the client in an OS temp path with a `hermes-verify-` or `hermes-build-` prefix, remove it after use, and report the actual response; do not fabricate scene state.
- When adding compositor glow, verify the node graph is actually linked and the rendered pixels show the intended effect. A successful node creation without valid links is not a successful glow setup.
