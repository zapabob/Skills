---
name: leadingmark-ai-employees
description: "AI employee org for 株式会社リーディングマーク: 7 specialized profiles with SOUL templates, kanban, crons, and Hermes integration."
version: 0.1.0
author: Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LeadingMark, AI-Employee-Org, Kanban, Autonomous-Agents, HRTech]
    category: autonomous-ai-agents
    related_skills: [ai-employee-org, hermes-agent, company-deepresearch, openmanus-delegation, hyperframes-hakua-video]
    profiles:
      - lm-secretary
      - lm-ai-engineer
      - lm-ml-researcher
      - lm-devops-engineer
      - lm-product-engineer
      - lm-security-engineer
      - lm-self-improver
---

# LeadingMark AI Employees Skill

Seven specialized Hermes profiles operating as an autonomous AI company inside 株式会社リーディングマーク, leveraging the full Hermes stack (kanban, openmanus, cron, delegation, curator, hyperframes, ai-employees plugin).

## When to Use

- Bootstrapping a full AI development team for ミキワメAI product suite
- Running parallel: ML research, model serving, product engineering, DevOps, security, self-improvement
- Structured handoffs via kanban with durable audit trails
- Periodic autonomous work via cron (digests, scans, retrospectives)
- Human-in-the-loop for approvals (external posts, budget, compliance)

## Prerequisites

- Hermes with gateway running (`hermes gateway run` or service)
- API keys in `~/.hermes/.env` (OpenAI, Anthropic, NVIDIA, etc.)
- Kanban dispatcher enabled in gateway profile (`kanban.dispatch_in_gateway: true`)
- Telegram bot token + chat ID for delivery (optional but recommended)
- Optional: `hermes plugins enable ai-employee-org` for CLI bootstrap

## How to Run

### 1. Create profiles and install skill

```bash
# Create all 7 profiles
for p in lm-secretary lm-ai-engineer lm-ml-researcher lm-devops-engineer lm-product-engineer lm-security-engineer lm-self-improver; do
  hermes profile create $p --description "$(hermes skill leadingmark-ai-employees read templates/SOUL-$p.md | head -3 | tail -1)"
done

# Install this skill into each profile
for p in lm-secretary lm-ai-engineer lm-ml-researcher lm-devops-engineer lm-product-engineer lm-security-engineer lm-self-improver; do
  hermes -p $p skills install official/autonomous-ai-agents/leadingmark-ai-employees
done
```

### 2. Copy SOUL templates to each profile home

```bash
# From this skill's templates/ directory
for p in lm-secretary lm-ai-engineer lm-ml-researcher lm-devops-engineer lm-product-engineer lm-security-engineer lm-self-improver; do
  cp templates/SOUL-$p.md ~/.hermes/profiles/$p/SOUL.md
done
```

### 3. Create kanban board and initialize

```bash
hermes -p lm-secretary kanban boards create lm-ai-company --name "LeadingMark AI Company" --switch
hermes -p lm-secretary kanban init
```

### 4. Enable dispatcher on gateway profile only

In `~/.hermes/config.yaml` (gateway profile):

```yaml
kanban:
  dispatch_in_gateway: true
  orchestrator_profile: lm-secretary
delegation:
  max_async_children: 5
  max_concurrent_children: 3
curator:
  enabled: true
```

### 5. Install role-specific crons

```bash
# Secretary: daily standup digest
hermes -p lm-secretary cron create "every weekday 8:30" -q "Read kanban board lm-ai-company; summarize blocked/ready/running; post to Telegram; create follow-up tasks for blockers."

# AI Engineer: model health check
hermes -p lm-ai-engineer cron create "every 6h" -q "Check inference endpoints health (latency, error rate, GPU util); kanban_block on SLO breach; report to lm-devops-engineer."

# ML Researcher: daily ArXiv scan
hermes -p lm-ml-researcher cron create "every weekday 8am" -q "Scan ArXiv cs.LG, cs.CL, stat.ML last 24h; openmanus_wide_research top 3 by relevance to personality prediction/wellbeing/LLM-as-judge; kanban_create experiment cards for lm-ai-engineer."

# DevOps Engineer: hourly health + daily cost
hermes -p lm-devops-engineer cron create "hourly" -q "Run health check script; kanban_block on anomaly; kanban_create remediation task."
hermes -p lm-devops-engineer cron create "daily 9am" -q "AWS cost anomaly scan; forecast vs budget; post summary to Telegram."

# Product Engineer: sprint heartbeat
hermes -p lm-product-engineer cron create "every weekday 10am" -q "kanban_heartbeat on assigned tasks; update story points; flag scope creep to lm-secretary."

# Security Engineer: daily vuln scan + weekly secret audit
hermes -p lm-security-engineer cron create "daily 6am" -q "Run Trivy/Semgrep/Dependabot scan; kanban_create critical/high findings with 7d SLA."
hermes -p lm-security-engineer cron create "weekly monday 9am" -q "Secret rotation audit (IAM keys, DB passwords, API tokens); kanban_block on stale secrets."

# Self-Improver: weekly retrospective
hermes -p lm-self-improver cron create "sunday 18:00" -q "Run hermes curator status; archive stale agent skills; write _docs/YYYY-MM-DD_self-review.md; kanban_create improvement proposals."
```

