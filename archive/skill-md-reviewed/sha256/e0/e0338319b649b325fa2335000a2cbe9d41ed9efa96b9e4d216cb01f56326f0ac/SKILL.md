---
name: web-content-fetching
description: Fetch page text via curl/python3.12 when web_extract fails.
category: research
---

# Web Content Fetching (terminal fallback)

## When to use
- `web_extract` fails with a credentials/config error (e.g. "No xAI credentials found") while `web_search` still returns URLs.
- You have URLs from search results and need the actual page text to summarize (news digests, "今日の注目ニュースは?", research lookups).
- A page resists extraction but a plain browser-UA curl fetch succeeds.

## Core workflow
1. **Prefer a dated summary page** over a sprawling article index. Known-good examples (validated 2026-08-06):
   - Asahi "きょうの3本": `https://www.asahi.com/pickup-news-summary/YYYYMMDD/` (contains the day's 3 headline summaries + a recent-days block, plus top-news headlines)
   - The HEADLINE morning paper: `https://www.theheadline.jp/paper/YYYYMMDD?edition=morning`
2. **Fetch with curl + browser UA into a local temp dir.** On Windows/git-bash: `cd` into the destination first, then use a **relative** `-o` filename (see Pitfalls):
   ```bash
   mkdir -p "$HOME/.hermes/tmp_news" && cd "$HOME/.hermes/tmp_news"
   curl -sS -o asahi.html -w "HTTP:%{http_code} SIZE:%{size_download}\n" \
     -L --max-time 30 -A "Mozilla/5.0" "https://www.asahi.com/pickup-news-summary/20260806/"
   ```
   Expect `HTTP:200 SIZE:18xxxx`. If you get a write error or 0 bytes, check the path form before retrying.
3. **Extract readable text with `python3.12`** (never `python`): strip `<script>`/`<style>`, strip tags, `html.unescape`, collapse whitespace, then print a window around a known marker string (e.g. `きょうの3本`). Full snippet in `references/windows-gitbash-curl-notes.md`.
4. **Verify before summarizing**: confirm HTTP 200 + non-zero size, and that the extracted window actually contains expected headlines. Only then write the user-facing summary, anchored in fetched content rather than search snippets.

## Pitfalls (Windows/git-bash host)
- **Native curl.exe does NOT understand MSYS-style absolute paths** (`/c/Users/...`, `$HOME/...`). `curl -o "$HOME/.../f.html"` fails partway with `curl: (23) client returned ERROR on write of NNNN bytes` and leaves no file; `/tmp/...` output also fails silently. **Fix:** `cd` into the destination directory, then use a **relative** `-o filename` — child processes inherit the Windows CWD, so relative paths resolve.
- **`python` is the Windows Store stub** (prints "Python", exits non-zero, no output). Use `python3.12` for any real script.
- A `web_extract` credential error is auth/config state (provider fallback), not a permanent tool break — after `hermes auth` is fixed, retry web_extract. Do not record "tool is broken"; keep curl as the fallback path.

## Verification
- Report HTTP status + downloaded size, then the extracted headline text — show the user real fetched content, not a paraphrase of search snippets.

## References
- `references/windows-gitbash-curl-notes.md` — validated recipe, dated summary-page URLs, extraction snippet, and the failure transcript that motivated the fix.
