---
name: job-interview-preparation
description: "Research a company, analyse applicant documents, and generate interview preparation materials via NotebookLM."
version: "1.2.0"
---

# Job Interview Preparation Skill

Research a target company thoroughly, analyse the applicant's cover letter/resume/skills sheet, and produce comprehensive interview preparation materials — including briefing docs, audio overviews, mind maps, and study guides — leveraging NotebookLM as the final delivery platform.

## When to Use

- User has a final/screening interview with a specific company
- User wants to research a company and prepare talking points
- User provides application documents (CV, cover letter, career history, skills sheet)
- User asks for "interview prep", "面接対策", "final interview preparation"

Requires:
- `nlm` CLI installed and authenticated (`nlm login --check`)
- For doc processing: `python-docx` package (for DOCX), `pymupdf` (for PDF text)
- Web search tools for company research

## Prerequisites

### NotebookLM authentication
```bash
nlm login --check     # Verify auth
# If expired:
nlm login             # Browser-based Google auth
```

### Python packages (for document parsing)
```bash
pip install python-docx  # DOCX extraction
pip install pymupdf      # PDF text extraction (falls back to DOCX when PDF images have no text layer)
```

## Procedure

### Phase 1: Document Ingestion

Extract text from all application documents:

```python
# DOCX extraction (reliable)
import docx
doc = docx.Document(path)
text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())

# PDF extraction (may be empty if scan/image-based)
import pymupdf
doc = pymupdf.open(path)
text = ''.join(page.get_text() for page in doc)
```

Documents to collect:
- Cover letter / カバーレター → key: motivation, tone, unique selling points
- Resume / 履歴書 → key: timeline, education, qualifications
- Career history / 職務経歴書 → key: detailed experience, responsibilities
- Skills sheet / スキルシート → key: technical competency matrix

### Phase 2: Company Deep Research

Use `web_search` + `web_extract` to research the company across these dimensions:

1. **Official site**: Mission, vision, values, leadership team, product lines
2. **Financial/IR data**: Funding rounds, revenue trajectory, investors, official filings
3. **Employee stories**: Wantedly, OpenWork, interview articles, Glassdoor
4. **Tech stack**: Engineering blog, job postings (HRMOS, Findy), product architecture
5. **News**: Press releases (PR TIMES), product launches, partnerships, acquisitions
6. **IPO/Valuation analysis** (pre-IPO targets): Use `references/valuation-analysis-methodology.md` for structured comparable-company IPO valuation — PSR multiples, first-day returns, pre-IPO peer data from minkabu.jp/irbank.net.

Optionally delegate parallel research to a subagent (Research-desk pattern) for deeper coverage on separate topics (competitors, tech challenges, leadership philosophy, IPO valuation modeling).

### Phase 3: Candidate-Company Matching

Create a structured analysis document that maps the applicant's profile to the company's needs:

- Skill alignment matrix
- Experience relevance per product area
- Cultural fit evidence (values matching)
- Key talking points for each potential conversation thread

### Phase 3.5: Interviewer Profiling & Deep-Dive Question Generation

When multiple interviewers from different functions will be present, build individual profiles for each and generate tailored questions. This is especially important when interviewers have diverse backgrounds (founder, finance, HR, engineering) — each evaluates from a different angle.

#### Step 1: Research each interviewer

Per interviewer, collect:
- **Career history**: past companies, roles, industries (source: company member page, LinkedIn, Wantedly articles)
- **Tenure at target company**: how long have they been there? Recent joiners bring external perspective; long-tenured ones embody the culture
- **Functional lens**: finance people evaluate ROI/scalability; HR evaluates self-awareness/culture-fit; founders evaluate mission alignment/ownership
- **Public statements**: interviews, blog posts, social media — these reveal their personal values and pet topics
- **Interview style signals**: from interview experience sites (OpenWork, OneCareer, 就活会議), look for patterns — "雑談ベース", "深掘りがすごい", "和やか", "ロジカル"

