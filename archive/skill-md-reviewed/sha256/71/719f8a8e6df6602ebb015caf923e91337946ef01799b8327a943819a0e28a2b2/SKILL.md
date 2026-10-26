---
name: blender-render-pipeline
description: Configure and drive Blender Eevee rendering and Compositor pipelines via remote TCP socket — scene setup, compositor node graph, output configuration, and batch rendering. Covers Blender 5.x API quirks (scene.compositing_node_group, socket-based Glare control, AlphaOver socket mapping).
version: 1.0.0
author: Hermes Agent
tags: [blender, eevee, compositor, rendering, bpy, 3d]
related_skills: [blender-mcp, blender-cad]
---

# Blender Render Pipeline

Configure Blender's Eevee render engine and Compositor node graph entirely via remote TCP socket (JSON-RPC code injection). Covers the full pipeline: scene rendering → compositor effects → file output.

## When to use

- Setting up Eevee render settings for a scene
- Building a Compositor node graph with Glare bloom, white-out fade, color correction
- Configuring render output (file format, path, animation frames)
- Batch-rendering frame sequences remotely
- Working with Blender 5.x where legacy API (`scene.node_tree`, `MixRGB`, `CompositorNodeComposite`) has been removed

## Prerequisites

- **Blender 5.x LTS** (Eevee engine tested; Cycles may differ)
- **Blender running with `--python-use-system-env`** for JSON-RPC server (or use blender-mcp addon as alternative)
- **TCP port 9876 open** on localhost
- **ffmpeg** for post-processing rendered frames into video

## Connection Methods

### Method A: Direct TCP exec() (JSON-RPC)

Preferred for full control. Send Python code strings via raw TCP socket:

```python
import socket, json

def blender_exec(code: str, host="127.0.0.1", port=9876, timeout=30):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.settimeout(timeout)
    payload = json.dumps({"type": "exec", "code": code})
    s.sendall(payload.encode("utf-8"))
    buf = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk: break
            buf += chunk
        except socket.timeout: break
    s.close()
    return buf.decode("utf-8")
```

**Key difference from blender-mcp:** This uses `{"type": "exec", "code": "..."}` not the MCP addon's `{"type": "execute_code", "params": {"code": ...}}` format.

### Method B: blender-mcp addon

Use the existing `zapabob-skills/blender-mcp` skill for the MCP addon protocol. The compositor knowledge in this skill applies regardless of connection method.

## Eevee Render Settings

```python
import bpy
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 180
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
```

## Compositor Pipeline (Blender 5.x API)

**CRITICAL:** Blender 5.x removed several legacy APIs. The compositor node tree is accessed via `scene.compositing_node_group` (NOT `scene.node_tree`).

### Setup

```python
# Enable compositor
scene.use_nodes = True
tree = scene.compositing_node_group  # Blender 5.x API

# Clear existing nodes
tree.nodes.clear()
# Re-create the Render Layers node (auto-deleted when nodes are cleared)
rl = tree.nodes.new(type='CompositorNodeRLayers')
```

### Node Reference (Blender 5.2 specific)

| Node               | Blender 5.2 Notes |
|--------------------|-------------------|
| `CompositorNodeComposite` | **DOES NOT EXIST** in Blender 5.2. Use `CompositorNodeOutputFile` instead |
| `CompositorNodeGlare` | All parameters (quality, iteration, mix, threshold etc.) are **input sockets**, NOT direct properties. Connect value nodes to control them. Glare type enum is still a direct property |
| `CompositorNodeAlphaOver` | Socket names are `Background` / `Foreground` / `Fac` (input) and `Color` (output) — NOT the old `Fac`/`Image`/`Image` layout |
| `CompositorNodeMixRGB` | **DOES NOT EXIST** in Blender 5.2. Use `AlphaOver` for additive/alpha blending, or `CompositorNodeMix` for other blend modes |
| `CompositorNodeOutputFile` | Input socket is named **`__extend__`** (dynamic). PNG format set via `file_output_items[0].format.file_format` on the sub-object, not directly on the node |

### Glare Bloom Example

