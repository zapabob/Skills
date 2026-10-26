---
name: corporate-deepresearch
description: "Structured DeepResearch methodology for company reputation, compensation, SaaS product analysis, and competitive positioning."
version: 1.1.0
author: ボブにゃん
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [deepresearch, company-research, corporate-analysis, saas-analysis, compensation-research, competitive-intelligence]
    related_skills: [deepresearch-defense-standard, openmanus-delegation]
---

# Corporate DeepResearch Methodology

Structured approach for researching a target company's reputation, compensation, SaaS product portfolio, and market positioning. Use when the task needs primary-source-backed company intelligence.

## When to Use

- Company due diligence (investment, partnership, competitive analysis, job evaluation)
- SaaS vendor assessment (product capabilities, differentiation, customer traction)
- Compensation benchmarking for hiring or negotiation
- Market positioning analysis (strengths, weaknesses, traction signals)

## Core Workflow

### 1. Anchor the Research Objective
Define: target company (legal name + brand names), jurisdiction, timeframe for "current" data, and decision context (invest/partner/compete/hire).

### 2. Reputation & Employee Sentiment (Primary Sources First)
| Source | What to Extract | Priority |
|--------|----------------|----------|
| **OpenWork / Glassdoor / Indeed** | Overall score, category scores (culture, comp, WLB, leadership), review count, verbatim excerpts | Primary |
| **Wantedly / Greenhouse / Lever career pages** | Mission narrative, team structure, hiring velocity | Secondary |
| **LinkedIn Insights** (if accessible) | Headcount growth, tenure distribution, talent flow | Secondary |
| **News / PR** (PR Times, Nikkei, TechCrunch) | Funding, major customer wins, leadership changes, product launches | Tertiary |

**Key metrics to capture**: overall rating, review count, salary range by role, voluntary attrition signals (reviews mentioning "left", "resigned"), eNPS proxies.

### 3. Compensation & Total Rewards
| Source | What to Extract |
|--------|----------------|
| OpenWork 年収データ | 平均年収、レンジ、職種別、回答者数、平均年齢 |
| doda / 転職会議 / Glassdoor Salary | 役職・職種・年次別レンジ |
| 有価証券報告書 (EDINET) | 役員報酬、平均年間給与、従業員数推移 |
| 求人票 (Wantedly, Greenhouse, 企業サイト) | 提示年収レンジ、ストックオプション、手当 |

**Normalize**: Convert all to annual gross JPY. Note sample sizes and recency.

### 4. SaaS Product Portfolio Analysis
For each product/brand:
| Dimension | Sources |
|-----------|---------|
| **Positioning & Tagline** | Official product site, hero section, meta description |
| **Core Features** | Product pages, feature matrices, comparison pages, demo videos |
| **Differentiation Claims** | "Why us" pages, case studies, whitepapers, webinar content |
| **Pricing Model** | Pricing page, "請求書払い/従量/シート" disclosures, partner/analyst quotes |
| **Traction Signals** | Customer logos, "導入社数○万社", "○○グループ○万名採用", 導入事例数, セミナー開催頻度 |
| **Tech Stack / Integrations** | 開発者向けドキュメント、APIリファレンス、連携サービス一覧 |
| **Org Backing** | 研究所/ラボの有無、専門家アドバイザー、特許・論文 |
| **Engineering Culture** | Speaker Deck / tech blog / job postings (Paiza, Greenhouse, Wantedly) for tech stack, dev process, team structure, benefits |

### 4b. Engineering Organization DeepResearch (When Targeting AI/Engineering Roles)
Add these queries to the workflow:
| Dimension | Queries |
|-----------|---------|
| **Tech Stack** | `[company] 技術スタック Python TypeScript React AWS`, `site:speakerdeck.com [company] エンジニア 組織` |
| **Dev Environment** | `[company] 開発環境 CI/CD GitHub Actions Docker`, `[company] エンジニア 働きやすさ 裁量` |
| **Team Structure** | `[company] サービス開発部 組織 体制`, `[company] VPoE EM インタビュー` |
| **Engineering Brand** | `[company] テックブログ`, `site:paiza.jp [company] 求人`, `site:wantedly.com [company] エンジニア` |
| **Compensation (Eng-specific)** | `[company] エンジニア 年収 OpenWork`, `[company] 提示年収 ストックオプション` |

