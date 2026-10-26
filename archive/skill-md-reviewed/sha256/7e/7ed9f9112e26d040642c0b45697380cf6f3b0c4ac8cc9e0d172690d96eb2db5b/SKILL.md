---
name: synthetic-drug-scaffold-compare
description: Compare scaffold and design strategy of synthetic drugs.
version: 0.1.0
author: Hermes
platforms:
  - windows
  - linux
  - macos
metadata:
  hermes:
    tags:
      - Research
      - Drugs
      - Scaffold
---

# Synthetic Drug Scaffold Comparison Skill

Systematically compare molecular scaffolds, modular design strategies, and toxicity patterns across synthetic drugs such as nitazenes and synthetic cannabinoids. The skill captures the workflow used to research scaffold similarity, update existing comparison docs, and persist findings to memory.

## When to Use
- User asks for scaffold similarity between two drug classes
- User requests a comparison of designer-drug design strategies
- User wants to extend an existing scaffold comparison report with new classes

## Prerequisites
- Internet access via `web_search`/`web_extract`
- A markdown file for the current comparison, e.g. `Synthetic_Drugs_Scaffold_Comparison_YYYY-MM-DD.md`

## How to Run
Use Hermes tools: `web_search` → `web_extract` → `read_file` → `patch` → `memory` add.

## Quick Reference
- `web_search(query="イミダゾール 人工カンナビノイド")`
- `web_extract(urls=[...])`
- `read_file(path="...Comparison_*.md")`
- `patch(mode="replace", path="...", old_string="...", new_string="...")`
- `memory` action add

## Procedure
1. Confirm scaffold names in Japanese and English for each class
2. Search for representative compounds and scaffold classification
3. Extract authoritative sources for structure and pharmacology
4. Read the existing comparison file
5. Patch the file with new class entries and revised conclusion
6. Add a concise memory entry with the updated file path
7. Verify by reading the first lines of the file

## Pitfalls
- Do not conflate indole with benzimidazole; note indazole is the bridge
- Distinguish CB1 vs opioid receptor families
- Do not invent potency numbers

## Verification
`read_file(path="<comparison_path>", limit=5)` shows updated header and date.
