---
name: japanese-tech-career-documents
description: Rewrite, review, and polish Japanese tech career documents — 履歴書, 職務経歴書, cover letters, agent messages, and interview-ready summaries — for Japanese companies, recruiters, freelance agents, and AI/LLM engineering roles.
tags:
  - japanese
  - career
  - resume
  - rirekisho
  - shokumukeirekisho
  - cover-letter
  - tech-recruiting
  - ai-engineer
  - freelance-agent
---

# Japanese Tech Career Documents

Use this skill when the user asks to review, rewrite, polish, localize, or optimize Japanese career documents such as 履歴書, 職務経歴書, カバーレター, LinkedIn summaries, recruiter messages, or agent-facing desired-condition notes.

This skill is especially relevant for Japanese companies, recruiting agents, freelance agents such as レバテック, and AI Engineer / AI Architect / LLM / AI coding-agent workflow positioning.

## Core principle

Japanese recruiting documents must be **specific, credible, and easy to match to案件**. Avoid both extremes:

- Too generic / AI-written: impressive words but little evidence.
- Too eccentric / over-branded: hard for agents to map to available roles.

Convert abstract claims into concrete, recruiter-readable evidence:

- What was built
- What problem it solved
- What technologies were used
- What scope/responsibility the candidate owned
- What result or operational improvement followed
- What kind of案件/company the experience maps to

## Workflow

1. **Identify document type and audience**
   - 履歴書: concise profile, dates, credentials, employment/education consistency.
   - 職務経歴書: project history, responsibilities, stack, achievements, self-PR.
   - カバーレター: motivation, role fit, selected evidence, next action.
   - Agent message: short, searchable desired conditions and selling points.
   - LinkedIn profile: stronger branding is acceptable, but still needs evidence.

2. **Extract or request source text**
   - If the document is a PDF/image, use an OCR/document extraction skill/tool first when available.
   - Preserve factual details. Do not invent employers, metrics, certifications, or production experience.
   - If metrics are missing, add placeholders/questions rather than fabricating numbers.

3. **Check consistency across documents**
   - Names, dates, role titles, languages, technologies, project descriptions.
   - Ensure 履歴書 summary, 職務経歴書 projects, and cover letter all support the same positioning.

4. **Remove generic AI prose**
   Watch for phrases like:
   - 革新的なソリューションを提供
   - 最先端技術を駆使
   - 高度なアーキテクチャを設計
   - ビジネス価値を最大化
   - シームレスな連携を実現

   Replace with specific wording:
   - 「Python/FastAPIで○○を実装」
   - 「LLM APIを用いて問い合わせ分類を自動化」
   - 「Cursor/Claude Code等を使った実装・調査・レビュー補助フローを構築」
   - 「既存手順をスクリプト化し、手作業を削減」

5. **Optimize for Japanese recruiters and agents**
   Agents need matching keywords and constraints. Make these easy to find:
   - 希望職種
   - 稼働開始時期
   - 稼働率 / 常駐可否 / リモート希望
   - 希望単価 or 年収レンジ if user provides it
   - 使用技術
   - 得意領域
   - NG条件
   - AI活用への希望度

6. **Optimize for AI coding-agent / AI-native development roles**
   Do not only say「AIを使えます」. Emphasize team/process value:
   - AIコーディングエージェント活用
   - 開発自動化
   - developer productivity
   - LLM API / RAG / MCP / agentic workflow
   - prompt/workflow design
   - test/review/CI integration for AI-generated code
   - documentation and reproducible workflows

   Good agent-facing phrasing:

   ```text
   AIコーディングエージェントを開発フローに取り入れている、または導入に前向きな現場を希望しています。Cursor、Claude Code、Codex、GitHub Copilot、MCP、RAG、LLM API などを活用し、開発効率化や自動化に関わる案件を優先したいです。単なるAI利用可ではなく、チームとしてAI活用を推進している環境を重視しています。
   ```

7. **Calibrate tone for Japanese business context**
   - Use confident but grounded wording.
   - Avoid excessive claims like「世界最高」「圧倒的」「完全自律」unless substantiated and appropriate.
   - Prefer「経験があります」「関心があります」「推進できます」「設計・実装に携わりました」depending on evidence strength.
   - For speculative or self-study work, label it honestly as 個人開発, 検証, PoC, or 学習・研究.

8. **Produce useful deliverables**
   Depending on the request, provide:
   - Redline-style review comments.
   - Rewritten Japanese version.
   - Stronger but conservative version for agents.
   - More branded version for LinkedIn.
   - Short recruiter message.
   - 面談で話す30秒/60秒自己紹介.
   - Open questions needed to quantify results.

   When the user asks to "全て作成" or "ワークフロー組んで", do not stop at advice or ask for another confirmation. Create a complete artifact set: review/strategy, resume rewrite, career-history rewrite, cover-letter rewrite, recruiter message templates, and a reusable workflow file. Keep original files unchanged and write clearly named Markdown outputs.

## Review checklist

- Is each claim backed by a project, tool, metric, or concrete action?
- Can a recruiter quickly identify matching案件?
- Are AI/LLM terms understandable to non-specialist recruiters?
- Are self-study and production experience clearly distinguished?
- Are dates and titles consistent across all documents?
- Is the document too verbose for Japanese screening?
- Does the first page communicate the strongest positioning?
- Does it avoid generic GPT-like phrasing?

## User-specific preference notes

For ボブにゃん, prefer Japanese guidance and career-document edits that position him toward AI Engineer / AI Architect work, especially companies or案件 that actively use AI coding agents and AI-native development workflows. He values removing generic AI-written phrasing while keeping the documents suitable for Japanese companies and recruiting agents such as レバテック.

## References

- `references/agent-ai-coding-positioning.md`: reusable Japanese wording for AI coding-agent / AI-native development positioning in recruiter messages and career documents.
- `references/bob-career-docs-workflow.md`: session-derived workflow and artifact map for ボブにゃん's resume/career-history/cover-letter rewrite package, including the `career_docs_output` files and LevTech positioning notes.
- `references/japanese-agent-doc-workflow.md`: full 3-document workflow for extracting, reviewing, rewriting, and packaging 履歴書・職務経歴書・カバーレター outputs for Japanese recruiters/agents.
- `references/hermes-agent-contribution-evidence.md`: session-verified evidence and conservative Japanese wording for ボブにゃん's `zapabob` Hermes Agent OSS contribution claims.