### 4c. Final Interview Preparation DeepResearch (When Preparing for Leadership/Final Round)

Add this dimension when the research is for a **final interview** (代表面接、役員面接). The goal shifts from "what's the company like" to "what will they ask and how do I prepare." Extract CEO philosophy, company pain points, and strategic challenges to anticipate deep questions.

| Dimension | Queries | What to Extract |
|-----------|---------|----------------|
| **CEO/Founder Philosophy** | `[CEO] インタビュー 経営哲学 思想`, `[CEO] 講演 登壇 PIVOT`, `site:note.com [CEO]`, `[CEO] 経営理念 ミッション` | Origin story, key phrases, leadership style, mission conviction; verbatim quotes for references |
| **Company Crisis History** | `[company] 組織崩壊 危機`, `[company] コロナ 売上 減少`, `[company] 事業 失敗 ピボット` | How the CEO explains past failures, values that emerged from crisis, resilience narrative |
| **Company Pain Points (Now)** | `[company] 組織課題 採用`, `[company] PMI 子会社 統合`, `[company] 上場 IPO 課題` | Current organizational growing pains; likely to come up as "what do you think about X" questions |
| **Competitive Edge (at depth)** | `[company] 競合 比較 差別化`, `[company] 強み 技術 データ`, `[company] 市場 ポジショニング` | What the CEO considers their unique advantage; be ready to discuss this with conviction |
| **Hiring Philosophy** | `[company] 採用 基準 求める人材`, `[CEO] 最終面接 聞きたいこと` | The traits/values the CEO personally screens for; these are red-flag questions |
| **Industry Thesis** | `HRテック 市場 動向 2025 2026`, `適性検査 AI パーソナライズ 将来` | The CEO's view on where the industry is going; you need a grounded opinion, not just agreement |

**CEOs often ask the same 3-4 questions at every final interview** — find their pattern:
- "Why do you want to work here?" (tests mission alignment, not flattery)
- "What do you think about our business direction?" (tests strategic thinking, not agreement)
- "Tell me about a time you took ownership of something hard" (tests 全部自分ごと / ownership culture)
- "What would you change if you joined tomorrow?" (tests fresh eyes vs. hubris)

**Synthesis output**: produce a briefing memo with:
- CEO's origin story and why it matters for culture
- 3-5 deep questions they are likely to ask, with grounded answer strategies
- Key quotes from the CEO to reference naturally in conversation
- The company's current "Chapter" (are they scaling? integrating an acquisition? prepping for IPO?)
- Your personal narrative alignment: connect your experience to their values

### 4d. Multi-Company IPO/PMI Case Study Analysis (Cross-Company Pattern Extraction)

**Trigger conditions**: "IPO preparation research", "compare HR tech companies' success/failure factors", "what can company A learn from B and C", pre-IPO strategic planning, investor/founder briefing for IPO timing decisions.

Requires primary-source research across 3-5 comparable companies. Use when the decision context involves **strategic sequencing** (IPO timing, market positioning, governance readiness).

#### Workflow

1. **Anchor the comparison frame**: Define the decision context (IPO preparation, investment thesis, competitive playbook), time horizon (pre-IPO, post-IPO, PMI phase), and key success metric (ARR growth, market cap trajectory, employee retention post-IPO, internal control maturity).

2. **Parallel company profiling**: For each company in scope, capture at minimum:
   - Founding story, years-to-IPO, pre-IPO funding history and valuation trajectory
   - IPO details: market (Mothers/Growth/Prime), public valuation vs private, first-day return
   - Post-IPO trajectory: how ARR/market cap evolved at years 1, 2, 3 post-listing
   - Identified challenges: organisational scaling events (people doubling), product quality incidents, internal control disclosures, SO/lockup controversies
   - Current state: listed, acquired, delisted, or MBO — and the root cause of that outcome
   - **Cite primary sources only**: IR materials (EDINET, IR-BANK, minkabu), business press (Nikkei, TechCrunch Japan, Business Insider), PR TIMES, and official company releases