### 6. Start gateway

```bash
hermes gateway run
```

### 7. Submit work

Talk to `lm-secretary` via CLI/Telegram or create tasks directly:

```bash
hermes -p lm-secretary kanban create "新機能: AIコーチ会話履歴エクスポート" \
  --assignee lm-secretary --priority 1 \
  --body "要件: ユーザーが過去のコーチング履歴をPDF/CSVで出力可能にする。GDPR対応含む。"
```

Secretary decomposes → routes to `lm-product-engineer` (FE/BE), `lm-ai-engineer` (export logic), `lm-security-engineer` (DPIA), `lm-devops-engineer` (preview env).

## Quick Reference

| Role | Profile | Primary Tools | Cadence |
|------|---------|---------------|---------|
| 秘書（オーケストレーター） | `lm-secretary` | kanban, delegation orchestrator | Always-on via gateway |
| AIエンジニア（推論・MLOps） | `lm-ai-engineer` | terminal, kanban, delegate_task, openmanus | Kanban `ready` queue + cron health |
| MLリサーチャー | `lm-ml-researcher` | web, openmanus_wide_research, company_deepresearch | Cron daily scan + kanban |
| DevOpsエンジニア | `lm-devops-engineer` | terminal (aws/tf/helm), kanban, cron | Hourly health + daily cost |
| プロダクトエンジニア | `lm-product-engineer` | terminal (rails/yarn), kanban, delegate_task | 2-week sprints + daily heartbeat |
| セキュリティエンジニア | `lm-security-engineer` | terminal (semgrep/trivy), kanban, cron | Daily scan + weekly audit |
| 自己改善エージェント | `lm-self-improver` | curator CLI, skills, memory, kanban | Weekly deep review |

## Procedure

### Work Enters

1. Human or webhook posts to `lm-secretary` session OR `hermes -p lm-secretary kanban create` with `--assignee lm-secretary`.
2. Secretary reads `kanban_show`, comments routing intent, creates child tasks with `kanban_create` + `kanban_link`.
3. Dispatcher spawns the assignee profile every ~60s (or Nudge in dashboard).

### Work Completes

1. Worker calls `kanban_complete(summary=..., metadata={...})`.
2. Parent task promotes when dependencies are `done`.
3. Secretary reviews parent; archives or opens follow-ups.

### Periodic Autonomy (cron)

See "How to Run" step 5. Each profile runs its own cron jobs with `skip_memory=True` by default. Use `script` + `workdir` for fixed ops directories.

### Async Subagent Research

Inside a worker turn, for quick parallel research:

```python
delegate_task(
    goal="競合3社のAIコーチ機能比較（Pymetrics, Eightfold, HireVue）",
    context="ミキワメAI AIコーチの差別化ポイント策定用。価格・精度・導入実績・API有無。",
    toolsets=["web", "file"],
    background=true,
)
```

## Pitfalls

- **`delegate_task` is not durable** — parent interrupt cancels children. Use Kanban for work that must survive restarts.
- **`background=true` is single-task** — no batch async delegation. Use `openmanus_wide_research` for parallel research.
- **Scratch workspaces are deleted on complete** — use `dir:<abs path>` for deliverables you need to keep.
- **One dispatcher gateway** — other profiles set `kanban.dispatch_in_gateway: false`.
- **Subagents know nothing** — pass full context in `goal` and `context`.
- **Claude Code full-org license** — LeadingMark has enterprise; configure `ANTHROPIC_API_KEY` per profile or use gateway model routing.

## Verification

```bash
# Check all profiles exist
hermes profile list | grep lm-

# Check skill installed
for p in lm-secretary lm-ai-engineer lm-ml-researcher lm-devops-engineer lm-product-engineer lm-security-engineer lm-self-improver; do
  hermes -p $p skills list | grep leadingmark-ai-employees
done

# Check kanban board
hermes -p lm-secretary kanban list --status ready,running,blocked

# Check crons
for p in lm-secretary lm-ai-engineer lm-ml-researcher lm-devops-engineer lm-product-engineer lm-security-engineer lm-self-improver; do
  hermes -p $p cron list
done

# Gateway status
hermes gateway status

# Dashboard
hermes dashboard  # → Kanban tab
```

Expected: 7 profiles, skill linked, board `lm-ai-company` active, 5+ crons per profile, dispatcher running on gateway profile.