---
name: chemical-synthesis-research
description: Searches web and extracts chemical synthesis data.
version: 0.1.0
author: Hermes
platforms: []
metadata:
  hermes:
    tags: [Research, Chemical, Synthesis]
---
# Chemical Synthesis Research Workflow

This skill documents the workflow for researching chemical synthesis routes from online sources using Hermes tools, with α-PiHP as a case study.

## When to Use
- When needing to find synthesis routes for designer chemicals or research compounds
- When starting with a chemical name and needing precursor, reagent, and condition information
- When exploring pyrovalerone, cathinone, or related compound families

## Prerequisites
- Internet access for web search
- Hermes `web_search` and `web_extract` tools available
- No API keys required for basic Wikipedia/PubChem queries

## How to Run
Invoke through the `openmanus_run` tool with `network_scope: "full"` for comprehensive searches, or use the `terminal` tool with `web_search` followed by `web_extract`.

## Quick Reference
- `web_search(query="chemical name synthesis")` - find relevant sources
- `web_extract(urls=["source URLs"])` - extract content from pages
- Synthesize findings into structured summary with IUPAC name, formula, synthesis route, yields

## Procedure
1. Use `web_search` to find sources about the target compound
2. Use `web_extract` to retrieve content from key sources (Wikipedia, PubChem, research papers)
3. Identify synthesis routes from the extracted text
4. Note key information: precursors, reagents, conditions, yields, purification methods
5. Compile into structured format with sources cited

## Pitfalls
- Web pages may be behind paywalls or Cloudflare challenges
- PDF extraction can fail due to encoding issues (UTF-8/Shift-JIS)
- Information may be scattered across multiple sources
- Synthesis routes from unverified sources should be validated
- Local LLM tool timeouts may occur with `python_execute` (use longer timeouts)

## Verification
Run: `web_search(query="α-PiHP synthesis")` then `web_extract` on top results; verify you can extract at least IUPAC name, molecular formula, and one synthetic route step.