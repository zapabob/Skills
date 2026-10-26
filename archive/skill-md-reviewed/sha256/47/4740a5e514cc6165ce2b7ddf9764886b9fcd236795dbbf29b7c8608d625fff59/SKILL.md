---
name: job-scan-track
description: Scan job boards (Herp.careers, HRMOS, Cloudworks Tech, BizReach, Findy, etc.), extract structured job postings, deduplicate against a seen-set, and emit prioritized new leads for application workflows.
category: productivity
tags:
  - job-search
  - scraping
  - deduplication
  - ai-ml-roles
  - japanese-tech-market
version: "1.0.0"
---

# Job Scan & Track Skill

Class-level skill for periodic job-board scanning, deduplication, and lead emission. Covers Herp.careers, HRMOS, Cloudworks Tech, BizReach, Findy, and similar Japanese tech job sources.

## Trigger Conditions
- Scheduled cron job (daily/weekly)
- Manual invocation when user wants fresh leads
- Before application-writing sessions to ensure working from latest unseen posts

## Prerequisites
- `seen.json` at workspace root (or configurable path) tracking processed URLs
- Cache directory with raw HTML/Markdown from prior fetches (e.g., `~/.hermes/profiles/<profile>/cache/web/`)
- Python 3.10+ with `re`, `json`, `pathlib`

## Standard Workflow

### 1. Load Seen Set
```python
def load_seen(seen_path: Path) -> set[str]:
    data = json.loads(seen_path.read_text())
    if isinstance(data, list):
        return set(data)
    if isinstance(data, dict):
        urls = set()
        urls.update(data.get('web', []))
        urls.update(data.get('gmail', []))
        return urls
    return set()
```

### 2. Parse Source Files
Each source has a distinct HTML→Markdown structure. Use regex patterns tuned per source:

| Source | Job ID Pattern | Title Pattern | URL Template |
|--------|---------------|---------------|--------------|
| **Herp.careers (Tier IV)** | `(\d{4})_([^_\n]+)` | Group 2 | `https://herp.careers/v1/tier4/jobs/{id}` |
| **HRMOS (Shiseido)** | N/A (no numeric ID in cache) | After `正社員\n` | `https://hrmos.co/pages/shiseido/jobs/{slug}` |
| **Cloudworks Tech** | `job_offers/(\d+)` | From note file or page | `https://tech.crowdworks.jp/job_offers/{id}` |
| **BizReach** | `job/view/(\d+)/` | From email HTML | `https://www.bizreach.jp/job/view/{id}/` |
| **Findy** | `companies/\d+/jobs/([^/"']+)` | From JSON/email | `https://findy-code.io/companies/{cid}/jobs/{jid}` |

### 3. Deduplicate & Emit
```python
def emit_new_jobs(jobs: list[dict], seen: set[str]) -> list[dict]:
    new = []
    for job in jobs:
        if job['url'] not in seen:
            job['idempotency_key'] = f"{job['source'].lower().replace('.','-')}-{job['id']}"
            new.append(job)
            seen.add(job['url'])
    return new
```

### 4. Persist Seen Set
```python
def save_seen(seen_path: Path, seen: set[str]):
    # Preserve old format (list) for backward compat
    seen_path.write_text(json.dumps(sorted(seen), indent=2, ensure_ascii=False))
```

## Priority Scoring (Optional)
Attach a `priority` field to each emitted job for downstream sorting:
- **Tier 1 (10)**: ML/MLOps/AI Engineer, Data Scientist, LLM, Generative AI
- **Tier 2 (7)**: Backend/Data Platform, SRE/DevOps with ML infra, Edge AI
- **Tier 3 (5)**: General Software Engineer, QA, PM at AI companies
- **Tier 4 (1)**: Non-technical, unrelated domains

Keywords for auto-scoring: `機械学習`, `MLOps`, `LLM`, `生成AI`, `AIエンジニア`, `データサイエンティスト`, `データエンジニア`, `ML Engineer`, `AI Engineer`, `Data Scientist`, `Data Engineer`.

## Output Format
Each new job as a JSON object (one per line or array):
```json
{
  "id": "1022",
  "title": "Senior Machine Learning Engineer, (自動運転End to Endモデル)",
  "url": "https://herp.careers/v1/tier4/jobs/1022",
  "source": "Herp.careers (Tier IV)",
  "idempotency_key": "herp-careers-tier4-1022",
  "priority": 10,
  "keywords": ["MLOps", "End to End", "自動運転", "分散学習", "評価基盤"],
  "raw_snippet": "...first 200 chars of description..."
}
```

## Pitfalls & Fixes
| Pitfall | Fix |
|---------|-----|
| HRMOS cache has no stable job IDs | Use slugified title as fallback; accept collisions are rare |
| Cloudworks Tech only in note files, not cache | Also scan `Documents/ops/job-seeker/*.md` for `tech.crowdworks.jp/job_offers/` URLs |
| `seen.json` format drift (list vs dict) | `load_seen()` handles both; always save as sorted list |
| Herp.careers job IDs like `0002`, `1001` collide across companies | Namespace by company in URL (`/v1/tier4/`); include source in idempotency key |
| Duplicate HRMOS entries (location lines parsed as jobs) | Filter out lines that are pure addresses (contain `丁目`, `市`, `区`, `県`, `府`) |

## Reference Files
- `references/herp-careers-patterns.md` — regex patterns, URL templates, sample extractions
- `references/hrmos-patterns.md` — HRMOS/Shiseido parsing notes, slugification rules
- `references/cloudworks-tech-patterns.md` — note-file parsing, known job IDs
- `references/scoring-keywords.md` — priority keyword lists (JA/EN)

## Example Invocation
```bash
cd /c/Users/downl/Documents/ops/job-seeker
python check_jobs.py
```
Produces JSON lines of new jobs to stdout; updates `seen.json` in place.