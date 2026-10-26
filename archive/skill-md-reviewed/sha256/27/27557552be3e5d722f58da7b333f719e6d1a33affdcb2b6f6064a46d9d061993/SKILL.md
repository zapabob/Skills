---
name: blender-52-api-guide
description: Guide to Blender 5.2 API changes for automated scene generation, covering compositor system updates, animation data access, and rendering setup.
version: 1.0.0
author: hudson (via Hermes Agent)
tags: [blender, 3d, animation, api, migration, bpy]
platforms: [linux, macos, windows]
---

# Blender 5.2 API Changes for Automation

This guide covers key breaking changes in Blender 5.2 that affect automated/scripted workflows, particularly for scene setup, compositing, and animation.

## Compositor System Overhaul

### The Change
In Blender 5.2, the old `scene.node_tree` system for compositing was completely removed and replaced with `scene.compositing_node_group`.

### Before (Blender 5.1 and earlier)
```python
# This will FAIL in Blender 5.2
if not scene.node_tree:
    scene.node_tree = bpy.data.node_groups.new('Compositor', 'CompositorNodeTree')

# Access nodes
nodes = scene.node_tree.nodes
links = scene.node_tree.links
```

### After (Blender 5.2+)
```python
# Create or get the compositing node group
if not scene.compositing_node_group:
    scene.compositing_node_group = bpy.data.node_groups.new('Compositor', 'CompositorNodeTree')

# Access nodes THROUGH the node group
cg = scene.compositing_node_group
nodes = cg.nodes
links = cg.links

# Remember to clear existing nodes if reusing
for node in nodes:
    nodes.remove(node)
```