Search examples:
```
web_search(query="[company] 面接 体験談 最終面接", limit=5)
web_search(query="[interviewer name] 経歴 プロフィール", limit=5)
web_extract(urls=["https://www.[company].jp/member/"])
```

#### Step 2: Infer interview style from career background

| Career Background | Likely Interview Style | Watch For |
|---|---|---|
| **Founder/CEO** | Mission-driven, values-focus, "why" deep-dives, story/listening mode | Hollow answers, lack of ownership, no personal mission |
| **Strategy/M&A (ex-consulting)** | Logical/structured, KPI/ROI focus, quantitative evidence required | Fuzzy metrics, vague impact claims |
| **HR veteran (ex-Recruit, ex-large corp)** | Self-awareness probes, growth-potential evaluation, meta-cognition checks | Low self-awareness, canned answers |
| **Engineering/product leader** | Technical depth, architecture decisions, trade-off reasoning | Surface-level tech knowledge |

#### Step 3: Generate 5 deep-dive questions per interviewer

The **Rule of 5**: for each interviewer, generate exactly 5 questions that:
1. **Connect the interviewer's expertise to the candidate's domain**: e.g. for a CFO-turned-M&A-exec, ask about security investment ROI
2. **Stress-test a specific value or skill** the interviewer likely cherishes: founders test ownership; HR tests self-awareness
3. **Require a specific concrete example** from the candidate's experience — no hypotheticals
4. **Demand translation** between tech and the interviewer's language: finance = numbers, HR = people, founder = mission
5. **Function as a reverse-question opener**: ask what the interviewer thinks about the candidate's domain (shows confidence and curiosity)

Each question entry in the document should have three fields:
```
#### Q[N]: [Actual question text in 日本語]

**質問の狙い**: What is the interviewer's hidden agenda? What signal are they collecting?

**回答のポイント**:
- Bullet-pointed answer strategy
- Suggested keywords and framing
- How to connect back to the company's mission/values
```

#### Step 4: Create a strength-to-context mapping table

Map the candidate's concrete achievements to the needs of the target company:

| Candidate Achievement | Company-Context Meaning | Which Interviewer Cares Most |
|---|---|---|
| OSS contributions to [project] | Ecosystem contributor, self-directed, peer-reviewed skills | Founder (ownership), Engineering lead (quality) |
| Security vulnerability discovery | Product trustworthiness, risk reduction | M&A exec (due diligence value), Founder (brand value) |
| Cross-platform architecture | Scalability, multi-environment reliability | Engineering lead (tech depth), M&A exec (growth readiness) |
| Side projects / autonomous systems | Self-starter, new value creation | Founder (事業家精神), HR (growth potential) |

#### Step 5: Per-interviewer strategy notes

For each interviewer, write a 3-line strategy:
- **Approach**: How to engage them (warm story vs. cold data vs. philosophical discussion)
- **Keywords**: 3-5 resonant terms to weave into answers
- **Avoid**: Topics or tones that would trigger a negative assessment

### Phase 4: Interview Q&A Generation

Generate predicted interview questions and draft answers organised by category:

- **Motivation**: Why this company? Why this role? Career narrative?
- **Technical**: Domain-specific questions (AI/ML, security, infrastructure, etc.)
- **Behavioural**: STARR-based situation handling, values alignment
- **Strategic**: Product vision, industry trends, company challenges
- **Interviewer-specific** (multi-interviewer panels): Generate per-interviewer deep-dives from Phase 3.5 — these are NOT duplicates of the category questions; they probe the interviewer's unique lens on the candidate's domain

### Phase 5: NotebookLM Material Generation

Push all research and prep materials into NotebookLM and generate artifacts:

