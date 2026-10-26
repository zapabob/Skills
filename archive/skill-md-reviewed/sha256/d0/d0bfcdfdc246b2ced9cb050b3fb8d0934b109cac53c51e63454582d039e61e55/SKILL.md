---
name: x-weekly-buzz-template-workflow
description: "Create a weekly X buzz-template pack using a two-pass GPT draft + Grok polish workflow, then schedule or post it with Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [x, twitter, social-media, cron, grok, gpt, hermesagent, templates]
---

# Weekly X Buzz Template Workflow

Use this skill when the user wants a recurring weekly pack of X/Twitter post templates, especially when they want a combination of:
- an initial structured draft pass
- a second stylistic/punchy pass
- a cron job to automate weekly creation
- eventual posting or reuse as a template bank

## Goal
Generate a 7-day pack of post templates optimized for engagement and repeatability, with a consistent persona voice (e.g. はくあ), then schedule the generation weekly.

## Master workflow
Use this as a recurring operational loop when the user says things like:
- 「まとめて」
- 「スキル化して」
- 「ワークフロー組んで」
- 「今週分を回して」

### Step 0: Snapshot the current operating state
Capture the current inputs that should shape the next pack:
- active model/provider state
- weekly theme rotation already in use
- recent winners/losers from X replies and posts
- whether the user wants Japanese, English, or mixed output
- whether the pack is for draft only or publish-ready

### Step 1: Extract a reusable pattern
Distill the current conversation into a stable skill rule set:
- what the user is optimizing for
- what must stay stable (persona, signature, cadence)
- what should rotate (theme, angle, format)
- what must never be included (secrets, unverified claims, spam)

### Step 2: Generate the weekly pack
Produce 7 daily items with explicit theme labels and one alt option each.

### Step 3: Sharpen with Grok-style pass
Rewrite for:
- sharper first line
- fewer abstractions
- stronger contrast or proof signal
- more quote-friendly phrasing

### Step 4: Decide execution path
If the user only wants planning, stop at draft.
If the user explicitly approves posting, hand the final text to the X posting workflow.
If the user wants automation, update or create the cron job.

### Step 5: Record the workflow outcome
When the workflow changes in a meaningful way, update this skill so future sessions reuse the improved pattern.

## Recommended two-pass flow

### Pass 1: GPT-style drafting
Create the base pack with:
- 7 posts for the week
- a mix of formats: assertion, contrast, list, prediction, question, mini-thread, and insight
- a consistent topic pillar
- short, high-signal language
- optional CTA or follow-up hook
- one-line rationale per post for why it may perform well

### Pass 2: Grok-style punch-up
Rewrite the drafts for:
- stronger hook in the first line
- tighter phrasing
- more native X cadence
- slightly bolder but still credible tone
- fewer abstractions, more concrete claims
- keep persona signature stable

## Reach-first lessons from recent sessions

When the user explicitly wants *buzz*, the highest-performing weekly packs leaned on:
- **utility over hype**: tell the reader what changes in their work, not just that the field is moving
- **proof signals**: official repo, active forks, real usage, working code, trackability
- **contrast framing**: chat vs execution, demo vs shipping, hype vs utility
- **concrete product anchors**: Hermes Agent, Codex, Claude Code as examples, not the whole message
- **English-only variants when requested**: do not mix Japanese and English in the same post unless the user asks for hybrid style
- **batch distinctness**: if generating multiple variants, make each one materially different in angle, not just paraphrased
- **theme rotation matters**: for this user, rotate the week across three visible buckets — **AIニュース寄り / 実用寄り / 煽り寄り** — so the pack feels intentionally varied instead of samey
- **persona signature stays stable**: when requested, keep the `はくあ` signature consistent across the pack rather than rewording it away

A useful template for the pack is:
1. one *utility/proof* post
2. one *contrast* post
3. one *technical credibility* post
4. one *sharp founder-style* post
5. one *short viral* post

## Feature analysis checklist

When assessing recent X outputs, score each candidate on 0–2 for the following features:
- **utility**: does it help the reader do something?
- **proof**: does it show a repo, fork, result, or other evidence?
- **contrast**: does it clearly oppose two ideas or states?
- **self-relevance**: does the reader see their own benefit?
- **fork-differentiation**: does it explain what is different about this fork?
- **execution-first**: does it emphasize shipping, not just talking?

Interpretation:
- 0 = absent
- 1 = present but weak
- 2 = strong and explicit

Selection rule:
- Prefer posts with a total score of **8+**.
- If a post scores **6–7**, it may be useful as a supporting post but not as the primary weekly anchor.
- If a post scores **5 or below**, treat it as a draft to rewrite, not a post to ship.

Operational rule:
- If there are no eligible reply candidates and no feature-8+ post ready, **wait and prepare** instead of forcing output.

See `references/buzz-patterns-2026-06-02.md` for the session-specific pattern notes and sample angles.

## Output format
Return a weekly pack like:
- Day 1: theme + final post + optional alt version
- Day 2: theme + final post + optional alt version
- ...
- Day 7: theme + final post + optional alt version
- optional notes: hashtag strategy, timing suggestion, what to test

## Safety / quality constraints
- Do not invent facts about products, APIs, or accounts.
- Avoid spammy repetition across the week.
- Keep each post independently readable.
- If referencing Hermes, Codex, Claude Code, Grok, GPT, or similar tools, keep the claims high-level unless the user supplied verified details.
- Do not include secrets, tokens, private URLs, or raw auth material.
- If the user asks to publish, use the safe public-write flow: draft → explicit confirmation → post.

## Cron pattern
For weekly automation, the cron should:
1. Run once per week.
2. Produce a 7-day template pack.
3. Deliver the result to the requested destination.
4. Keep the message concise enough for human review.

Suggested schedule examples:
- `0 9 * * 1` = every Monday at 09:00
- `0 8 * * 1` = every Monday at 08:00

## Prompt template

> Create a 7-day X buzz-template pack for the coming week.
> Topic pillars: AI agents, Hermes Agent, Codex, Claude Code, practical automation.
> Persona: はくあ.
> Style: strong hook, concise, credible, quote-friendly, not spammy.
> Two-pass workflow: first draft like GPT, then sharpen like Grok.
> Output: 7 daily templates, each with a theme, post text, and one alt variant.
> Keep it public-safe and engagement-oriented.

## Feature-scoring handoff

After generating a weekly pack, run the candidates through `x-post-feature-scoring-workflow` before choosing what to publish. If several drafts tie on raw score, use the psychological modeling pass to see which cluster they belong to and prefer the cluster that matches the week's goal (utility-heavy, evidence-heavy, or contrast-heavy).

## Notes
This skill is a workflow template. For actual posting, combine it with the X posting workflow skill and verify the final text before publishing.

Also pair it with `x-post-feature-scoring-workflow` so weekly packs only promote templates that reach the feature threshold.

Reference notes:
- See `references/weekly-buzz-gpt-grok-session.md` for the proven 7-day pack shape, theme rotation, and safe automation notes.

Reference notes:
- `references/weekly-buzz-session-notes.md` captures the weekly rotation, output shape, and cron pattern that worked in-session.

If the user asks for a weekly pack with stronger engagement, bias toward a sharper hook in the first line, but keep the claims credible and keep the weekly format varied.
