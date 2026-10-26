---
name: creative-design
description: Class-level workflow for visual design, diagrams, HTML prototypes, design-token specs, creative coding, and critique.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
category: creative
metadata:
  hermes:
    tags: [design, diagrams, html, prototypes, design-systems, creative-coding, critique]
    category: creative
---

# Creative Design Operations

Use this umbrella for design work that spans visual composition, technical diagrams, HTML artifacts, design-token specifications, interactive sketches, creative browser demos, and critique.

## Choose the branch

- **Diagram** — architecture/infrastructure or explanatory SVG/HTML diagrams.
- **Artifact** — polished standalone HTML landing pages, decks, prototypes, or component labs.
- **Design system** — formal DESIGN.md tokens, references, contrast validation, and exports.
- **Sketch** — disposable 2–3 variant mockups for comparing directions before implementation.
- **Creative coding** — text-as-geometry, kinetic typography, or canvas demos.
- **Critique** — inspect supplied images explicitly, separate resemblance from plagiarism, and give skeleton-level redesign levers.

## Composition first

Name the primary surface before styling: Monitor, Operate, Compare, Configure, Decide/Learn, Explore, or Command/Inspect. Commit to a composition that serves that surface; do not decorate a generic hero/card grid onto every task. Prefer supplied brand/source context, use real copy, and verify the actual artifact in a browser when possible.

## Progressive disclosure

Keep the main workflow concise. Branch-specific recipes, templates, visual references, and critique notes live in `references/`, `templates/`, and `scripts/`.

## Verification

For artifacts, verify the file exists, syntax is valid, key interactions work, and browser console/layout errors are absent when browser inspection is available. For critiques, state exactly which images were inspected and distinguish evidence from uncertainty. For design tokens, validate references and contrast before delivery.

## Support files

The former narrow creative workflows are preserved as labeled support files under this umbrella. Use them as references, not as reasons to create another one-session skill.

## Style preference

- Favor mature, aesthetic, non-slop visuals that feel like intentional design rather than generic AI splash. Avoid oversaturated gradients, decorative blobs, and stock-looking hero sections absent client request.

## Windows desktop rule

- When visual work targets a running Blender session on Windows: prefer **Blender GUI-first** unless the user explicitly asks for Hermes-driven control.
- If control is explicitly requested, use the JSON-wrapped Blender MCP helper, not raw socket sends.