3. **Cross-company theme matrix**: Build a structured comparison:
   | Theme | Company A | Company B | Company C | Cross-Cutting Pattern |
   |-------|-----------|-----------|-----------|----------------------|
   | Org scaling velocity | N→2N in 18mo | N→2N in 12mo | ... | Common: post-IPO hiring spree |
   | Culture dilution signal | ... | ... | ... | Emerges at 2× personnel |
   | Internal control maturity | J-SOX finding at Y+1 | ... | ... | Common: pre-IPO ≠ ready |
   | SO design mistake | ... | ... | ... | Excessive dilution / no cliff |
   | Lockup exit impact | ... | ... | ... | Symptom of misaligned incentives |
   - Mark each cell with confidence: **high** (cited in IR/audit), **medium** (analyst inference), **low** (speculative)

4. **Target-company gap analysis**: Compare the target company's current state against each identified pattern using the same dimensions. Rate readiness:
   - **P0** — gap that could block or delay IPO (security baseline, internal controls, governance structure)
   - **P1** — gap that erodes post-IPO value (engineering scalability, culture preservation, SO design)
   - **P2** — gap manageable post-IPO with plan (M&A capability, IR readiness, international expansion)

5. **Candidate skill mapping** (when research supports a hiring decision): Map candidate competencies to each priority gap using **primary evidence** of their work (OSS repos, PRs merged, blog posts, talk transcripts, public architecture decisions). Format:
   ```markdown
   | Gap | Priority | Candidate Skill Source | Expected Impact | Confidence |
   |-----|----------|----------------------|-----------------|------------|
   | Security governance | P0 | Contributed X feature to Y project, addressing Z | Reduced incident response time by ... | High (verified in source) |
   ```

6. **Synthesis output**:
   - Executive summary with 3-5 key takeaways for the target company
   - Per-company case study briefs (300-500 words each) with cited references
   - Cross-company pattern matrix
   - Target-company P0/P1/P2 action items with timeline (relative to target event, e.g. "IPO-3yr")
   - Candidate skill mapping table (if applicable)
   - Open questions / low-confidence areas

#### Pitfalls
- **Confusing correlation with causation**: note "associated with" vs "caused by" — a post-IPO stock drop may reflect market conditions, not operational failure
- **Survivor bias**: include companies that changed course (Kaonavi delisting, HRBrain PE exit) — their choices are as informative as "success" stories
- **Time-shifted context**: Company A's 2016 IPO market (Mothers boom) ≠ Company B's 2028 conditions (Growth market reforms, stricter governance rules)
- **Source asymmetry**: public companies (listed 7+ years) have richer IR data than pre-IPO companies — note confidence levels per dimension
- **Never fabricate a case study**: if a company lacks public data on a dimension, mark it as `not available` rather than inferring. Label "lower confidence" for any non-primary-source claim.

#### See also
- `references/ipo-pmi-case-study.md` — complete worked example: Japanese HR Tech IPO/PMI case study (Atrae, Kaonavi, HRBrain, i-plug, Bizreach/Persol Career) with cross-company pattern extraction and candidate skill mapping to a pre-IPO HR SaaS target company

### 5. Competitive Positioning
Build a 2×2 or feature matrix against 3–5 named competitors:
- Axes: e.g., "Specialization (Vertical vs Horizontal)" × "AI/ML Depth"
- Or: "Enterprise Readiness" × "Self-serve Velocity"
- Populate with primary sources only (vendor docs, third-party comparisons with citations)
- For M&A / Post-Merger Integration scenarios, extend this into a full PMI roadmap using `references/ma-integration-research.md` (3-phase plan with risk matrix, KPI dashboard, and Japanese HRTech-specific competitor mapping)

