---
name: twitter-post-writing
description: Compose X/Twitter post copy under strict character limits for technical products. Use when the user asks for social post drafts, buzz-focused variants, engineer-focused messaging, enterprise adoption messaging, or requests 139/140-character Japanese post optimization with URL inclusion.
---

# Twitter Post Writing

## Purpose

Create high-impact X/Twitter post drafts for technical products, especially AI/LLM tools, with explicit character constraints and target audience tuning.

## Trigger Conditions

Apply this skill when the user asks for:

- X/Twitter向け投稿文
- 文字数制限付きコピー（例: 139字以内）
- バズ狙い版、技術者向け、企業導入向けの複数パターン
- リポジトリURL入りの紹介文

## Workflow

1. Clarify input assets:
   - product name
   - value proposition
   - target persona
   - required URL
   - character limit
2. Draft 3 variants by default:
   - buzz-oriented
   - technical/deep-engineer
   - enterprise/adoption
3. Verify length:
   - run `py -3` for script-based checks
   - optionally double-check with shell string length
4. Return compact output:
   - each variant labeled
   - character count shown
   - final recommended one highlighted

## Style Rules

- Keep one core benefit per sentence.
- Put the strongest keyword early (`RTX30`, `CUDA12`, `Ollama互換API`, etc.).
- Avoid vague hype; keep claims concrete.
- Include URL once at the end unless user asks otherwise.
- Prefer plain UTF-8 Japanese for JP posts.

## Output Template

Use this format:

```markdown
1) よりバズ狙い版（XXX字）
`...`

2) 技術ガチ勢版（XXX字）
`...`

3) 企業導入訴求版（XXX字）
`...`

推奨案:
`...`
```

## Length Check Snippet

Use `py -3`:

```bash
py -3 -c "posts=['...','...','...'];[print(i+1,len(p),p) for i,p in enumerate(posts)]"
```
