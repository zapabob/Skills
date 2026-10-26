---
name: kanban-summary-create
category: productivity
description: Summarize messages and create kanban tasks.
---
# Summary and Task Creation Skill

This skill summarizes unread messages from LINE, Telegram, and Discord channels and creates corresponding tasks in the kanban board.

## Steps

1. Run `social-sync` to extract non-secret messages from the specified channels.
2. Identify actionable items in the summary.
3. Create tasks using `kanban-create-task --title "Title" --description "Description"`.
4. Verify with `kanban-show`.

## Example

```bash
kanban-create-task --title "Review Script Failure" --description "Investigate why disaster-news-jp.sh failed."
```

## Pitfalls

- Ensure only non-secret messages are processed.
- Keep task descriptions concise.

## Verification

After execution, the kanban board should list the new tasks.