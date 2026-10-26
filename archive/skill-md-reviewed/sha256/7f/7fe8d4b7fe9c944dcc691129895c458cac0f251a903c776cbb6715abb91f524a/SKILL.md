---
name: workflow-distill
description: "Use when saving workflow as reusable skill; write, create."
category: productivity
version: "1.0.0"
author: "Hermes"
license: "MIT"
hermes:
  tags: ["workflow", "distill", "reusable"]
  related_skills: ["productivity"]
---
## When to Use
Use when saving workflow as reusable skill; write, create.
**Description**: Use when saving workflow as reusable skill; write, create.

## Steps
1. Review the conversation transcript to identify major actions (tool calls, commands, decisions).
2. Summarize each step concisely.
3. Draft the skill description and one-line behavior.
4. Write the skill content with YAML frontmatter and markdown body.
5. Create the skill using `skill_manage create`.
6. Verify by loading the skill with `skill_view(name='workflow-distill')`.

## Pitfalls
- Description must be <=57 characters.
- Skill name must be unique and follow naming conventions.
- Ensure steps are clear and actionable.

## Verification
- Load the skill with `skill_view(name='workflow-distill')`.
- Confirm the content matches the drafted steps.