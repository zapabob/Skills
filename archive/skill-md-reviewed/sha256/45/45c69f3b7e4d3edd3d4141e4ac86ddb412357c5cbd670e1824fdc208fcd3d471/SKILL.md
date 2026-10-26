---
name: japanese-concept-vocabulary
description: Japanese vocabulary for Hakua/VRChat conceptual layers.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [japanese, vocabulary, concept-layers, hakua, vrchat]
    category: autonomous-ai-agents
    related_skills: [ebbinghaus-memory, memory-maintenance]
---
# Japanese Concept Vocabulary for Hakua/Hermes

## When to Use

User explicitly prefers that critical Hermes Agent memories, conceptual layer descriptions, and policy guard statements use Japanese vocabulary (not English) for the Hakua/VRChat concept layers. This ensures consistency across sessions, language model alignment, and durable memory integrity.

## Concept Mappings

| Concept | Japanese | English Default |
|---------|----------|----------------|
| Hermes Agent | 中枢/agency kernel | agency kernel |
| OpenClaw | 外殻/embodiment shell | embodiment shell |
| VRChat Harness | 身体反射/reflex layer | reflex layer |
| VOICEVOX | 声帯/vocal layer | vocal layer |
| Memory | 同一性の連続性/identity continuity | identity continuity |
| Policy Guard | 安全な自律境界/self-restraint | safe autonomous boundary |
| Audit Log | 反省的記憶/reflective memory | reflective memory |

## Procedure

### Documentation Pattern

When writing conceptual descriptions, use the Japanese term from the mapping table above as the primary term. Append English in parentheses for external compatibility: e.g., "agency kernel (中枢)".

### Memory Encoding

When encoding memories related to conceptual layers:
1. Set `language` field to `ja` if content is primarily Japanese
2. Populate `cue_vector` with token counts reflecting Japanese text analysis
3. Ensure `salience` and `retention` reflect conceptual importance
4. Cross-reference with SOUL.md or MEMORY.md using Japanese terminology

## Verification

After writing: confirm Japanese terms present, no English-default terms appear alone, mapping table consistent, language check passes, SOUL.md cross-reference verified.

## Pitfalls

- ❌ Mixing English defaults without Japanese counterparts in critical memories
- ❌ Storing unverified Wiki facts in Ebbinghaus without Japanese vocabulary encoding
- ❌ Using English term as sole term for Hermes Agent/VRChat concepts
- ❌ Forgetting to update both mapping AND memory encoding
- ❌ Assuming preference applies to all contexts (covers internal Hermes concepts/memory primarily)

## Verification Steps

1. Read recent Hakua/VRChat memories - confirm Japanese terms present
2. Check `language: ja` set where content Japanese
3. Verify mapping table current and complete
4. Check no language-mixing issues flagged
5. Cross-reference with SOUL.md for consistency

## Related Skills

- `skills/autonomous-ai-agents/ebbinghaus-memory` - Memory encoding with language-aware cues
- `skills/hermes-agent-skill-authoring` - Skill authoring reference

## Version History

- 0.1.0 (2026-09-09): Initial release with core conceptual layer mappings and user preference documentation