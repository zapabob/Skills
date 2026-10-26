---
name: codex-evolution-fluency
description: Use when designing or operating Codex/Hermes long-running agent workflows that should get smarter with use while staying fast and smooth via retrospective learning and safe session archival.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [codex, ai-agent, retrospective, skills, session-handoff, fluency, memory]
    related_skills: [codex, agent-memory-consolidation, agent-memory-systems]
---

# Codex Evolution + Fluency

## Overview

Use this skill to keep a long-running Codex-style AI agent both **smarter over time** and **smooth to operate**.

The core pattern combines two complementary capabilities:

1. **`codex-retrospective`** — intelligence evolution. Codex periodically reviews the past few weeks of conversation history, makes minimal updates to `AGENTS.md`, and extracts only genuinely reusable, small skills.
2. **`codex-fluent`** — runtime fluency. Codex prevents long-lived sessions from becoming heavy and slow by forcing a handoff, then safely archiving old sessions into isolated directories instead of deleting them directly.

Together, they separate two concerns that often get mixed together:

- **Learning:** preserve reusable patterns, lessons, and project conventions.
- **Fluency:** keep startup, context loading, and session operations fast.

## When to Use

Use this skill when:

- Codex/Hermes has been used for days or weeks and valuable habits are scattered across conversations.
- You want the agent to become more capable without dumping large transcripts into memory.
- Sessions, logs, or startup state are getting heavy and slowing down the agent.
- You need a safe maintenance workflow before archiving or pruning old sessions.
- You want to explain the design publicly: "one skill evolves intelligence, one skill preserves fluency."

Do **not** use this skill for:

- One-off tasks with no durable learning value.
- Blind deletion of session history.
- Adding broad, vague, or project-specific trivia to `AGENTS.md`.
- Extracting skills from unverified or failed workflows.

## The Two-Skill Model

### `codex-retrospective`: Intelligence Evolution

Purpose: make the agent **smarter the longer it is used**.

Expected behavior:

1. Review recent conversation history, typically the past few weeks.
2. Identify recurring corrections, successful workflows, repeated setup steps, and durable project conventions.
3. Update `AGENTS.md` with the **smallest possible diff**.
4. Extract small, reusable skills only when the workflow is likely to recur.
5. Avoid preserving temporary task progress, stale artifact IDs, or noisy transcripts.

Good retrospective outputs:

- A short new rule in `AGENTS.md` that prevents repeated user correction.
- A compact skill for a workflow that required multiple steps and is likely to recur.
- A removed or tightened instruction that was causing drift.

Bad retrospective outputs:

- Large transcript summaries.
- Temporary TODO state.
- PR numbers, issue numbers, commit SHAs, or stale task completion logs.
- Broad personality changes not grounded in repeated user preference.

### `codex-fluent`: Runtime Fluency

Purpose: keep the agent **smooth even after long-term use**.

Expected behavior:

1. Detect when sessions or local state are making startup or interaction slow.
2. Force a handoff before archival so active context is not lost.
3. Archive old sessions into a safe, independent directory.
4. Do **not** directly delete sessions as the first step.
5. Preserve enough metadata to recover or inspect archived sessions later.

Safe archival principles:

- Handoff first, archive second.
- Archive to a timestamped or clearly named directory.
- Keep archives outside active session-loading paths if the goal is startup speed.
- Prefer move/copy with verification over destructive cleanup.
- Delete only after explicit confirmation and backup verification.

## Sleep-Time Activation Pattern

This skill works best when it runs during an agent sleep/idle maintenance window together with an Ebbinghaus-style memory cycle.

Recommended pairing:

1. **Ebbinghaus decay/rehearsal pass** decides which memories are still important, which should be rehearsed, and which low-value traces should be forgotten.
2. **`codex-retrospective` pass** reviews surviving high-signal sessions and promotes only stable lessons into `AGENTS.md` or small reusable skills.
3. **`codex-fluent` pass** creates a handoff, then archives old/heavy sessions so the next wake starts smooth.
4. **Wake report** summarizes what was rehearsed, what was promoted to skill/AGENTS.md, and what was archived — without exposing secrets or raw transcripts.

Conceptually:

- Ebbinghaus handles **retention and forgetting**.
- `codex-retrospective` handles **intelligence evolution**.
- `codex-fluent` handles **runtime fluency**.

A nightly/idle job should be self-contained, should not recursively schedule more jobs, and should avoid destructive deletion. Archive first; prune only after verification and explicit policy.

## Operating Workflow

