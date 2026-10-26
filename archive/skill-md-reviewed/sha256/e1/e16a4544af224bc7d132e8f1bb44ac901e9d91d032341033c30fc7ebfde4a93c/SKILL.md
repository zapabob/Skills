---
name: create-company-ai-employees
description: "Create a company-specific AI employee organization skill with tailored profiles, SOUL templates, and Hermes integration."
version: 0.1.0
author: Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [AI-Employee-Org, Kanban, Autonomous-Agents, Company-Research, Skill-Authoring]
    category: autonomous-ai-agents
    related_skills: [ai-employee-org, hermes-agent, company-deepresearch, openmanus-delegation, leadingmark-ai-employees]
---

# Create Company AI Employees Skill

Build a reusable skill that generates a **company-specific AI employee organization** — tailored profiles, SOUL templates, Kanban board, cron jobs, and full Hermes integration — based on company research (tech stack, org structure, products, culture).

**What it does**: Takes company DeepResearch output and produces a complete `hermes skills install`-able skill directory with 5–8 specialized profiles, each with a SOUL.md tuned to the company's domain, stack, and processes.

**What it does NOT do**: Run the agents, provision cloud infra, or replace human engineers. It only authors the skill artifact.

**Dependencies**: `company-deepresearch` skill (for research), `ai-employee-org` (base patterns), `skill_manage` (authoring). Stdlib + Hermes tools only.

## When to Use

- "Create AI employee org for [Company X] based on our research"
- "Generate LeadingMark-style skill for another HR Tech SaaS"
- "Bootstrap autonomous agent team matching a company's tech stack and org chart"
- "Turn DeepResearch brief into runnable Hermes skill"

## Prerequisites

- Hermes with `skill_manage` tool available
- `company-deepresearch` skill installed (for research phase)
- `ai-employee-org` skill installed (for base templates)
- Target company DeepResearch brief (Markdown with: tech stack, org structure, products, culture, metrics)
- Write access to `~/.hermes/skills/<category>/<skill-name>/`

## How to Run

```bash
# 1. Research the target company (if not done)
hermes skill company-deepresearch run --company "Target Company"

# 2. Invoke this skill authoring workflow
# Option A: Via execute_code (orchestrated)
hermes execute_code "$(cat scripts/create-company-ai-employees.py)"

# Option B: Step-by-step through chat using skill_manage
# (see Procedure below)
```

## Quick Reference

| Step | Tool | Output |
|------|------|--------|
| Research | `company-deepresearch` | `brief.md` |
| Analyze | `execute_code` / chat | profile list, stack mapping |
| Author SKILL.md | `skill_manage create` | skill skeleton |
| Write SOUL templates | `skill_manage write_file` | `templates/SOUL-*.md` |
| Verify | `skill_view` | loadable skill |

## Procedure

### 1. Gather Company Intelligence

Run DeepResearch to produce a structured brief:

```bash
# Using the company-deepresearch skill pattern
# Output: brief.md with sections:
# - tech_stack: {backend, frontend, infra, ml, data}
# - org_structure: {teams, roles, headcount, leadership}
# - products: [{name, domain, challenges}]
# - culture: {values, rituals, evaluation, autonomy}
# - metrics: {slo, cost_targets, velocity, quality_gates}
```

### 2. Map to AI Employee Profiles

Derive 5–8 profiles from org structure + tech stack:

| Source Signal | Profile | Example |
|---------------|---------|---------|
| ML team + model serving | `*-ai-engineer` | Inference, MLOps, GPU fleet |
| Research-heavy (ArXiv, experiments) | `*-ml-researcher` | Survey, experiment design, handoff |
| Platform/SRE/infra | `*-devops-engineer` | EKS, Terraform, observability, cost |
| Product engineering (FE/BE) | `*-product-engineer` | Rails/React, sprints, feature flags |
| Security/compliance focus | `*-security-engineer` | AppSec, DataSec, MLSec, audit |
| Orchestration/human interface | `*-secretary` | Triage, decompose, approvals |
| Continuous improvement | `*-self-improver` | Curator, memory, config drift |

