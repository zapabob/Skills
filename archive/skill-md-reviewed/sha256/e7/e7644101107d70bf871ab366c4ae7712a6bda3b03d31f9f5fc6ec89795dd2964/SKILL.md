---
name: methamphetamine-sar-synthesis-research
description: Research meth synthesis, SAR, analogs; produce report
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Forensic, Chemistry, Literature-Review, SAR, GC-MS, Synthesis]
---

# Methamphetamine SAR & Synthesis Research Skill

Conduct structured literature research on methamphetamine synthesis routes, structure-activity relationships (SAR), pharmacological analogs, and forensic analytical methods (GC-MS, LC-MS, NMR, IR). Produces a comprehensive academic report with cited literature values. Uses `web_search` + `web_extract` for PubMed/UNODC/DEA sources and `write_file` for report output.

**Does NOT perform**: wet-lab synthesis, controlled substance handling, or primary analytical instrument operation. This is a literature synthesis skill only.

---

## When to Use

- Need forensic-grade synthesis route comparison (yields, conditions, route-specific markers)
- Require SAR table for phenethylamine/cathinone/tryptamine analogs
- Need GC-MS/LC-MS/NMR/IR analytical parameters for methamphetamine and regioisomers
- Preparing expert report, court testimony support, or academic literature review

---

## Prerequisites

- Hermes with `web_search` and `web_extract` tools available
- Internet access for PubMed, Google Scholar, UNODC, DEA, AAFS sources
- Write permission to target output directory

---

## How to Run

```bash
# Via Hermes agent conversation:
# "Run methamphetamine SAR/synthesis research and generate report at <path>"
# The agent will execute the Procedure steps below using terminal, web_search, web_extract, write_file
```

---

## Quick Reference

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `web_search` | Query synthesis routes, SAR, analytical methods |
| 2 | `web_extract` | Pull full text from key papers (UNODC, DEA, ACS, Wiley) |
| 3 | `execute_code` | Consolidate extracted data into structured tables |
| 4 | `write_file` | Write final Markdown report |

---

## Procedure

1. **Define scope**: Identify target areas (synthesis, SAR, analogs, analytics) and output path.
2. **Search synthesis routes** (4-6 queries):
   - `methamphetamine synthesis Leuckart reductive amination yield byproducts forensic`
   - `methamphetamine ephedrine pseudoephedrine reduction iodine phosphorus yield`
   - `methamphetamine synthesis route-specific impurities markers`
   - `methamphetamine Birch reduction Moscow Emde Nagai yields`
3. **Search SAR/pharmacology** (3-4 queries):
   - `methamphetamine SAR structure-activity relationship dopamine transporter affinity`
   - `methamphetamine enantiomers d-l pharmacological activity difference`
   - `methamphetamine metabolism CYP2D6 pharmacokinetics`
   - `methamphetamine analogs derivatives pharmacological activity review`
4. **Search analytical methods** (3-4 queries):
   - `methamphetamine GC-MS fragmentation pattern retention time analytical`
   - `methamphetamine LC-MS/MS method validation forensic`
   - `methamphetamine NMR IR spectroscopy identification`
   - `methamphetamine chiral separation enantiomer identification`
5. **Extract full text** from priority sources (UNODC ST/NAR/34, DEA SOP-METH-001, ACS Anal. Chem. papers, JPET pharmacology papers, AAFS proceedings).
6. **Consolidate data** into structured tables:
   - Synthesis route comparison table (yield, conditions, markers, stereoselectivity)
   - SAR table (substituent vs. DAT/NET/SERT affinity)
   - d/l-body pharmacological comparison table
   - Metabolic pathway diagram (text-based)
   - Analog catalog table (structure, activity, notes)
   - GC-MS/LC-MS/NMR/IR analytical parameters
   - Route-specific impurity markers table
   - Detection limits table by method
7. **Write report** as Markdown with:
   - Title, date, methodology
   - Numbered sections matching scope
   - Tables with literature values
   - Reference list with DOIs/URLs
8. **Verify**: Open report, confirm all tables populated, references cited.

---

## Pitfalls

- **Cloudflare blocks**: Many publisher sites (ACS, Wiley, Elsevier, Springer) return challenge pages. Use `web_extract` on PDF URLs or free mirrors (Europe PMC, ResearchGate, university repos) instead of HTML.
- **PDF extraction fails**: Binary PDFs return decode errors. Fallback: search for "PDF" in snippet, try direct PDF URL, or use `browser_navigate` + `browser_snapshot` for JS-heavy pages.
- **site:pubmed searches return empty**: CloakBrowser backend blocks site: operator. Use broad queries + filter manually for PubMed IDs.
- **Rate limits**: Space queries 2-3 seconds apart; batch 4-5 URLs per `web_extract` call.
- **Incomplete data**: Some route yields vary widely in clandestine literature. Report ranges, note "literature values" not single numbers.
- **Enantiomer data**: d/l-body Ki values differ by assay (HEK293 vs. synaptosomes). Cite assay system when possible.

---

## Verification

```bash
# Confirm report exists and has required sections
read_file path="<output_path>/methamphetamine_literature_report.md" limit=50
# Should show: title, 4 main sections (Synthesis, SAR, Analogs, Analytics), tables, references
```