```bash
# 1. Create notebook
nlm notebook create "<Company> Final Interview Preparation"
NB="<notebook-id>"

# 2. Add sources (all prep documents)
nlm source add "$NB" --file interview_master_source.md --wait
nlm source add "$NB" --file cover_letter.md --wait
nlm source add "$NB" --file career_history.md --wait

# 3. Generate artifacts
nlm report create "$NB" --format "Briefing Doc" --language ja-JP --confirm
nlm audio create "$NB" --format deep_dive --length short --language ja-JP --confirm
nlm mindmap create "$NB" --confirm
nlm quiz create "$NB" --count 10 --difficulty 3 --language ja-JP --confirm

# 4. Download outputs
nlm download report "$NB" --output briefing_report.md
nlm download audio "$NB" --output interview_prep.m4a   # NOTE: .m4a not .mp3!
```

### Full-format generation ("すべての資料形態")

When the user asks for ALL material formats, generate: report, audio, video
(explainer/whiteboard), slides, infographic, quiz, flashcards, mind map, and
data table. Batch the `create` calls with `sleep 5` between them, then poll
downloads.

### ⚠️ Download/Export Pitfalls (verified 2026-07-24)

- **Flashcards `--format markdown` can return a near-empty file** (title only, ~20 bytes). Use `--format html` instead. Quiz markdown may also be title-only if downloaded before generation truly completes — check `wc -c` and re-download.
- **Data table → Google Sheets**: command is `nlm export to-sheets <nb> <artifact-id> --title "..."` (NOT `export sheets`). Returns a docs.google.com URL — include it in the deliverables list.
- **Video/slides/infographic also show `unknown` status** — poll via download-attempt loop like audio. Video (~50MB) can take 10+ min; run the polling loop as `terminal(background=true, notify_on_complete=true)`.
- **Windows `.venv` without pip**: install parsing deps with `uv pip install <pkg> --python .venv/Scripts/python.exe`.
- **`nlm login --check` may report network_error while cached creds still work** — try an actual API call (`nlm notebook list`); only relogin on a real "Authentication expired".

### Updated applicant documents arriving mid-task (delta-source pattern)

When the user supplies a NEWER application pack after generation has started
(or finished):

1. Extract the new pack (DOCX preferred over PDF for tables).
2. Write a **delta source** (e.g. `candidate_update_<date>.md`) that:
   - states explicitly "this supersedes older documents when they conflict",
   - lists only the NEW/changed facts (new job-title axis, new achievements,
     address changes, new timeline), plus a "translation to this company"
     section mapping the new facts to the target company's needs.
