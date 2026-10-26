---
name: hermes-desktop-preview-layout
description: Use when changing Hermes Desktop preview layout.
version: 1.0.0
author: curator
license: MIT
metadata:
  hermes:
    tags: [hermes, desktop, preview, pane-system, paneMirror, electron, renderer]
    category: software-development
---

# Hermes Desktop Preview Layout

## Overview

Use this skill when changing the Hermes Desktop preview surface in `apps/desktop`, especially preview tab identity, persisted preview state, `paneMirror` contributions, or simultaneous live URL panes. The preview system is a layout-tree surface: every file, URL, and artifact preview is represented as a pane contribution and participates in the zone tab strip, drag, stack, split, and close behavior.

This skill complements the broader Hermes Desktop plugin skill. Use this skill for preview/layout behavior; use the broader desktop skill for plugin SDK or general pane contributions.

## Architecture checkpoints

Before editing, inspect:

- `apps/desktop/src/store/preview.ts` for `PreviewTarget`, `$previewTabs`, persistence decoding, `openPreview`, and `previewTabId`.
- `apps/desktop/src/app/chat/preview-tile.tsx` for `watchPreviewTileMirror` and the relationship between preview tabs and layout-tree panes.
- `apps/desktop/src/app/chat/pane-mirror.ts` for mirror callback semantics.
- `apps/desktop/src/components/pane-shell/tree/model.ts` for split directions and anchors.
- `apps/desktop/src/app/chat/right-rail/preview.tsx` for the pane body.
- Related store and reader tests before changing identity or selection semantics.

Use the existing layout tree and `paneMirror`; do not introduce a second preview layout mechanism or resurrect a separate right-rail tab bar.

## Multi-URL identity pattern

When multiple live URLs must remain visible at once, URL previews need independent stable IDs. Do not use a singleton such as `url:browser`:

```ts
export function previewTabId(target: PreviewTarget): RightRailTabId {
  return `${target.kind}:${target.url}`
}
```

The persisted decoder must normalize legacy URL entries to the same URL-specific IDs without filtering all but the last URL. Opening the same URL twice should still refresh/re-front one tab through the existing ID-based deduplication; opening different URLs should create distinct tabs.

## Vertical split pattern

When the first URL should open beside chat and subsequent URLs should appear below it, pass the full preview item to `paneMirror` so docking can inspect target kind:

```ts
function urlPreviewIds(): string[] {
  return $previewTabs
    .get()
    .filter(tab => tab.target.kind === 'url')
    .map(tab => tab.id)
}

const watchPreviewTileMirror = paneMirror<{ id: string; target: PreviewTarget }>({
  source: $previewTabs,
  key: tab => tab.id,
  prefix: PREVIEW_TILE_PREFIX,
  dir: tile => {
    if (tile.target.kind !== 'url') return 'right'
    return tile.id === urlPreviewIds()[0] ? 'right' : 'bottom'
  },
  anchor: tile => {
    if (tile.target.kind !== 'url') return 'workspace'
    const firstUrlId = urlPreviewIds()[0]
    return tile.id === firstUrlId ? 'workspace' : `${PREVIEW_TILE_PREFIX}:${firstUrlId}`
  },
})
```

Keep non-URL behavior explicit. The first URL is anchored to `workspace`; later URLs are anchored to the first URL pane and use `bottom`. This creates a vertical split while retaining independent webview state and tab identity.

## Persistence and migration

Changing preview identity is a persistence migration, not only a rendering change. Re-key restored URL tabs consistently, preserve valid file/artifact migration behavior, and avoid destructive “keep last URL” filtering when simultaneous URL panes are now supported. Consider stale layout-tree entries and document whether users must close/reopen previews for a clean re-dock.

## Regression tests

Update or add focused tests for:

- different URLs produce two URL tabs and the latest becomes active;
- the same URL remains one tab and is refreshed/re-fronted;
- persisted URL tabs retain separate identities;
- `read_preview` readers are keyed by each unique URL tab ID;
- files and artifacts keep their previous placement and lifecycle behavior.

Prefer the focused UI test command before broad suites:

```text
npm run test:ui -- src/store/preview.test.ts src/store/preview-persistence.test.ts src/app/chat/right-rail/preview-reader.test.ts
```

## Verification and reporting

Run the strongest available checks and keep evidence separated by scope:

```text
npx tsc -p tsconfig.json --noEmit
npm run lint
npm run typecheck
npm run build
npm run test:ui -- <focused paths>
git diff --check
```

A renderer-only typecheck passing does not prove Electron or e2e typechecks pass. If a full gate is blocked by an unrelated missing native dependency or staging step, report the exact blocker and do not label the focused renderer change as failed. Likewise, if a broad test suite times out or has unrelated failures, report those separately from focused test results.

## References

- `references/multi-url-vertical-split.md` — compact implementation recipe, migration notes, and verification evidence for simultaneous YouTube/X-style URL previews.

## Pitfalls

- Do not compute URL docking rules for every preview item; files and artifacts must remain explicit.
- Do not keep the old singleton URL ID while claiming multi-pane support.
- Do not update only the renderer and forget persisted-tab decoding or reader tests.
- Do not claim a complete build from a successful Vite bundle if native dependency staging failed.
- Do not use stale comments that still describe the Browser as a singleton.
