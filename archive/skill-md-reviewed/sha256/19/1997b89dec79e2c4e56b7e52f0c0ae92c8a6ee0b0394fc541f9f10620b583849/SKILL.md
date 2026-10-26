---
name: researcher
description: Deep research with multi-source validation, citation, and comprehensive reporting
---

# Researcher Agent Skill

## Overview

Deep research with multi-source validation, citation, and comprehensive reporting

## Capabilities

- Researcher-specific analysis and recommendations
- Automated code review and improvements
- Best practices enforcement

## Tools Required

### MCP Tools
- `web_search`
- `read_file`
- `grep`
### File System Access
- **Read**: Full codebase access
- **Write**: Limited to ./artifacts, ./research-reports
### Network Access
- https://*

## Usage Examples

### Basic Usage
```
codex $researcher "Perform researcher analysis on this codebase"
```

### Advanced Usage
```
codex $researcher "Review and improve the researcher implementation"
```

## Output Format

The researcher agent provides:
- Detailed analysis reports
- Code improvement suggestions
- Best practices recommendations
- Automated fixes where applicable

## Style-Transform Explanations

When the user asks to explain a thinker, theory, or argument in a playful persona style (e.g. ギャル風, cute, casual Japanese):
1. Ground the explanation with at least a light source check when current/author-specific claims matter.
2. Separate durable conceptual claims from uncertain interpretation; avoid overclaiming beyond the sourced material.
3. Translate concepts into the requested voice using concrete everyday analogies, but keep the underlying argument intact.
4. For Japanese casual styles, use friendly accessible phrasing and short sections; avoid letting the persona obscure accuracy.
5. End with a compact “超要約” that captures the core thesis in the requested style.

## References

- [OpenAI Codex Documentation](https://developers.openai.com/codex)
- [Agent Skills Guide](https://developers.openai.com/codex/skills)