3. Add the delta + raw extracted texts as additional sources (don't delete old ones).
4. Re-run ALL artifact `create` calls with `--focus` instructions naming the
   new facts as top priority ("2026-07-21最新版の…を最優先に…Use only uploaded sources.").
5. Download into a separate `deliverables_v2/` folder and keep v1 for comparison.
6. Verify the new facts actually appear in the regenerated briefing
   (`grep` for the new keywords) before reporting completion.

### Retrieving artifact IDs for export

`nlm export to-sheets` needs the data_table artifact id. Get it via:
```bash
nlm studio status "$NB" --json | python -c "import sys,json;d=json.load(sys.stdin);[print(x['id']) for x in d if x['type']=='data_table' and x['status']=='completed']"
```
Newest artifact is typically listed first. Multiple regenerations leave old
completed artifacts in the list — pick the right one by recency.

### ⚠️ Audio Generation Pitfalls

**`unknown` status**: The CLI reports audio artifacts as `unknown` even when
generation is still processing. Do not rely on `studio status` for audio.
Instead, poll via download attempts:

```bash
for i in $(seq 1 12); do
  nlm download audio "$NB" --output audio.m4a 2>/dev/null && break
  sleep 30
done
```

**Japanese audio** can take 3–5 minutes or longer. Use `--length short` to
reduce generation time. If still stuck after 5 minutes, regenerate (the
original artifact may have silently hung).

**Format requirement**: NotebookLM audio is AAC in an MP4 container. Use
`.m4a` extension, not `.mp3`. Convert later with ffmpeg if needed:

```bash
nlm download audio "$NB" --output raw.m4a
ffmpeg -i raw.m4a -acodec libmp3lame -q:a 2 interview_prep.mp3
```

### ⚠️ Audio length flag is NOT free-form

`nlm audio create --length <x>` only accepts `short`, `default`, or `long`.
Any other value (e.g. `medium`) fails immediately with:
`Error: Unknown audio length 'medium'. Valid options: default, long, short`.
When a longer-than-short but not max-length audio is wanted, use `--length long`
(or omit `--length` for `default`). Do not guess `medium`.

## Drill-down / deep-dive on a sub-topic (post-delivery)

After the initial full-format delivery, the user often asks to go DEEPER on
one theme (e.g. "新経営体制・IPO・M&Aをさらに深掘りした専用の想定Q&A"). This is
DISTINCT from the delta-source pattern (which UPDATES existing facts) — a
drill-down produces a DEDICATED new deliverable set for a focused topic.

Procedure:
1. Fan out 2 parallel subagents (Research-desk + OpenManus role):
   - one for primary research on the sub-theme (with cited URLs),
   - one for candidate-specific predicted Q&A (full scripts) mapping the
     candidate's real achievements to that sub-theme.
2. Write an **integrated source** (`<theme>_integrated.md`) that condenses both
   into a Japanese, interview-ready brief: 1-minute executive summary, key
   facts, category-indexed Q&A index pointing to the full-script file.
3. Add the 3 files (research + Q&A + integrated) as NEW sources to the SAME
   notebook (don't delete v1 sources; more sources = richer cross-reference).
4. Regenerate a focused format set with `--focus` naming the sub-theme as top
   priority ("<theme>を軸に…Use only uploaded sources.").
5. Download into a SEPARATE sub-folder (`deliverables_<theme>/`) so v1 stays
   intact for comparison. Verify the new facts appear in the regenerated
   briefing before reporting done.

This keeps the original deliverable as a baseline while giving a specialised
pack — matches the "compare and use" working style.

## Visual handoff when tldraw-offline is requested

If the user asks to "use tldraw-offline" for a mind-map/diagram, note the
runtime prerequisite: the **tldraw offline desktop app must be running** with a
document open AND `server.json` present (see `tldraw-offline` skill). If the app
is NOT running (no `server.json` at `~/.config/tldraw/` / `%APPDATA%\tldraw\`),
the live `/exec` canvas generation cannot run.

Fallback that still delivers value: write a structured JSON mind-map data file
(central node + labelled branches + leaf notes) into the deliverables folder.
The user can open tldraw offline later and the agent can expand it via `/exec`
from that JSON. Pattern proven 2026-07-24: `tldraw_mindmap.json` with keys
`title`, `note`, `central`, `branches[]` (each `label` + `children[]`).

## References

See the `references/` directory for session-specific case studies:
- `tldraw-mindmap-template.json` — Copy-able JSON scaffold for a tldraw mind-map
  (central + labelled branches + leaf notes) when tldraw offline is requested
  but the app is not running (use as fallback deliverable).
- `leading-mark-case.md` — Full Leading Mark final interview preparation workflow (NotebookLM-based)
- `leadingmark-interviewer-profiling-case.md` — Multi-interviewer profiling + 15 deep-dive questions (pure research, no NotebookLM) — 2026-07-24 Leading Mark session with founder/M&A/CHRO profile analysis
- `leadingmark-full-format-run.md` — All-formats run: timings per artifact, download gotchas, subagent output-path pattern
- `leadingmark-v2-refresh.md` — Mid-task document refresh: delta-source pattern, DOCX table extraction, to-sheets artifact-id lookup
- `valuation-analysis-methodology.md` — Structured methodology for comparable-company IPO valuation analysis (PSR multiples, peer data collection, revenue estimation, scenario table construction)
- `persol-bpd-case.md` — PERSOL Business Process Design AIエンジニア case: local source-pack structure, interview strategy mapping, 5 concrete candidate-company fit stories, and NotebookLM notebook layout for one-person screening/ first-interview breakthrough prep

## Related Skills

- `company-deepresearch` — Company research methodology (use in Phase 2)
- `nlm-skill` — NotebookLM CLI deep reference
- `delegate_task` — Parallel subagent research pattern (Research-desk)
