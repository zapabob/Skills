---
name: company-deepresearch
description: "DeepResearch a company: reputation, compensation, SaaS products, and fundamentals."
version: 0.1.0
author: Hermes
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Research, DeepResearch, Company-Analysis, HRTech, SaaS]
    related_skills: [web-search, web-extract, browser-navigate]
---

# Company DeepResearch Skill

Perform structured DeepResearch on a target company to gather: employee reviews/reputation (OpenWork, Glassdoor), compensation data (salary ranges, by role), SaaS product portfolio and differentiators, and corporate fundamentals. Outputs a concise briefing memo.

**What it does NOT do**: financial modeling, legal due diligence, or primary data collection (surveys/interviews).

**Dependencies**: `web_search`, `web_extract`, `browser_navigate` (Hermes tools). No external API keys required.

## When to Use

- "DeepResearch [company name] 評判 年収 SaaS"
- "Company analysis for [target] — reputation, pay, products"
- "競合調査: [company] の口コミとプロダクト強みをまとめて"
- "HRTech/SaaS 企業の実態を把握したい"

## Prerequisites

- Hermes with web toolset enabled (`tools.web.enabled: true` in config.yaml)
- Internet access (no proxy/auth needed for public sites)
- Optional: Bitwarden entry for Glassdoor login if deeper review access needed

## How to Run

```python
# Via execute_code (recommended for orchestration)
from hermes_tools import web_search, web_extract, browser_navigate, browser_snapshot

# Or invoke step-by-step through Hermes chat:
# 1. web_search for reputation sources
# 2. web_search for compensation sources
# 3. web_search for product/SaaS sources
# 4. browser_navigate + browser_snapshot for key pages
# 5. web_extract for clean content from product sites
# 6. Synthesize into briefing memo
```

## Quick Reference

| Step | Tool | Target |
|------|------|--------|
| Reputation | `web_search` | `site:openwork.jp [company] 口コミ` |
| Reputation | `web_search` | `[company] Glassdoor 評判` |
| Compensation | `web_search` | `[company] 年収 平均年収 OpenWork` |
| Products | `web_search` | `[company] SaaS プロダクト 機能 特徴` |
| Products | `browser_navigate` | Company product site (e.g. `https://mikiwame.com/`) |
| Products | `web_extract` | Product page URLs |
| Fundamentals | `web_search` | `[company] 企業概要 設立 代表 従業員数` |

## Procedure

1. **Reputation & Reviews**
   - Search: `web_search(query="site:openwork.jp [company] 口コミ 評判", limit=10)`
   - Search: `web_search(query="[company] Glassdoor レビュー 評判", limit=5)`
   - Navigate OpenWork company page: `browser_navigate(url="https://www.openwork.jp/company.php?m_id=...")`
   - Capture: overall score, review count, category scores (働きがい, 風通し, 待遇等), verbatim excerpts
   - Note: Glassdoor often blocks bots; rely on OpenWork + secondary summaries

2. **Compensation Data**
   - Search: `web_search(query="[company] 年収 平均年収 OpenWork", limit=10)`
   - OpenWork salary page: `browser_navigate(url="https://www.openwork.jp/company_answer.php?m_id=...&q_no=2")`
   - Extract: 平均年収, 年収レンジ, 平均年齢, 回答者数, 職種別内訳
   - Cross-ref: doda, OpenMoney, 転職会議 for triangulation

3. **SaaS Product Portfolio**
   - Search: `web_search(query="[company] SaaS プロダクト 機能 特徴 強み", limit=10)`
   - Identify product site URL (e.g. `https://mikiwame.com/` for リーディングマーク)
   - `browser_navigate(url=product_site)` → `browser_snapshot(full=true)`
   - `web_extract(urls=[product_site, product_site+"/aptitude-test.html", ...])`
   - Map each product: name, one-liner, core differentiator, target user, pricing hint
   - Note: enterprise logos, case studies (e.g. "NTT東3万名導入")

4. **Corporate Fundamentals**
   - Search: `web_search(query="[company] 企業概要 設立 代表 従業員数 資本金", limit=5)`
   - Sources: Compalyze, マイナビ, Wantedly, コーポレートサイト会社概要
   - Extract: 設立年, 代表者, 本社所在地, 従業員数, 決算概要(公開されている場合), ミッション/ビジョン

5. **Synthesize Briefing Memo**
   - Structure per the output template (see Verification)
   - Include source URLs inline for traceability
   - Flag gaps (e.g. "Glassdoor inaccessible", "NRR非開示")

## Pitfalls

- **OpenWork pagination**: review lists paginate; capture first 2-3 pages for sentiment spread
- **Glassdoor bot detection**: often returns 403/redirect; do not rely on it as primary
- **Product site JS-heavy**: `web_extract` may return empty; use `browser_navigate` + `browser_snapshot` for SPA content
- **Salary data freshness**: OpenWork data lags 6-12 months; note "as of [date]" in memo
- **Language**: Japanese sources dominate for domestic companies; English sources sparse
- **Rate limits**: `web_search` ~30req/min; batch queries, add 2s sleep between batches

## Verification

Produce a briefing memo with these sections (all populated):

```markdown
## [Company Name] DeepResearch Brief

### 1. Reputation (OpenWork/Glassdoor)
- Overall: X.XX (rank: top Y%)
- Reviews: N件
- Key scores: 働きがい X.X, 風通し X.X, 待遇 X.X, 20代成長 X.X, 長期育成 X.X
- Verbatim themes: [positive], [negative]

### 2. Compensation
- 平均年収: XXX万円 (業界平均比 ±XXX万円)
- レンジ: XXX〜XXX万円
- 平均年齢: XX歳 / 回答者: XX名
- 職種別: [role] XXXX万円 (N名)

### 3. SaaS Products
| Product | One-liner | Differentiator | Evidence |
|---------|-----------|----------------|----------|
| ...     | ...       | ...            | URL      |

### 4. Fundamentals
- 設立: YYYY / 代表: [Name] / 本社: [Addr]
- 従業員: XXX名 / 決算: [summary]
- Mission: "..."

### 5. Competitive Positioning
| Axis | [Company] | Typical Competitor |
|------|-----------|-------------------|
| Core Value | ... | ... |
| Data Moat | ... | ... |
| Scope | Full-cycle | Point solution |

### 6. Gaps & Watch Items
- [ ] NRR/ARR 非開示
- [ ] Glassdoor 深層レビュー未取得
- [ ] チャーンレート 不明
```

Run complete when all 6 sections have ≥1 data point each.