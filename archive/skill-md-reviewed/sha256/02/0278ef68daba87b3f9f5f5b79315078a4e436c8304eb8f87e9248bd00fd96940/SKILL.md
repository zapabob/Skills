---
name: pitch-deck
description: "Create investor-grade fundraising pitch decks (.pptx) using officecli. Seed/Series A-C / SAFE / convertible / strategic raises. NOT for sales, product, or board decks (route those to pptx)."
version: "1.0.0"
---

# Pitch Deck Skill (officecli)

Use this skill when the user wants to create a **fundraising pitch deck** — equity/SAFE/convertible/strategic raise. This skill encapsulates the narrative structure, slide sequence, and officecli patterns that produce investor-ready decks.

## When to use
- Seed / Series A / B / C / D fundraising decks
- SAFE or convertible note round materials
- Strategic / corporate round decks
- **NOT** for: sales decks, product demos, board reviews, all-hands (use `pptx` skill instead)

## Narrative structure (standard 10-14 slide sequence)

| # | Slide | Purpose | Key content |
|---|-------|---------|-------------|
| 1 | **Cover** | Company + round tagline | Logo, one-liner, raise amount + instrument |
| 2 | **Problem** | Pain worth solving | 3 bullets, quantified ($/time/risk), customer quote |
| 3 | **Solution** | Your unique approach | One sentence + 3 value props, demo screenshot/mockup |
| 4 | **Why Now** | Market timing | Macro tailwinds, tech readiness, regulatory shift |
| 5 | **Market Size** | TAM/SAM/SOM | Bottom-up calc, credible sources, expanding market |
| 6 | **Product** | What you built | Architecture diagram, key features, differentiation |
| 7 | **Traction** | Proof it works | Revenue/users/retention/NPS — charts, not vanity metrics |
| 8 | **Business Model** | How you make money | Pricing, unit economics (LTV/CAC), payback period |
| 9 | **Go-to-Market** | How you grow | Channels, CAC by channel, sales cycle, partnerships |
| 10 | **Competition** | Why you win | 2x2 or feature matrix, your moat (tech/data/distribution) |
| 11 | **Team** | Why you | Founders + key hires, relevant exits/domain expertise |
| 12 | **Financials** | Model + ask | 3-yr projection, burn, runway, use-of-funds waterfall |
| 13 | **The Ask** | Round details | Amount, instrument, valuation/cap, allocation %, close date |
| 14 | **Appendix** | Deep dives | Tech stack, detailed financials, customer logos, FAQ |

**Trim rule**: If pre-seed, drop Financials appendix. If Series B+, add "Strategic Vision" slide after Team.

## officecli patterns for pitch decks

### Create & theme
```bash
officecli create deck.pptx
officecli set deck.pptx / --prop defaultFont="Inter" --prop themeColor=003366 --prop accentColor=00A3E0
```

### Cover slide
```bash
officecli add deck.pptx / --type slide --prop layout=Title
officecli set deck.pptx '/slide[1]/shape[@name="Title 1"]' --prop text="Company Name"
officecli set deck.pptx '/slide[1]/shape[@name="Subtitle 1"]' --prop text="One-liner tagline"
officecli add deck.pptx '/slide[1]' --type shape --prop text="Seed • $2.5M SAFE • $15M cap" --prop x=2cm --prop y=14cm --prop size=18 --prop color=FFFFFF
```

### Problem / Solution (2-column layout)
```bash
officecli add deck.pptx / --type slide --prop layout=TwoContent
officecli set deck.pptx '/slide[2]/shape[@name="Content Placeholder 2"]' --prop text="• Pain point 1: $X cost per incident\n• Pain point 2: Y hours wasted\n• Pain point 3: Z% churn"
officecli set deck.pptx '/slide[2]/shape[@name="Title 1"]' --prop text="The Problem"
```

### Traction chart (bar/line)
```bash
officecli add deck.pptx '/slide[7]' --type chart --prop chartType=columnClustered \
  --prop categories="Q1,Q2,Q3,Q4" --prop series='[{"name":"MRR","values":[50,75,110,160]}]' \
  --prop anchor.x=2cm --prop anchor.y=5cm --prop anchor.w=20cm --prop anchor.h=12cm
```

