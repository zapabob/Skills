# SOP Frontend Design

## Scope

Apply this SOP to all browser UI, product pages, web apps, dashboards, prototypes, visual redesigns, component libraries, and frontend work where layout, interaction, typography, imagery, or user perception can affect the result.

This SOP supplements `SOP-WebApp-Development.md`. For implementation language rules, also apply the relevant language SOP such as `SOP-TypeScript.md`.

## Source Standards

1. Use `DESIGN.md` as the durable design-system contract when a project has a visual identity or repeatable UI surface.
2. Use Apple site UI/UX patterns as a reference for clarity, product-first hierarchy, concise interaction choices, restrained composition, high-quality real imagery, and progressive disclosure.
3. Use existing project design systems first. If local tokens, components, brand rules, or Figma references exist, derive changes from them before adding new visual language.
4. Do not copy Apple trade dress, assets, marks, product-page content, or proprietary styling. Extract operational principles only.
5. Treat accessibility, performance, responsive behavior, and visual regression risk as frontend release criteria.

## Reference URLs

- `google-labs-code/design.md`: `https://github.com/google-labs-code/design.md`
- Apple site reference: `https://www.apple.com/`
- Apple product-page reference: `https://www.apple.com/iphone-17-pro/`

These URLs are evidence sources, not frozen specifications. If a task depends on exact current behavior, inspect the live pages again before implementation.

## DESIGN.md Contract

1. A project-level `DESIGN.md` should combine YAML front matter for machine-readable tokens with Markdown sections for human-readable rationale.
2. The YAML token layer is normative. The prose explains why those values exist and how to apply them.
3. Required token groups for mature frontend work:
   - `colors`: semantic colors for surfaces, text, borders, states, and accents.
   - `typography`: named type roles with font family, size, weight, line height, and letter spacing.
   - `spacing`: spacing scale used by layout, components, and responsive gaps.
   - `rounded`: radius scale for controls, cards, media, and containers.
   - `components`: tokenized button, input, card, nav, modal, and state variants where applicable.
4. Recommended Markdown section order:
   - `Overview`
   - `Colors`
   - `Typography`
   - `Layout`
   - `Elevation & Depth`
   - `Shapes`
   - `Components`
   - `Do's and Don'ts`
5. Preserve unknown but intentional sections. Reject duplicate section headings and broken token references.
6. Validate `DESIGN.md` before relying on it:
   - `npx @google/design.md lint DESIGN.md`
   - On Windows package scripts, prefer the `designmd` binary alias when direct `.md` command resolution is unreliable.
7. For design-system changes, compare before and after:
   - `npx @google/design.md diff DESIGN-before.md DESIGN.md`
8. Any frontend implementation that introduces new colors, type sizes, radii, spacing values, or component variants must either reference existing `DESIGN.md` tokens or update `DESIGN.md` in the same change.

## Apple-Informed UI/UX Baseline

1. Start with the object or task. The first viewport must make the product, workflow, or primary user action unmistakable.
2. Use restrained global navigation. Keep top-level choices stable, short, and organized around user intent.
3. Keep primary copy concise. Headings should name the product, task, or concrete outcome; supporting copy carries explanation.
4. Prefer one primary action and one secondary action per major section. Avoid competing command clusters.
5. Use real product, workflow, or state imagery where visual inspection matters. Decorative imagery must not replace information.
6. Reveal detail progressively. Lead with the high-value summary, then expose highlights, comparison, technical detail, pricing, requirements, or legal notes as the user moves deeper.
7. Use large spacing only where it serves hierarchy. Dense operational tools should remain scan-friendly and efficient.
8. Pair polished visual rhythm with plain operability: visible focus, keyboard access, readable contrast, predictable scroll behavior, and no hidden dependency on animation.
9. Treat footnotes, constraints, compatibility, pricing, and legal caveats as part of UX, not afterthoughts.
10. Make responsive states intentional. Mobile and desktop should preserve the same task priority, not merely collapse layout.

## Procedure

1. Define the frontend requirement:
   - user goal
   - primary screen or flow
   - target devices
   - success criteria
   - known constraints and residual risks
2. Inspect existing visual authority:
   - local `DESIGN.md`
   - component library
   - CSS variables or theme config
   - screenshots or Figma references
   - production pages
3. If no visual authority exists, create `DESIGN.md` before broad UI work. Keep it small, explicit, and usable by agents and engineers.
4. Map Apple-informed principles to the project context:
   - product/task first viewport
   - concise hierarchy
   - restrained navigation
   - real imagery or concrete UI state
   - progressive detail
   - explicit caveats and constraints
5. Implement with project-native components and tokens. Avoid new abstractions unless they remove meaningful duplication or match established local patterns.
6. Verify:
   - lint and typecheck where applicable
   - `DESIGN.md` lint when present or changed
   - keyboard navigation
   - WCAG AA contrast for text and critical controls
   - responsive screenshots for mobile and desktop
   - console health in browser verification
   - no text overflow, overlapping UI, or layout shift in primary states
7. Record evidence in `_docs` for substantive changes:
   - source standards used
   - changed files
   - verification commands
   - skipped checks and reasons
   - residual risks

## Prohibitions

1. Do not create generic purple-gradient, card-heavy, oversized-padding AI-style interfaces unless a project design system explicitly requires them.
2. Do not use Apple assets, logos, product copy, or page structure as a direct clone.
3. Do not introduce raw color, spacing, typography, radius, or shadow values when a token exists.
4. Do not hide important actions behind hover-only or animation-only affordances.
5. Do not ship frontend changes without checking mobile and desktop behavior.
6. Do not let marketing composition replace the actual usable first screen for apps, tools, dashboards, or games.

## Acceptance Criteria

- The relevant frontend requirement is explicit.
- Existing visual authority was inspected or a new `DESIGN.md` was created.
- Tokens and component choices are traceable to `DESIGN.md` or the project design system.
- Apple-informed UI/UX principles are applied as operational principles, not copied branding.
- Accessibility, responsive layout, and browser health have fresh verification evidence.
- Residual risks and skipped checks are documented.
