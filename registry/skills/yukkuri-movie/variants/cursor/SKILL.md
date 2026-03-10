---
name: yukkuri-movie
description: "ゆっくりMovieMaker (YMM4) video production skill with character animation, scene management, and MIDI integration."
short_description: ゆっくりMovieMaker (YMM4) video production skill with character animation, scene management, and MIDI integration.
---

# Yukkuri MovieMaker Agent Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

ゆっくりMovieMaker (YMM4) video production skill with character animation, scene management, and MIDI integration. Automates video production workflows for VTuber content creation using YukkuriMovieMaker.

## Capabilities

- **Character Animation**: Create and animate ゆっくり characters
- **Scene Management**: Manage scenes, timelines, and transitions
- **Audio Effects**: Configure audio effects and MIDI integration
- **Video Effects**: Apply video effects and filters
- **Project Management**: Create and organize YMM4 projects
- **Rendering**: Trigger and manage video rendering
- **Plugin Integration**: Work with YMM4 plugin architecture

## Cursor Tools

This skill uses the following Cursor-native tools:

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

### Basic Project Creation

### Character Animation

### Scene Management

## YMM4 Project Structure

```
ymm4-project/
├── project/
│   └── project.ymmp
├── characters/
│   ├── character1/
│   │   ├── pose1.pose
│   │   ├── pose2.pose
│   │   └── motion.motion
│   └── character2/
├── backgrounds/
│   ├── bg1.png
│   └── bg2.jpg
├── audio/
│   ├── bgm/
│   ├── se/
│   └── voice/
├── effects/
│   ├── videoeffects/
│   └── audioeffects/
└── output/
    └── rendered_video.mp4
```

## YMM4 Plugin Architecture

YMM4 supports plugins via COM interface:

```csharp
// Example YMM4 Plugin Interface
public interface IMovieMakerPlugin
{
    void Initialize(IMovieMakerApi api);
    void OnSceneChanged(SceneChangedEventArgs args);
    void OnRenderProgress(RenderProgressEventArgs args);
}
```

### Plugin Types

| Type        | Description          | Extension Point     |
| ----------- | -------------------- | ------------------- |
| AudioEffect | Audio processing     | `[AudioEffect]`     |
| VideoEffect | Video processing     | `[VideoEffect]`     |
| Full Plugin | Complete integration | `IMovieMakerPlugin` |

## ゆっくりCharacter Setup

ゆっくり characters have:

- Multiple facial expressions
- Body movement ranges
- Lip sync capability
- Eye tracking
- Accessory support

## Output Format

The yukkuri-movie agent provides:

- YMM4 project configurations
- Character animation setups
- Scene transition scripts
- Render job configurations
- Export packages

- [ゆっくりMovieMaker Official](https://imammura.channel.jp/)
- [YMM4 Plugin Documentation](https://booth.pm/ja/items/2666730)
- [ゆっくり素材配布所](https://sanabou.com/)
- [YMM4 API Reference](https://github.com/o8o8o8/Ymm4ApiDoc)

---

$ the skill-install skill https://github.com/zapabob/codex-yukkuri-movie-skill`
**Version**: 1.0.0
