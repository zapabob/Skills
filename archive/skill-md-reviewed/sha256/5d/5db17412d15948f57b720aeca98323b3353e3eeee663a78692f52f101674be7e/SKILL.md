---
name: hermes-desktop-preview
description: Hermes Desktop default preview tabs (YouTube, X).
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [desktop, preview, tabs, youtube, x]
    category: desktop
    related_skills: [computer-use]
---
# Hermes Desktop Preview Tabs Skill

This skill documents the default preview tabs feature in Hermes Desktop (Electron app).

When Hermes Desktop launches, the `$previewTabs` atom is initialized with `DEFAULT_PREVIEW_TABS`. This contains two pre-configured tabs: YouTube (`url:https://www.youtube.com`) and X (`url:https://x.com`). These appear in the right preview rail of the Hermes Desktop interface.

If tabs don't appear on launch:
- Ensure Hermes Desktop is fully running (the Electron app, not just the CLI)
- Restart Hermes Desktop if tabs are missing
- Feature only works when the app is running

## Vertical Split Behavior

URL previews (YouTube, X) open side by side in a row split — equal height, sharing rail width. File/artifact previews dock as before.

See `references/code-reference.md` for implementation details and the 2026-08-18 change.

Code reference: `apps/desktop/src/store/preview.ts`, `apps/desktop/src/app/chat/preview-tile.tsx`.