### 1. Sleep/idle trigger

Start only when the user is inactive or during a configured low-activity window. Prefer an idle-aware cron/scheduler configuration so retrospective work does not compete with active interaction.

Checklist:

- [ ] Confirm the sleep window or idle condition is active.
- [ ] Run Ebbinghaus decay/rehearsal first if available.
- [ ] Do not mutate `AGENTS.md`, skills, or archives while an active task is in progress.

### 2. Retrospective pass

Run this when the agent has accumulated useful experience and the sleep/idle trigger has fired.

Checklist:

- [ ] Search or inspect recent sessions.
- [ ] Group findings into reusable lessons vs. temporary noise.
- [ ] Patch `AGENTS.md` only for stable, high-signal guidance.
- [ ] Create small skills for recurring procedures.
- [ ] Verify that no stale task progress or raw transcript dump was saved.

### 2. Handoff pass

Before archiving sessions, create a handoff summary.

A good handoff includes:

- Current project or mission.
- Active decisions and constraints.
- Where important artifacts live.
- Open risks or next steps.
- Which archived sessions may matter later.

It should **not** include every message or every tool output.

### 3. Fluency/archive pass

After handoff:

- Move old sessions into an isolated archive directory.
- Keep the active session set small.
- Verify that the agent can still start quickly.
- Verify that archived content can still be searched or restored if needed.

### 4. Wake-up verification

After archival or retrospective changes:

- Start a fresh session.
- Confirm `AGENTS.md` still loads correctly.
- Confirm the new skills are discoverable in the next session.
- Confirm startup/session switching feels faster.
- Ask whether the new behavior actually reduced user steering.

## Suggested Public Explanation

Use this framing when explaining the pattern in Japanese:

```text
一つは使えば使うほど賢くなるようにするもの、もう一つは常にスムーズさを保つものです。

codex-retrospective は、Codex が定期的に過去数週間の会話履歴を自分でレビューし、最小限の変更で AGENTS.md を更新し、本当に再利用可能な小さな skill を抽出できるようにします。

codex-fluent は、もう一つの痛点に特化しています。長く使っているとセッションが重くなり、起動が遅くなる問題です。まず handoff を強制し、古いセッションを直接削除するのではなく、安全に独立したディレクトリへアーカイブします。

この2つの skill を組み合わせると特に相性がいい。一つは知能の進化を、もう一つは流暢さの維持を担当します。
```

Shorter X-ready version:

```text
AI Agent の長期運用では「賢く育つこと」と「重くならないこと」の両方が重要。

codex-retrospective は過去数週間の会話履歴をレビューし、AGENTS.md の最小更新と小さな reusable skill 抽出を担当。

codex-fluent は handoff 後に古いセッションを安全に独立ディレクトリへアーカイブし、起動や操作の流暢さを保つ。

一つは知能の進化、もう一つは流暢さの維持。
```

## Common Pitfalls

1. **Retrospectiveが肥大化する。** 目的は巨大な記憶保存ではなく、最小限の再利用可能な差分を残すこと。

2. **AGENTS.mdに一時情報を書く。** タスク進捗、PR番号、issue番号、commit SHA、完了ログはすぐ古くなる。保存しない。

3. **handoffなしでアーカイブする。** 古いセッションを隔離する前に、現在の作業継続に必要な要約を必ず作る。

4. **削除を先に行う。** `codex-fluent` の基本は delete ではなく archive。削除はバックアップと復元確認後の別判断。

5. **skillを大きくしすぎる。** 再利用可能な小さな skill を抽出する。1 skill = 1 recurring workflow を目安にする。

6. **知能進化と速度改善を混ぜる。** `codex-retrospective` は learning、`codex-fluent` は operational hygiene。責務を分ける。

## Verification Checklist

- [ ] sleep/idle window 中に発動し、 active task と競合していない。
- [ ] Ebbinghaus decay/rehearsal が先に走り、保持・強化・忘却候補が整理されている。
- [ ] `AGENTS.md` の変更は最小限で、安定したルールだけになっている。
- [ ] 新規 skill は小さく、再利用可能で、発火条件が明確。
- [ ] handoff summary が存在し、次セッションが作業を再開できる。
- [ ] 古いセッションは削除ではなく、独立ディレクトリへ安全にアーカイブされた。
- [ ] アーカイブ後も必要な情報を復元または検索できる。
- [ ] 新しいセッションの起動・操作が軽くなった。
- [ ] ユーザーの追加説明や訂正が実際に減った。
