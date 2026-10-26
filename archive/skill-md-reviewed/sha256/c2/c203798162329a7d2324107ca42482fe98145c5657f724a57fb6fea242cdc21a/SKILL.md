---
name: working-style-interview
description: Interview work style; save only the user's words.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Memory, Interview, Onboarding, Work-Style]
    category: memory
    related_skills: [omh-memory-new, ulw-interview]
---

# Working-Style Interview

Run a bounded interview so the agent learns how this user works. It does not plan, code, or change files or config. It writes only via the `memory` tool, in the user's words.

Do not use `ulw-interview` here. That skill is a 6-round product-clarity loop, not this 10-question work-style capture.

## When to Use

- 「働き方を知る必要がある。尋ねなさい、推測しないでください」
- 「My words, not yours」/ working-style interview / onboarding interview
- User wants habits, tools, conventions, stop-doing, or answer style saved to memory
- Do not use for product-feature clarification (`ulw-interview`) or a single fact (`omh-memory-new`)

## Prerequisites

- `memory` tool available
- Target `user` for preferences and working style
- Near-full `user` store is expected; plan one interview entry, not ten

## How to Run

Ask one question in the user's language. Wait. After each answer, write `memory` then quote the saved text. Stop after question 10. No files, no config, no extra questions.

## Quick Reference

- Cap: 10 questions, one per turn
- Skip: save nothing for that topic
- Write: `memory` only, target `user`
- Quote: show the exact stored entry after every write
- Replace: `content` is the full new entry, not a substring patch

## Procedure

1. Start at question 1. Do not batch questions. Do not guess answers from profile or past sessions.
2. Cover these topics, one thing per question, in this order (mirror the user's language):
   1. Reply language
   2. Preferred tool
   3. Coding / work convention to keep
   4. What to never do
   5. Short vs detailed answers
   6. Whether answers must include evidence (command output, URLs)
   7. Confirm-first vs execute-now
   8. On failure: stop-and-report vs continue with another approach
   9. Whether commit and push may be done without asking
   10. Code-comment language
3. Canonical Japanese bank used in the source run (use only if the user is in Japanese):
   1. 普段、私には日本語と英語のどちらで返してほしい？
   2. 作業で一番よく使ってほしいツールは何？
   3. 作業で守ってほしい慣習は何？
   4. 絶対にやめてほしいことは何？
   5. 回答は短くしてほしい？それとも詳しく？
   6. 回答にコマンド出力やURLなどの根拠は毎回つけてほしい？
   7. 作業は確認してから進める？それともすぐ実行してほしい？
   8. 失敗したらすぐ止めて報告？それとも別案で続ける？
   9. コミットとpushは任せていい？
   10. コードのコメントは日本語と英語、どちら？
4. After each answer, save with `memory`. Keep the user's wording. Do not paraphrase, infer, or fill skipped questions. Prefer one growing interview entry over many small ones.
5. After the write, show the stored interview entry verbatim, then ask the next question. After question 10, stop asking and show the final entry.
6. If the user says to skip a question, store nothing about it and continue.

Done when: 10 answers or skips are processed, `memory` holds only spoken answers, and the user has seen the exact entry text.

## Pitfalls

- `memory` `replace`: `old_text` identifies the entry; `content` replaces the whole entry. A short `content` wipes the rest of that entry.
- Do not shorten unrelated profile entries to make room. Merge this interview into one entry instead.
- A convention like `_docs` filenames is a preference to store, not a file to write during the interview.
- Do not write AGENT.md, MEMORY.md, skills, or config as part of this workflow.
- Do not import answers from existing profile memory. Ask.

## Verification

Confirm all three: no question 11 was asked; `memory` was the only write; the last message quoted the stored interview entry exactly.