**Rule**: One profile per distinct *accountability domain*, not per human role. Merge if same tools/cadence.

### 3. Author SKILL.md

```bash
skill_manage create \
  --name "<company-slug>-ai-employees" \
  --category "autonomous-ai-agents" \
  --content "$(cat <<'EOF'
---
name: <company-slug>-ai-employees
description: "AI employee roles tailored for <Company> <domain> engineering team."
version: 0.1.0
author: Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [<Company>, AI-Employee-Org, Kanban, Autonomous-Agents, <Domain>]
    category: autonomous-ai-agents
    related_skills: [ai-employee-org, hermes-agent, company-deepresearch, openmanus-delegation]
    profiles:
      - <profile-1>
      - <profile-2>
      # ... 5-8 total
EOF
)"
```

### 4. Write SOUL Templates (one per profile)

For each profile, create `templates/SOUL-<profile>.md` with:

```markdown
# <Profile Title> — <Japanese Role>

You <one-sentence mission>.

## Mission
- Bullet 1: core accountability
- Bullet 2: key deliverable
- Bullet 3: quality standard

## Execution
- **Stack**: exact technologies from brief
- **Tools**: `terminal`, `kanban`, `delegate_task`, `cron`, `web`
- **Cadence**: sprint / cron / event-driven
- **Definition of Done**: measurable gates

## Product-Specific Context (if applicable)
| Product | Key Technical Challenges |
|---------|-------------------------|
| ...     | ...                     |

## Collaboration
- Receives from: <other profiles>
- Sends to: <other profiles>
- Escalates: <conditions>

## Complete Metadata
```json
{
  "changed_files": [],
  "verification": "measurable success criteria",
  "deliverable": "concrete artifact"
}
```
```

### 5. Add Procedural Sections to SKILL.md

Append to SKILL.md:

- **How to Run**: bootstrap commands (profile create, skill install, SOUL copy, kanban init, cron install)
- **Quick Reference**: profile table with tools/cadence
- **Procedure**: work enters → completes → periodic autonomy
- **Pitfalls**: delegate_task not durable, WIP limits, one dispatcher
- **Verification**: checklist commands

### 6. Validate

```bash
hermes skill_view <company-slug>-ai-employees
hermes -p <profile> skills list | grep <company-slug>
hermes -p <profile> kanban list --status ready,running
```

## Pitfalls

- **Profile explosion**: >8 profiles creates coordination overhead. Merge adjacent domains.
- **Generic SOULs**: Every template must reference company-specific products, stack, metrics. No boilerplate.
- **Missing cron integration**: Each profile needs at least one cron job for autonomy.
- **Skill size**: Keep SKILL.md ~200 lines; large scripts → `scripts/`, references → `references/`.
- **Secret handling**: Never bake API keys. Document `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / etc. as prerequisites.

## Verification

Skill is valid when:

```bash
# All checks pass
hermes skill_view <skill-name>  # loads without error
hermes profile list | grep -c <prefix>  # returns profile count (5-8)
ls ~/.hermes/skills/.../templates/SOUL-*.md | wc -l  # matches profile count
grep -r "company-specific" ~/.hermes/skills/.../templates/  # finds product/stack refs
```

---

## Example Output: LeadingMark AI Employees

The skill we just created (`leadingmark-ai-employees`) demonstrates the pattern:

- **7 profiles** mapped from サービス開発部 + ML + infra + security + self-improvement
- **SOUL templates** each reference ミキワメAI products, Rails/Django/React stack, AWS EKS, 5000社データ, NTT東3万名導入
- **Kanban board** `lm-ai-company` with swimlanes per profile
- **Crons**: daily ArXiv scan, hourly health, weekly retro, daily standup digest
- **Integration**: `openmanus_wide_research`, `company_deepresearch`, `delegate_task`, `hyperframes`, `irodori TTS`