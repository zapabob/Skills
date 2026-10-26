---
name: cbd-thc-research-workflow
description: "CBD to THC conversion research workflow: academic literature gathering, catalyst screening, and safety boundaries for regulated chemistry research."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [chemistry, cbd, thc, research, regulated-substances, OpenManus, web-search]
    category: research
    related_skills: [regulated-chemistry-research-safety]
---

# CBD to THC Conversion Research Workflow

This skill documents a safe, academic-focused research workflow for studying CBD-to-THC conversion, emphasizing literature gathering, catalyst screening, and strict safety boundaries. It does not provide actionable synthesis conditions, quantities, or procedural details for THC production.

## When to Use

- Requests to review academic literature on CBD→THC conversion mechanisms
- Inquiry into catalyst screening (zeolites, acids, other materials) for qualitative comparison
- Assessment of isolation/purification methods as analytical concepts
- Framing research questions within regulated chemistry safety boundaries
- Redirecting users from actionable synthesis toward safe research scopes

## Prerequisites

- Access to academic databases (PubMed, arXiv, Google Scholar) via OpenManus or web_search
- Awareness that Japanese law (Cannabis Control Act, Marihuana Tax Law) classifies THC as a regulated substance
- Understanding that this skill serves academic/analytical research only
- Access to `web_search`, `web_extract`, and `openmanus_run` tools

## How to Run

### Through Hermes CLI

```bash
hermes chat -q "CBD to THC conversion academic review"
```

### Through OpenManus (bounded scope)

```python
openmanus_run({
  "agent_mode": "manus",
  "max_steps": 6,
  "task": "学術的観点からCBDからTHCへの変換メカニズムをレビューし、触媒・反応条件・分析手法の文献情報のみを収集。合成条件・定量的収率・器具仕様の詳細情報は含めない",
  "workspace": "cbd-thc-safe-research"
})
```

### Web search fallback

```bash
hermes web_search --query "CBD THC acid-catalyzed cyclization mechanism review"
```

## Quick Reference

| Topic | Safe Scope | Restricted |
|---|---|---|
| Reaction mechanism | Qualitative description of cyclization, activation, rearrangement | Quantitative conditions, temperatures, times, catalyst loadings |
| Catalyst screening | Names and general properties of ZSM-5, Beta, Y-type, etc. | Pore size effects on selectivity, optimal operating conditions |
| Isolation/purification | General concepts (extraction, distillation, chromatography principles) | Solvent systems, temperature parameters, purification sequences |
| Analytical methods | HPLC-UV, GC-MS, NMR as identification concepts | Specific column compositions, gradient conditions, quantification methods |
| Legal status | Jurisdictional references with dates | Procurement routes, home synthesis instructions |

## Procedure

### 1. Topic Classification

Classify the request: Is it asking for academic review, catalyst comparison, or actionable synthesis? Only proceed with academic/catalyst scopes.

### 2. Safe Literature Gathering

Use `web_search` with queries like:

- `CBD THC acid-catalyzed cyclization mechanism review`
- `zeolite catalyzed cannabinoid conversion literature`
- `Marzullo J Nat Prod 2020 THC synthesis review`

Collect results, then use `web_extract` on accessible sources (Wikipedia, open-access papers).

### 3. Catalyst Property Collection

Gather zeolite framework types, pore dimensions (Å), acid site characteristics from open sources. Note: pore sizes are structural data, not optimization conditions.

### 4. Safety Boundary Check

Before presenting any collected information:

- Confirm no reproducible synthesis sequence is included
- Verify no quantitative conditions (temp, time, catalyst %) that enable production
- Ensure any numbers cited are from regulatory or safety contexts only
- Explicitly note academic/analytical focus

### 5. Safe Redirection Offer

Offer two or three concrete safe scopes:

- Toxicology/pharmacology review
- Legal status by jurisdiction (with sources)
- Analytical detection method concepts
- General acid catalysis principles (textbook level)

## Pitfalls

- Treating "academic" or "for analysis" as sufficient justification for actionable synthesis requests
- Delegating to OpenManus without explicit bounded prompts
- Providing isolated reaction conditions that could be combined with external sources
- Interpreting "continue" after refusal as boundary-crossing permission
- Citing pore sizes or catalyst names without emphasizing they're structural, not operational
- Presenting purification concepts without noting they're analytical frameworks

## Verification

Before responding, confirm that the output contains:

- No reproducible synthesis sequence
- No quantities, temperatures, times, or catalyst loadings that enable THC production
- No solvent systems or purification sequences with operational parameters
- Clear academic/analytical framing with safety boundary statements
- Any OpenManus receipt inspected and cleaned of accidental detail

## Reference Files

- `references/zeolite-catalysts.md` — Zeolite framework types and pore dimensions (structural data only)
- `references/safe-redirection-examples.md` — Response patterns for boundary enforcement
- `references/legal-status-jurisdictions.md` — Cannabis regulations by jurisdiction with effective dates

## OpenManus Integration Notes

When using `openmanus_run` for this topic:

- Always set `agent_mode: manus` with `max_steps: 6`
- Include explicit instruction: "収集のみ、合成条件は含めない"
- Set `workspace: cbd-thc-safe-research`
- After completion, inspect receipt for accidental procedural detail and remove before presenting
- Prefer `openmanus_wide_research` only for independent safe topics (legal status, pharmacology)