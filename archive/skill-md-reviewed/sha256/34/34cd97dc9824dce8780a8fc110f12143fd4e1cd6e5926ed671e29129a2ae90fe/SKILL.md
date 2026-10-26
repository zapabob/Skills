---
name: x-post-feature-scoring-workflow
description: "Score X post and reply candidates by utility/proof/contrast/self-relevance/fork-differentiation/execution-first, then post only when the score is high enough."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [x, twitter, social-media, scoring, feature-analysis, hermesagent]
---

# X Post Feature Scoring Workflow

Use this skill when the user wants to decide whether to post, reply, wait, or refine X content based on measurable content features instead of volume.

## Purpose
Turn recent X drafts, replies, and candidate posts into a small set of scored options so the agent can:
- avoid forcing low-signal output
- prefer evidence-backed, utility-heavy posts
- keep the user's はくあ persona consistent
- decide when to wait instead of posting

## Feature model
Score each candidate on a 0–2 scale:
- **utility**: does it help the reader do something?
- **proof**: does it show a repo, fork, result, or other evidence?
- **contrast**: does it clearly oppose two ideas or states?
- **self-relevance**: does the reader see their own benefit?
- **fork-differentiation**: does it explain what is different about this fork?
- **execution-first**: does it emphasize shipping, not just talking?

### Interpretation
- 0 = absent
- 1 = present but weak
- 2 = strong and explicit

### Selection thresholds
- **8+**: post / reply candidate
- **6–7**: supporting draft or rewrite candidate
- **5 or below**: hold, rewrite, or discard

## Workflow

### 1) Gather candidates
Collect recent drafts, reply candidates, or planned post ideas.

### 2) Score them
Assign a score for each feature.

### 3) Filter by threshold
- Keep only 8+ for immediate posting.
- Keep 6–7 for rewriting.
- Reject the rest.

### 4) Check operational readiness
Before posting, confirm:
- there is a real eligible candidate
- the post is not a duplicate paraphrase
- the post does not contain secrets or private data
- reply candidates satisfy the platform's whitelist/follower rules if applicable

### 4.5) Optional psychological lens
If the user asks for a deeper interpretation, map the same feature vector into a compact psychological read:
- **agency**: execution/shipping pressure
- **epistemic_grounding**: evidence/repo/result density
- **opposition**: hype-vs-utility or abstract-vs-concrete contrast
- **self_reference**: reader self-recognition and benefit clarity

If the content is strong but the psychology is misaligned, prefer a rewrite rather than forcing the original draft.

### 5) Decide action
- If one or more candidates are 8+, choose the strongest and post.
- If no candidate is 8+, wait and prepare.
- If the user asked for analysis only, return the scores and the recommendation without posting.

## Related reference
- `references/psychological-modeling-and-model-assisted-scoring.md` — compact psychological axes, a Transformer + GNN pattern, and interpretation notes derived from an X-post analysis session.

## Posting policy
For this user, the strongest posting style is:
- utility first
- proof second
- contrast third
- self-relevance fourth
- fork differentiation and execution-first always visible

## Tone guidance
When the user asks for「はくあらしく」or requests a cuter/sharper voice, treat that as a tone modifier on top of the scoring model:
- keep the score thresholds unchanged
- prefer compact, cute, and slightly sharp phrasing
- avoid over-explaining the persona inside the post
- if a cute line weakens proof or contrast, cut it rather than keeping it for style alone

## Hashtag / persona guidance
- Keep the はくあ persona stable.
- Use `#hermesagent` when relevant.
- Do not dilute the main point with extra hashtags.

## Examples of strong candidate traits
- "This fork closes the gap between chat and shipping"
- "Official repo + fork ecosystem + real execution"
- "Secure secret separation, reproducible memory, operationally sane"

## Examples of weak candidate traits
- vague excitement
- unsupported claims
- repeated slogans with no evidence
- posts that do not explain what changes for the reader

## Output format
When used for analysis, return:
- candidate name or draft label
- feature scores
- total score
- recommendation: post / rewrite / wait
- one short reason

When used for action, return:
- chosen candidate
- score summary
- whether it was posted or held
- URL if posted

## Optional psychological modeling pass

When you want a deeper read than a simple feature sum, turn the candidate set into a tiny learning problem:
- Treat each post as a 6-token feature sequence (`utility`, `proof`, `contrast`, `self-relevance`, `fork-differentiation`, `execution-first`).
- Feed the sequence into a small Transformer encoder to learn latent interaction patterns between features.
- Build a similarity graph over the posts with cosine similarity on the feature vectors or learned embeddings.
- Run a small GNN/GCN over that graph to smooth noisy single-post signals and surface recurring psychological clusters.
- Interpret the latent axes in practical terms such as: `agency`, `epistemic_grounding`, `opposition`, and `self_reference`.
- Use clustering or nearest-centroid summaries to label recurring post modes, then decide which mode you want to amplify.

This is especially useful when several drafts have similar raw scores but different psychological signatures.

## Reference material
- See `references/psychological-feature-modeling.md` for a compact recipe and the session-derived axis mapping.

## Relationship to other skills
This skill is meant to pair with:
- `hermes-x-posting-workflows`
- `x-weekly-buzz-template-workflow`
- `ebbinghaus-memory`

Use it as the decision layer before posting or replying.
