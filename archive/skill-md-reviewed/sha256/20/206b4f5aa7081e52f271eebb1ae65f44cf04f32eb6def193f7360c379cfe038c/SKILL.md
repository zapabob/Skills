---
name: vrchat-dev
description: VRChat world and avatar development skill with UdonSharp, modularavatar,
  and PhysBones support. Automates VRChat SDK3 development workflows.
metadata:
  short-description: VRChat world and avatar development skill with UdonSharp, modularavatar,
    and PhysBones support. Automates VRChat SDK3 development workflows.
---

## Runtime compatibility

Inherit the selected model and effort; preserve explicit user choices and fixed agent-role settings. On Astra, state the outcome and constraints once, read relevant references progressively, and batch independent reads when supported. On earlier or unknown models, use bounded steps and explicit checkpoints with the same acceptance criteria. Model names do not grant tools, permissions, context capacity, or delegation authority.

Use only exposed tool schemas. Historical tool names below describe operations; use an available equivalent within the same scope, or report a required capability as unavailable. Delegate only when authorized and supported; otherwise work sequentially without claiming independent review. Examples and metrics below are illustrative, never evidence of completed work. Finish from verified acceptance criteria, unless the task expressly requires user sign-off.

Preserve the domain constraints in [role-guidance.md](references/role-guidance.md). Runtime/tool guidance here resolves legacy assumptions; it does not relax security, write scope, approvals, or verification requirements.

# VRChat Dev Agent Skill

> **Codex Integration**: This skill is auto-discovered by Codex. It activates based on the task description matching the skill's capabilities.

## Overview

VRChat world and avatar development skill with UdonSharp, modularavatar, and PhysBones support. Automates VRChat SDK3 development workflows including world building, avatar configuration, and upload automation.

## Capabilities

- **UdonSharp Development**: Write, compile, and optimize Udon/UdonSharp scripts for VRChat worlds
- **World Building**: Create VRChat worlds with dynamic content, interactive objects, and optimization
- **Avatar Configuration**: Configure avatars with modularavatar, PhysBones, and contact systems
- **Shader Integration**: Work with popular shaders like liltoon and Poiyomi
- **World Upload**: Automate world upload and version management
- **Performance Optimization**: Optimize worlds for various performance tiers

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

### Basic World Development

### Avatar Configuration

### UdonSharp Scripting

## VRChat Project Structure

```
vrchat-project/
├── Assets/
│   ├── Scripts/
│   │   └── Udon/
│   │       ├── MainController.cs
│   │       └── InteractiveObjects/
│   ├── Shaders/
│   ├── Materials/
│   └── Prefabs/
├── Packages/
│   ├── com.vrchat.sdk3/
│   ├── com.modularavatar/
│   └── com.liltoon/
├── ProjectSettings/
└── Unity/
```

## Performance Tiers

VRChat supports multiple performance tiers:

| Tier   | Description   | Requirements                   |
| ------ | ------------- | ------------------------------ |
| Low    | Minimum specs | Simple geometry, basic shaders |
| Medium | Balanced      | Moderate complexity            |
| High   | High-end      | Complex shaders, particles     |
| Ultra  | Maximum       | Full features enabled          |

## Output Format

The vrchat-dev agent provides:

- UdonSharp code with compilation
- World configuration files
- Avatar setup scripts
- Performance optimization recommendations
- Upload-ready packages

- [VRChat SDK3 Documentation](https://docs.vrchat.com/docs/sdk3)
- [UdonSharp Documentation](https://udosharp-docs.vercel.app/)
- [modularavatar](https://modularavatar.nadena.dev/)
- [PhysBones](https://docs.vrchat.com/docs/physbones)
- [VRChat Performance Stats](https://docs.vrchat.com/docs/performance-stats)

---

$ the skill-install skill https://github.com/zapabob/codex-vrchat-dev-skill`
**Version**: 1.0.0