### Competition 2x2 (scatter via XY chart)
```bash
officecli add deck.pptx '/slide[10]' --type chart --prop chartType=scatter \
  --prop series='[{"name":"Us","values":[{"x":90,"y":95}]},{"name":"Competitor A","values":[{"x":60,"y":70}]},{"name":"Competitor B","values":[{"x":75,"y":60}]}]' \
  --prop axisTitleX="Technical Differentiation" --prop axisTitleY="Distribution Reach"
```

### Financials table
```bash
officecli add deck.pptx '/slide[12]' --type table --prop rows=5 --prop cols=4 \
  --prop data="Year,Revenue,EBITDA,Cash Burn\n2025,2.4M,-0.8M,1.2M\n2026,8.1M,0.5M,0.9M\n2027,22M,5.2M,0.3M\n2028,45M,14M,-2.1M"
officecli set deck.pptx '/slide[12]/table[1]' --prop style=Medium2 --prop headerRow=true
```

### Use-of-funds waterfall (stacked bar)
```bash
officecli add deck.pptx '/slide[12]' --type chart --prop chartType=barStacked \
  --prop categories="Use of Funds" --prop series='[{"name":"R&D (45%)","values":[45]},{"name":"S&M (30%)","values":[30]},{"name":"Ops (15%)","values":[15]},{"name":"G&A (10%)","values":[10]}]'
```

## Styling checklist (apply after all content)
```bash
# Font consistency
officecli set deck.pptx / --prop defaultFont="Inter"
# Color theme: dark navy bg, white text, electric blue accent
officecli query deck.pptx 'shape[fill=FFFFFF]' | while read p; do officecli set deck.pptx "$p" --prop fill=003366; done
officecli query deck.pptx 'shape[fill=000000]' | while read p; do officecli set deck.pptx "$p" --prop fill=00A3E0; done
# Slide numbers (skip cover)
officecli set deck.pptx / --prop slideNumberStart=2 --prop footerText="Confidential • Company Name • 2026"
```

## Data inputs expected
Feed these from the user / research pack before building:
- **One-liner** (≤12 words)
- **Problem bullets** (3, quantified)
- **Solution statement** (1 sentence + 3 value props)
- **Market numbers** (TAM/SAM/SOM with sources)
- **Traction metrics** (MRR, users, retention, NPS, logos)
- **Unit economics** (LTV, CAC, payback, gross margin)
- **GTM channels** (CAC by channel, cycle length)
- **Competitive axes** (your 2 dimensions + competitor coords)
- **Team bios** (1-line each, relevant exit/expertise)
- **Financial model** (3-yr revenue/EBITDA/burn, assumptions)
- **Round details** (amount, instrument, cap/valuation, %, close date)

## Pitfalls to avoid
- **Don't guess property names** — run `officecli help pptx shape` / `help pptx chart` / `help pptx table`
- **Don't use positional shape indices** — use stable `@name=` or `@id=` from `get --depth 1`
- **Don't stack too many elements on one slide** — max 5 shapes (title + 3 content + footer)
- **Don't use `--index` for slide ordering** — `add` appends by default; use `--after '/slide[N]'` for precise placement
- **Don't forget `--prop headerRow=true` on financial tables** — otherwise first row isn't styled as header
- **Don't export without `validate`** — run `officecli validate deck.pptx` before sending

## Quick start template (copy-paste)
```bash
officecli create pitch.pptx
officecli set pitch.pptx / --prop defaultFont="Inter" --prop themeColor=003366 --prop accentColor=00A3E0
# Cover
officecli add pitch.pptx / --type slide --prop layout=Title
officecli set pitch.pptx '/slide[1]/shape[@name="Title 1"]' --prop text="<Company>"
officecli set pitch.pptx '/slide[1]/shape[@name="Subtitle 1"]' --prop text="<One-liner>"
# Problem
officecli add pitch.pptx / --type slide --prop layout=TitleAndContent
officecli set pitch.pptx '/slide[2]/shape[@name="Title 1"]' --prop text="The Problem"
officecli set pitch.pptx '/slide[2]/shape[@name="Content Placeholder 2"]' --prop text="• <Pain 1>\n• <Pain 2>\n• <Pain 3>"
# ... continue for each slide ...
officecli validate pitch.pptx
```