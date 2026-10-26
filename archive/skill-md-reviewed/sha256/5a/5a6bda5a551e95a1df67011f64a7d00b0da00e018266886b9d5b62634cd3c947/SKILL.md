---
name: distill-conversation-workflow
description: "Distill conversation steps into reusable skill"
version: "1.0.0"
author: "Hermes"
license: "MIT"
hermes:
  tags: ["workflow", "distill", "reusable"]
  related_skills: ["productivity"]
---

## When to Use

Use this skill to capture and save a reusable workflow based on a recent conversation, turning steps into a repeatable skill.

## Steps

1. Identify major actions (tool calls, commands, decisions) in the conversation.
2. Summarize each step concisely.
3. Draft a one-line description (<=57 characters).
4. Write the skill content with YAML frontmatter and markdown body.
5. Create the skill using `skill_manage create`.
6. Verify by loading with `skill_view(name='distill-conversation-workflow')`.

## Pitfalls

- Description must be <=57 characters.
- Skill name must be unique and follow naming conventions.
- Ensure steps are clear and actionable.

## Verification

- Load the skill with `skill_view(name='distill-conversation-workflow')`.
- Confirm the content matches the drafted steps.