---
name: project-standards-practice
description: "Read AGENTS.md/SOP, consolidate standards, apply to tasks."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [coding-standards, AGENTS.md, SOP, best-practices, workflow]
    related_skills: [hermes-agent-skill-authoring, systematic-debugging, cross-platform-path]
---

# Project Standards Practice

Read the project's AGENTS.md and SOP documents, distill the key coding standards, and apply them to subsequent tasks.

## When to Use

- Starting a new coding task in an unfamiliar codebase
- User asks to "read the AGENTS.md and SOP" or "check the project standards"
- Beginning work on a repository with established conventions
- Before making changes that need to respect project-wide invariants

## Prerequisites

None. The skill operates on locally available documentation.

## How to Run

1. **Locate the standards documents**:
   - Primary: `AGENTS.md` at repository root (usually the main SOP)
   - Secondary: search for `SOP*`, `*.sop`, or `STANDARD*` files
   - Check `_docs/` directory for implementation records

2. **Read and inventory**:
   - Use `read_file` on AGENTS.md (may be large — read in chunks if needed)
   - Use `search_files` to find specific topics (e.g., "Windows", "testing", "profiles")
   - Note section headings to understand document structure

3. **Distill into actionable summary**:
   - Extract concrete rules (not vague guidance)
   - Group by theme: paths, testing, platform quirks, skill authoring, etc.
   - Flag anything that directly constrains how you'll work

4. **Apply to current task**:
   - Reference the consolidated standards when making decisions
   - Flag any conflicts between standards and the current task

## Quick Reference

| Document | Typical Location | Purpose |
|----------|------------------|---------|
| AGENTS.md | repo root | Master guide & assistant mirrors |
| CLAUDE.md / GEMINI.md | repo root | Mirror guides for other assistants |
| _docs/ | repo root | Implementation audit logs |
| skills/ | repo root | Built-in skill standards |

## Procedure

### Step 1: Find the standards

```python
# Search for SOP-like documents
search_files(pattern="AGENTS.md", target="files")
search_files(pattern="*SOP*", target="files")
search_files(pattern="*.sop", target="files")
```

### Step 2: Read the primary document

If AGENTS.md exists at root, read it. For large files, read in sections:

```
read_file(path="AGENTS.md", limit=500)
# If truncated, continue with offset=501
```

### Step 3: Search for specific topics

Focus on sections relevant to your task:

```
# Windows-specific pitfalls
search_files(pattern="Windows|os.kill|UTF-8|pathlib", path=".", file_glob="*.md")

# Testing standards
search_files(pattern="test|pytest|mock", path=".", file_glob="*.md")

# Profile safety
search_files(pattern="get_hermes_home|profile", path=".", file_glob="*.md")
```

### Step 4: Consolidate

Produce a concise summary organized by theme. Include:
- **Hard requirements** (must follow)
- **Strong conventions** (should follow)
- **Platform-specific notes** (Windows/Linux/macOS)
- **Anti-patterns** (what NOT to do)

### Step 5: Apply

Reference the consolidated standards throughout the current task. When in doubt, check the original document.

## Pitfalls

1. **Only reading the first part of AGENTS.md** — it's often long (1000+ lines). Read the whole thing or search for relevant sections.
2. **Treating guidelines as optional** — AGENTS.md often contains hard invariants (e.g., "Sacred Invariants" section).
3. **Missing the "What We Reject" section** — equally important as "What We Want"; tells you what NOT to do.
4. **Not checking for platform-specific sections** — Windows pitfalls are often called out separately.
5. **Forgetting skill authoring standards** — if creating skills, the HARDLINE section is mandatory.

## Verification

- [ ] Read AGENTS.md (or equivalent SOP document) in full or via targeted search
- [ ] Searched for platform-specific sections (Windows/Linux/macOS)
- [ ] Identified hard requirements vs. conventions
- [ ] Consolidated standards into a usable reference
- [ ] Applied standards to current task decisions

## Related Skills

- `hermes-agent-skill-authoring` — if creating/editing skills
- `systematic-debugging` — for root cause investigation
- `cross-platform-path` — for path handling across OSes