### Key Node Types for Effects
- **Bloom/Glare**: Use `CompositorNodeGlare` with `inputs["Type"].default_value = "Bloom"`
- **White Color**: Use `CompositorNodeRGB` for constant color output
- **Alpha Blending**: Use `CompositorNodeAlphaOver` for fade effects
- **Output**: Use `CompositorNodeOutputFile` (NOT `CompositorNodeComposite` which doesn't exist)

## Animation Data Access Changes

### The Change
In Blender 5.2, animation fcurves are no longer accessed directly via `action.fcurves`. Instead, they are organized within `action.slots`.

### Before (Blender 5.1 and earlier)
```python
# This will FAIL in Blender 5.2
for fcu in obj.animation_data.action.fcurves:
    fcu.interpolation = 'BEZIER'
```

### After (Blender 5.2+)
```python
# Correct way to access fcurves
if obj.animation_data and obj.animation_data.action:
    action = obj.animation_data.action
    for slot in action.slots:  # Note: iterating through slots
        for fcu in slot.fcurves:  # Then accessing fcurves from each slot
            fcu.interpolation = 'BEZIER'
            fcu.handle_left_type = 'AUTO_CLAMPED'
            fcu.handle_right_type = 'AUTO_CLAMPED'
```

### Important Notes
- Always check if `action` exists before accessing `.slots`
- Some object types may have different slot structures
- The `slots` collection corresponds to animated properties (location, rotation, scale, etc.)

## Node Setup for Common Effects

### Bloom/Glow Effect
```python
# Glare node for bloom
glare = nodes.new('CompositorNodeGlare')
glare.location = (-200, 0)
glare.inputs["Type"].default_value = "Bloom"  # Options: 'Glare', 'Ghosts', 'Streaks', 'Bloom'
glare.inputs["Quality"].default_value = "High"  # 'Low', 'Medium', 'High'
glare.inputs["Strength"].default_value = 1.5
glare.inputs["Threshold"].default_value = 0.8
glare.inputs["Size"].default_value = 0.6
```

### Fade to White (AlphaOver)
```python
# White color source
rgb_node = nodes.new('CompositorNodeRGB')
rgb_node.location = (-200, -300)
rgb_node.outputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # White RGBA

# AlphaOver for blending
alpha_over = nodes.new('CompositorNodeAlphaOver')
alpha_over.location = (200, 0)
# Factor will be animated (0.0 = original, 1.0 = white)

# Linking: Render Layers -> Glare -> AlphaOver (background)
#                         RGB (white) -> AlphaOver (foreground)
links.new(rl.outputs["Image"], glare.inputs["Image"])
links.new(glare.outputs["Image"], alpha_over.inputs["Background"])
links.new(rgb_node.outputs["Color"], alpha_over.inputs["Foreground"])
# Note: The final output is taken from the last node in the chain
# In practice, the compositor outputs the combined result
```

## Animation Setup Patterns

### Setting Keyframes Safely
```python
def set_keyframe_safe(obj, prop, frame, value):
    """Set a keyframe only if the property can be animated"""
    try:
        setattr(obj, prop, value)
        obj.keyframe_insert(data_path=prop, frame=frame)
    except TypeError:
        # Property doesn't support keyframing
        pass
```

### Animating Material Properties
```python
# For emission strength
emission_node = mat.node_tree.nodes['Emission']
emission_node.inputs['Strength'].default_value = 50.0
emission_node.inputs['Strength'].keyframe_insert("default_value", frame=30)
emission_node.inputs['Strength'].default_value = 120.0
emission_node.inputs['Strength'].keyframe_insert("default_value", frame=40)
```

## Rendering Settings

### For Transparent Background (PNG)
```python
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
# Note: PNG with RGBA preserves transparency
```

### Eevee Specific Notes
```python
scene.render.engine = 'BLENDER_EEVEE'
# Bloom is NOW handled via compositor, not eevee settings
# scene.eevee.use_bloom = False  # This property may not exist in 5.2
# Use compositor glare node instead
```

## Common Pitfalls and Solutions

### Pitfall 1: "'Action' object has no attribute 'fcurves'"
**Cause**: Using pre-5.2 animation access pattern
**Solution**: Always access fcurves via `action.slots[].fcurves`

### Pitfall 2: "'bpy_prop_collection[key]: key \"Image\" not found'"
**Cause**: Trying to access non-existent node outputs
**Solution**: In Blender 5.2, `CompositorNodeRGB` outputs are named "Color" not "Image"
**Correct**: `rgb_node.outputs["Color"]`

### Pitfall 3: Render output not saving
**Cause**: Using relative paths or incorrect node setup
**Solution**:
- Use absolute paths: `bpy.context.scene.render.filepath = "/tmp/render_####.png"`
- Ensure the compositor node tree is properly linked (outputs don't need explicit connection to file output in newer versions, but it's safer to connect)
- For file output: `file_output = nodes.new('CompositorNodeOutputFile')`

### Pitfall 4: Missing bloom effect
**Cause**: Expecting bloom from Eevee settings
**Solution**: Blender 5.2 moved bloom to compositor - must use Glare node with Type="Bloom"

## Verification Checklist
When testing your Blender 5.2 automation script:

☐ Compositor node tree accessed via `scene.compositing_node_group`
☐ Glare node Type set to "Bloom" for bloom effect
☐ RGB node outputs accessed via `["Color"]` not `["Image"]`
☐ Animation fcurves accessed via `action.slots[].fcurves`
☐ Keyframe interpolation set after animating properties
☐ Render filepath uses absolute path with frame padding (e.g., `frame_####.png`)
☐ Film transparency enabled for PNG alpha channel

## Example Workflow
See the `city_destruction_sim.py` script for a complete example implementing:
- 5x5 grid of animated buildings with destruction keyframes
- Bomb drop and explosion animation
- Shockwave ring animation
- Mushroom cloud growth with particle smoke
- Camera animation with bezier interpolation
- Compositor setup for bloom and fade-to-white effects
- Eevee rendering to PNG sequence

This pattern ensures compatibility with Blender 5.2+ while maintaining the visual effects expected from the animation.