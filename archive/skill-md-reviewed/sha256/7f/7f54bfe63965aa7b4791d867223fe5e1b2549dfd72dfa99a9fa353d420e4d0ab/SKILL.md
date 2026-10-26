---
name: web-fallback
description: Fallback path when web_search is blocked or weak.
version: 1.0.0
tags: [web, fallback, browser, cloakbrowser, browser-use, computer-use, lm-twitterer, cron]
allowed-tools: Bash(web_fallback:*), terminal
---

# Web Search Fallback

## Trigger

- `web_search` returns 403 / empty / captcha / rate-limit
- News / OSINT / X-research cron needs resilient retrieval
- `lm-twitterer` or research tasks must keep working when primary search fails

## Core rule

Do **not** replace Hermes built-in `web_search`. Instead, wrap the fallback as an
external script and call it from the failing path. Keep the built-in tool as the
first attempt; only invoke fallback when the primary path fails or is missing.

## Fallback order

1. `ddg-lite` — direct DuckDuckGo HTML via `urllib`. Fast, no install.
2. `cloakbrowser` — stealth Chromium via the bundled `plugins/web/cloakbrowser/`
   provider. Requires `cloakbrowser` Python package + Playwright Chromium binary.
3. `browser-use` / ComputerUse — best-effort page fetch or GUI browser automation
   when both search-based paths fail.

## Prereqs

```bash
# venv install (already present in this repo)
python -m pip install cloakbrowser

# Playwright Chromium
python -m playwright install chromium

# Enable Hermes plugin
hermes plugins enable web-cloakbrowser
```

Smoke test:

```bash
python -c "from plugins.web.cloakbrowser.session import search_duckduckgo_sync, extract_urls_sync; print(search_duckduckgo_sync('test', 2))"
```

## Reusable script

`~/.hermes/scripts/web_search_fallback.py`

Args: `query` [limit]

Output JSON:
```json
{"ok": true, "query": "...", "provider": "ddg-lite|cloakbrowser", "results": [{"title","url","description","position"}]}
```

Behavior:
- returns direct DDG lite results first
- falls back to CloakBrowser stealth search
- falls back to CloakBrowser extract from DuckDuckGo lite results page
- never raises on failure; returns `{"ok": false, ...}` with error detail

URL normalization:
- unwraps DuckDuckGo `//duckduckgo.com/l/?uddg=...` redirects
- coerces protocol-relative URLs to `https:`

## Cron / script wiring

### lm-twitterer wrappers
Edit `~/.hermes/scripts/lm-twitterer-post.py` and `lm-twitterer-replies.py`:

```python
FALLBACK = "/c/Users/downl/.hermes/scripts/web_search_fallback.py"
# on web_search failure or empty result set:
subprocess.run([PYTHON, FALLBACK, topic, str(limit)], ...)
```

Use only for **research** or **topic inspiration**. Never feed unvalidated fallback
output directly into a public post without human-readable review.

### News / OSINT cron
For cron jobs that call `web_search` directly, replace the failing call with:

```python
import subprocess, json, os
PYTHON = os.environ.get("HERMES_PYTHON") or sys.executable
result = subprocess.run(
    [PYTHON, os.path.expanduser("~/.hermes/scripts/web_search_fallback.py"), query, str(limit)],
    capture_output=True, text=True, timeout=180
)
data = json.loads(result.stdout or "{}")
results = data.get("results", []) if data.get("ok") else []
```

## browser-use deep fallback

When both DDG lite and CloakBrowser return empty:

```python
from browser_use import open as bu_open
session = bu_open("https://lite.duckduckgo.com/lite/?q=" + quote_plus(query))
state = session.state
text = state.get_text()
# parse text for URLs/titles
```

Or use Hermes `computer_use` against the running Chrome window if the task needs
GUI browser state.

## Targets in this repo

- `plugins/lm-twitterer/core.py` — keep built-in; fallback only from cron wrappers
- `~/.hermes/scripts/lm-twitterer-post.py`
- `~/.hermes/scripts/lm-twitterer-replies.py`
- `~/.hermes/scripts/osint-agent-morning.py`
- `~/.hermes/scripts/osint-agent-evening.py`
- `~/.hermes/scripts/wm-osint-pdb-evening.py`
- `~/.hermes/scripts/disaster-news-jp.py`

## Pitfalls

- **Do not** post fallback results to X without review. Fallback is **research only**.
- CloakBrowser provider must be enabled via `hermes plugins enable web-cloakbrowser`;
  import alone is not enough.
- `browser-use` CLI is `browser-use`, not `browser_use`. The Python package import is
  `from browser_use import ...`.
- Playwright binaries live under `%LOCALAPPDATA%\ms-playwright\`. Re-install if the
  cache is cleared.
- DDG lite HTML selectors change; CloakBrowser is the more stable fallback path.
- Hermes `web_search` tool output is not a stable schema; do not parse it.

## Verification

```bash
python ~/.hermes/scripts/web_search_fallback.py "Hermes Agent" 3
```

Expected:
- first run: `provider=ddg-lite`, `results` count >= 1
- if ddg-lite is blocked: `provider=cloakbrowser`, `results` count >= 1

For full integration test, run the affected cron job manually and inspect its
stdout for `ok=true` or the expected research payload.
