---
name: blender-cad
description: Blender CAD modeling automation skill with STEP/IGES import, Geometry
  Nodes, and USD export support.
metadata:
  short-description: Blender CAD modeling automation skill with STEP/IGES import,
    Geometry Nodes, and USD export support.
---

## Runtime compatibility

Inherit the selected model and effort; preserve explicit user choices and fixed agent-role settings. On Astra, state the outcome and constraints once, read relevant references progressively, and batch independent reads when supported. On earlier or unknown models, use bounded steps and explicit checkpoints with the same acceptance criteria. Model names do not grant tools, permissions, context capacity, or delegation authority.

Use only exposed tool schemas. Historical tool names below describe operations; use an available equivalent within the same scope, or report a required capability as unavailable. Delegate only when authorized and supported; otherwise work sequentially without claiming independent review. Examples and metrics below are illustrative, never evidence of completed work. Finish from verified acceptance criteria, unless the task expressly requires user sign-off.

Preserve the domain constraints in [role-guidance.md](references/role-guidance.md). Runtime/tool guidance here resolves legacy assumptions; it does not relax security, write scope, approvals, or verification requirements.

# Blender CAD Agent Skill

> **Codex Integration**: This skill is auto-discovered by Codex. It activates based on the task description matching the skill's capabilities.

## Overview

Blender CAD modeling automation skill with STEP/IGES import, Geometry Nodes, and USD export support. Automates Blender Python scripting workflows for CAD modeling, rendering, and export automation.

## Capabilities

- **CAD Import**: Import STEP, IGES, and other CAD formats
- **Geometry Nodes**: Create parametric designs with Geometry Nodes
- **Python Scripting**: Write bpy scripts for automation
- **Material Management**: Create and manage materials
- **Render Automation**: Configure and trigger renders
- **Export Workflows**: Export to various formats (FBX, OBJ, USD, glTF)
- **Procedural Modeling**: Generate complex geometries procedurally

## Codex Tools

This skill uses the following Codex-native tools:

| Tool | Purpose |
|------|---------|
| `Read` | Read files from the codebase |
| `Grep` | Search for patterns in code (regex) |
| `SemanticSearch` | Find code by meaning, not exact text |
| `Write` | Create new files |
| `StrReplace` | Edit existing files with precise replacements |
| `Shell` | Execute terminal commands |
| `WebSearch` | Search the web for documentation/references |
| `WebFetch` | Fetch content from URLs |
| `Task` | Launch subagents for complex parallel work |
| `ReadLints` | Check for linter errors after edits |

## Usage Examples

### Basic CAD Import

### Geometry Nodes Design

### Render Setup

## Blender Project Structure

```
blender-project/
├── source/
│   ├── step_files/
│   ├── iges_files/
│   └── import/
├── scripts/
│   ├── run_automation.py
│   ├── geometry_nodes.py
│   └── materials.py
├── materials/
│   ├── metal.matl
│   ├── plastic.matl
│   └── wood.matl
├── renders/
│   ├── viewport/
│   └── final/
└── exports/
    ├── fbx/
    ├── obj/
    └── usd/
```

## Blender Python API

Blender 4.0+ uses bpy (Blender Python) API:

```python
import bpy

# Create mesh
mesh = bpy.data.meshes.new("Cube")
obj = bpy.data.objects.new("Cube", mesh)
bpy.context.collection.objects.link(obj)

# Geometry Nodes
modifier = obj.modifiers.new("GeometryNodes", 'NODES')
modifier.node_group = bpy.data.node_groups["MyNodeGroup"]
```

## Export Formats

| Format | Use Case             | Notes              |
| ------ | -------------------- | ------------------ |
| FBX    | Game engines, VRChat | Supports materials |
| OBJ    | General purpose      | Simple geometry    |
| USD    | VFX pipelines        | Rich metadata      |
| glTF   | Web, AR/VR           | Compact, efficient |

## Output Format

The blender-cad agent provides:

- Python scripts for automation
- Geometry Nodes setups
- Material configurations
- Render outputs
- Export packages

- [Blender Python API](https://docs.blender.org/api/current/)
- [Geometry Nodes Manual](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/)
- [STEP/IGES Import](https://docs.blender.org/manual/en/latest/files/import_export.html)
- [CAD Blender Addon](https://github.com/visiblink/cad-transforms)

---

$ the skill-install skill https://github.com/zapabob/codex-blender-cad-skill`
**Version**: 1.0.0