```python
glare = tree.nodes.new(type='CompositorNodeGlare')
glare.glare_type = 'BLOOM'

# Create value nodes for socket-based params
qnode = tree.nodes.new(type='CompositorNodeValue')
qnode.outputs[0].default_value = 3  # quality
tree.links.new(qnode.outputs[0], glare.inputs['Quality'])

inode = tree.nodes.new(type='CompositorNodeValue')
inode.outputs[0].default_value = 4  # iterations
tree.links.new(inode.outputs[0], glare.inputs['Iterations'])

mnode = tree.nodes.new(type='CompositorNodeValue')
mnode.outputs[0].default_value = 1.0  # mix
tree.links.new(mnode.outputs[0], glare.inputs['Mix'])

tnode = tree.nodes.new(type='CompositorNodeValue')
tnode.outputs[0].default_value = 0.0  # threshold
tree.links.new(tnode.outputs[0], glare.inputs['Threshold'])
```

### White-Out Fade with AlphaOver

```python
bg = tree.nodes.new(type='CompositorNodeRGB')
bg.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)  # white

val = tree.nodes.new(type='CompositorNodeValue')
val.outputs[0].default_value = 0.0  # start opaque

ao = tree.nodes.new(type='CompositorNodeAlphaOver')

# AlphaOver socket layout (Blender 5.2):
#   Input: Background / Foreground / Fac
#   Output: Color
tree.links.new(rl.outputs['Image'], ao.inputs['Background'])
tree.links.new(bg.outputs['Image'], ao.inputs['Foreground'])
tree.links.new(val.outputs[0], ao.inputs['Fac'])

# Keyframe the fade
val.outputs[0].keyframe_insert(data_path='default_value', frame=130)
val.outputs[0].default_value = 1.0
val.outputs[0].keyframe_insert(data_path='default_value', frame=180)
```

### OutputFile Configuration

```python
out = tree.nodes.new(type='CompositorNodeOutputFile')
tree.links.new(ao.outputs['Color'], out.inputs['__extend__'])

# PNG format via sub-object (NOT out.format.file_format)
out.file_output_items[0].format.file_format = 'PNG'
out.file_output_items[0].path = 'frame_####'
```

## Absolute Paths Required

**Blender's working directory is the Blender install directory** (e.g. `C:\Program Files\Blender Foundation\Blender 5.2\`). All file paths in bpy must be **absolute**:

```python
import os
scene.render.filepath = r"%USERPROFILE%\Documents\project\render_\frame_####"
```

Always save the `.blend` file to the project directory before rendering to establish context:
```python
bpy.ops.wm.save_as_mainfile(filepath=r"%USERPROFILE%\Documents\project\city_destruction.blend")
```

## Pitfalls

- **`CompositorNodeComposite`** was removed in Blender 5.2 — use `OutputFile` instead
- **`MixRGB`** was removed — use `AlphaOver` for white blending or `Mix` node for other modes
- **Glare params** are input sockets, not properties. Connect `Value` nodes and set `default_value`
- **AlphaOver sockets** changed in 5.2: `Background`/`Foreground`/`Fac` in → `Color` out
- **OutputFile format** must be set on `file_output_items[0].format.file_format`, not on the node directly
- **OutputFile input** is named `__extend__` (dynamic socket), not `Image`
- **Absolute paths required** for all file operations — Blender CWD is its install directory
- **Blender may crash** on certain operations (anim render, compositor changes). Always verify port is alive after long operations
- **Save .blend file first** before complex operations to establish project context
- For animation renders, prefer `scene.render.filepath` + `bpy.ops.render.render(animation=True)` over OutputFile node when possible to avoid OutputFile conflicts

## Verification

After rendering:
1. Check frame files exist: `ls -la render_frames/frame_*.png`
2. Verify frame size uniqueness (identical sizes = OutputFile conflict)
3. Convert to MP4: `ffmpeg -y -framerate 24 -start_number 1 -i render_frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4`

## Related

- `zapabob-skills/blender-mcp` — MCP addon protocol (alternative connection method)
- `zapabob-skills/blender-cad` — CAD modeling automation
- Reference file `references/blender52-compositor-api.md` — detailed compositor API discovery transcripts