### 6. Synthesis Output Format
```markdown
## [Company] DeepResearch Summary (as of YYYY-MM-DD)

### Reputation Snapshot
- Overall: X.Y / 5.0 (N reviews, Source)
- Key strengths: [verbatim themes with citations]
- Key concerns: [verbatim themes with citations]
- Attrition signals: [count/tenure mentions]

### Compensation Benchmark
| Role | Median | Range | Sample | Source | Date |
|------|--------|-------|--------|--------|------|
| ...  |        |       |        |        |      |

### Product Portfolio
| Product | Positioning | Key Differentiator | Traction Signal | Pricing Hint |
|---------|-------------|-------------------|-----------------|--------------|
| ...     |             |                   |                 |              |

### Competitive Positioning
[Matrix or narrative with citations]

### Residual Risk / Unknowns
- [What primary sources are missing]
- [Where sources disagree]
```

## Tooling & Fallback Patterns

### Primary: OpenManus Delegation (`openmanus_wide_research`)
```python
items = [
  "company reputation reviews OpenWork Glassdoor",
  "company salary compensation 年収 平均年収",
  "company product SaaS features pricing differentiation",
]
workspace = "<configured_openmanus_root>/<task_slug>"
```
**Pitfall**: If `workspace escapes the configured OpenManus workspace root`, the OpenManus plugin has a fixed allowed root. Discover it via `openmanus_capabilities` or plugin config. **Do not guess paths.**

### Fallback: Direct Hermes Web Research
When OpenManus is unavailable or blocked:
1. `web_search` with targeted queries (site:openwork.jp, site:glassdoor.com, "会社名 年収", "サービス名 機能")
2. `browser_navigate` + `browser_snapshot` for official product pages
3. `web_extract` for article/content extraction
4. `terminal` + `curl` for HTML when browser tools fail (502, bot detection)
5. Synthesize with `execute_code` or direct reasoning

**Always cite primary sources inline** (URL + access date).

## Source Priority for Corporate Research
1. **Official filings** (EDINET 有価証券報告書, 登記情報)
2. **Official product sites** (pricing, features, case studies, API docs)
3. **Employee review platforms** (OpenWork, Glassdoor, Indeed) — aggregate, not anecdote
4. **Reputable business media** (Nikkei, Toyo Keizai, TechCrunch, PR Times)
5. **Analyst/Comparison sites** (BOXIL, ITreview, G2, Capterra) — secondary only
6. **LinkedIn/Wantedly** — structural signals (headcount, hiring), not opinion

## Red Flags
- Single Glassdoor review quoted as "the truth"
- Salary data without sample size or date
- Product claims without demo/docs/customer reference
- "Market leader" without TAM/share citation
- No primary source for a material claim → label "lower confidence"

## Verification Checklist
- [ ] Every material claim has a primary-source citation (URL + date accessed)
- [ ] Salary data includes: source, N, date, role granularity
- [ ] Product claims traced to vendor doc or demo
- [ ] Competitive matrix cites sources per cell
- [ ] Disagreements between sources explicitly noted
- [ ] "Unknowns" section lists gaps for follow-up

## References
- `references/ma-integration-research.md` — M&A / PMI integration research workflow: 3-phase integration roadmap structure, competitive mapping for post-acquisition analysis, Japanese HRTech competitor profiles, risk matrix construction, and source discovery patterns for Japanese M&A intel
- `references/openmanus-workspace-pitfall.md` — OpenManus workspace root discovery and fallback pattern
- `references/company-research-query-templates.md` — Reusable search query templates by research dimension
- `references/engineering-org-deepresearch.md` — Engineering org/AI role specific query templates and metrics
- `references/interview-preparation-research.md` — Final-interview prep research workflow: CEO philosophy mining, question anticipation, company pain-point mapping
- `references/leading-mark-case-study.md` — Leading Mark company-specific case study (reputation, product, compensation, IPO readiness context)
- `references/ipo-pmi-case-study.md` — Japanese HR Tech IPO/PMI multi-company case study: cross-company analysis of Atrae, Kaonavi, HRBrain, i-plug, Bizreach/Persol Career. Covers 6 IPO/PMI challenge themes (org scaling, quality, culture dilution, internal controls, SO design, lockup), target-company gap analysis, and candidate skill mapping. See section 4d for the methodology that produced this reference.