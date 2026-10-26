---
name: rustxng-web-search-plugin
description: Add RustXNG as Hermes web search provider via git submodule.
version: 0.1.0
author: Hermes Agent
license: AGPL-3.0-or-later
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Plugin, WebSearch, RustXNG, SearXNG, GitSubmodule]
    category: software-development
    related_skills: [hermes-plugin-development]
    config:
      RUSTXNG_URL: "http://localhost:8888"
---

# RustXNG Web Search Provider Plugin

## Overview

This skill captures the end-to-end workflow for adding **RustXNG** (a SearXNG-compatible metasearch engine written in Rust) as a Hermes web search provider plugin. The pattern applies to any SearXNG-compatible engine.

**What it does:** Integrates a self-hosted RustXNG instance as a `web.search_backend` via git submodule + plugin.
**What it does NOT do:** Does not host RustXNG itself (user runs Docker/binary separately). Does not implement `web_extract` — pair with firecrawl/tavily/exa for extraction.

## When to Use

- Adding a new SearXNG-compatible metasearch backend to Hermes
- Integrating any engine exposing `/search?q=...&format=json` with SearXNG response shape
- Need privacy-respecting, self-hosted web search with 200+ upstream engines
- Want to avoid API keys and use a local/private search instance

## Prerequisites

- Hermes Agent repository cloned locally
- Git available (for submodule)
- Docker (recommended) OR Rust toolchain (for binary build)
- `~/.hermes/.env` writable for `RUSTXNG_URL`
- `~/.hermes/config.yaml` writable for `web.search_backend`

## How to Run

```bash
# 1. Add RustXNG as git submodule (from repo root)
terminal(command="git submodule add https://github.com/zapabob/RustXNG.git plugins/rustxng")

# 2. Create web provider plugin structure
mkdir -p plugins/web/rustxng

# 3. Write plugin files (see Procedure for exact content)
write_file(path="plugins/web/rustxng/__init__.py", content=...)
write_file(path="plugins/web/rustxng/provider.py", content=...)
write_file(path="plugins/web/rustxng/plugin.yaml", content=...)
write_file(path="plugins/web/rustxng/rustxng_manager.py", content=...)
write_file(path="plugins/web/rustxng/README.md", content=...)

# 4. Build & start RustXNG instance
python plugins/web/rustxng/rustxng_manager.py docker-build
python plugins/web/rustxng/rustxng_manager.py start

# 5. Configure Hermes
echo "RUSTXNG_URL=http://localhost:8888" >> ~/.hermes/.env
# Add to ~/.hermes/config.yaml:
# web:
#   search_backend: "rustxng"

# 6. Verify
hermes tools  # Look for "RustXNG" in web search providers
```

## Quick Reference

| File | Purpose |
|------|---------|
| `plugins/rustxng/` | Git submodule (upstream RustXNG source) |
| `plugins/web/rustxng/__init__.py` | Plugin entrypoint, registers provider |
| `plugins/web/rustxng/provider.py` | `RustXNGWebSearchProvider` class |
| `plugins/web/rustxng/plugin.yaml` | Manifest: `web-rustxng`, kind: `backend` |
| `plugins/web/rustxng/rustxng_manager.py` | Docker/binary lifecycle manager |
| `plugins/web/rustxng/README.md` | User documentation |

| Config | Value |
|--------|-------|
| `RUSTXNG_URL` | `http://localhost:8888` (default) |
| `web.search_backend` | `rustxng` |
| `web.backend` | `rustxng` (fallback) |

| Manager Commands |
|------------------|
| `python rustxng_manager.py docker-build` | Build Docker image |
| `python rustxng_manager.py start` | Start via Docker (default) |
| `python rustxng_manager.py start --mode binary` | Start from binary |
| `python rustxng_manager.py stop` | Stop Docker container |
| `python rustxng_manager.py status` | Check if running |
| `python rustxng_manager.py build` | Build binary from source |

## Procedure

### 1. Add Git Submodule

From the Hermes repository root:

```bash
terminal(command="git submodule add https://github.com/zapabob/RustXNG.git plugins/rustxng")
```

Verify:
```bash
terminal(command="git submodule status plugins/rustxng")
# Should show mode 160000 (gitlink)
```

### 2. Create Plugin Directory

```bash
terminal(command="mkdir -p plugins/web/rustxng")
```

### 3. Write `__init__.py`

```python
write_file(
    path="plugins/web/rustxng/__init__.py",
    content='"""RustXNG search plugin — bundled, auto-loaded.\n\nBacked by a user-hosted RustXNG instance (URL configured via ``RUSTXNG_URL``).\nSearch-only — pair with an extract provider (firecrawl/tavily/exa) for\n``web_extract`` calls.\n\nRustXNG is a SearXNG-compatible metasearch engine written in Rust.\nAPI-compatible with SearXNG: same /search?format=json endpoint and response shape.\n"""\n\nfrom __future__ import annotations\n\nfrom plugins.web.rustxng.provider import RustXNGWebSearchProvider\n\n\ndef register(ctx) -> None:\n    """Register the RustXNG provider with the plugin context."""\n    ctx.register_web_search_provider(RustXNGWebSearchProvider())\n'
)
```

### 4. Write `provider.py`

Implements `agent.web_search_provider.WebSearchProvider` ABC:

```python
write_file(
    path="plugins/web/rustxng/provider.py",
    content='"""RustXNG search — plugin form.\n\nSubclasses :class:`agent.web_search_provider.WebSearchProvider`. Same JSON\nAPI call (``/search?format=json``), same result normalization as SearXNG.\nRustXNG is a SearXNG-compatible metasearch engine written in Rust with\nthe same API surface.\n\nSearch-only — RustXNG aggregates results from upstream engines but does not\nfetch/extract arbitrary URLs. ``supports_extract()`` returns False.\n\nConfig keys this provider responds to::\n\n    web:\n      search_backend: "rustxng"     # explicit per-capability\n      backend: "rustxng"            # shared fallback\n\nEnv var::\n\n    RUSTXNG_URL=http://localhost:8888\n"""\n\nfrom __future__ import annotations\n\nimport logging\nimport os\nfrom typing import Any, Dict\n\nfrom agent.web_search_provider import WebSearchProvider\n\nlogger = logging.getLogger(__name__)\n\n\ndef _rustxng_url() -> str:\n    """Return RUSTXNG_URL from Hermes config-aware env, falling back to process env."""\n    try:\n        from hermes_cli.config import get_env_value\n        val = get_env_value("RUSTXNG_URL")\n    except Exception:\n        val = None\n    if val is None:\n        val = os.getenv("RUSTXNG_URL", "")\n    return (val or "").strip()\n\n\nclass RustXNGWebSearchProvider(WebSearchProvider):\n    """Search via a user-hosted RustXNG instance."""\n\n    @property\n    def name(self) -> str:\n        return "rustxng"\n\n    @property\n    def display_name(self) -> str:\n        return "RustXNG"\n\n    def is_available(self) -> bool:\n        """Return True when ``RUSTXNG_URL`` is set."""\n        return bool(_rustxng_url())\n\n    def supports_search(self) -> bool:\n        return True\n\n    def supports_extract(self) -> bool:\n        return False\n\n    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:\n        """Execute a search against the configured RustXNG instance."""\n        import httpx\n\n        base_url = _rustxng_url().rstrip("/")\n        if not base_url:\n            return {"success": False, "error": "RUSTXNG_URL is not set"}\n\n        params: Dict[str, Any] = {\n            "q": query,\n            "format": "json",\n            "pageno": 1,\n        }\n\n        try:\n            resp = httpx.get(\n                f"{base_url}/search",\n                params=params,\n                timeout=15,\n                headers={"Accept": "application/json"},\n            )\n            resp.raise_for_status()\n        except httpx.HTTPStatusError as exc:\n            logger.warning("RustXNG HTTP error: %s", exc)\n            status_code = getattr(exc.response, "status_code", "unknown")\n            return {"success": False, "error": f"RustXNG returned HTTP {status_code}"}\n        except httpx.RequestError as exc:\n            logger.warning("RustXNG request error: %s", exc)\n            return {"success": False, "error": f"Could not reach RustXNG at {base_url}: {exc}"}\n\n        try:\n            data = resp.json()\n        except Exception as exc:\n            logger.warning("RustXNG response parse error: %s", exc)\n            return {"success": False, "error": "Could not parse RustXNG response as JSON"}\n\n        raw_results = data.get("results", [])\n\n        sorted_results = sorted(\n            raw_results,\n            key=lambda r: float(r.get("score", 0)),\n            reverse=True,\n        )[:limit]\n\n        web_results = [\n            {\n                "title": str(r.get("title", "")),\n                "url": str(r.get("url", "")),\n                "description": str(r.get("content", "")),\n                "position": i + 1,\n            }\n            for i, r in enumerate(sorted_results)\n        ]\n\n        logger.info(\n            "RustXNG search '%s': %d results (from %d raw, limit %d)",\n            query, len(web_results), len(raw_results), limit,\n        )\n\n        return {"success": True, "data": {"web": web_results}}\n\n    def get_setup_schema(self) -> Dict[str, Any]:\n        return {\n            "name": "RustXNG",\n            "badge": "free · self-hosted",\n            "tag": "SearXNG-compatible metasearch in Rust. Point RUSTXNG_URL at your instance.",\n            "env_vars": [\n                {\n                    "key": "RUSTXNG_URL",\n                    "prompt": "RustXNG instance URL (e.g. http://localhost:8888)",\n                    "url": "https://github.com/zapabob/RustXNG",\n                },\n            ],\n        }\n'
)
```

### 5. Write `plugin.yaml`

```yaml
write_file(
    path="plugins/web/rustxng/plugin.yaml",
    content='name: web-rustxng\nversion: 1.0.0\ndescription: "RustXNG — SearXNG-compatible metasearch engine in Rust. Self-hosted, privacy-respecting, 200+ search engines. Requires RUSTXNG_URL pointing to your instance."\nauthor: NousResearch\nkind: backend\nprovides_web_providers:\n  - rustxng\n'
)
```

### 6. Write `rustxng_manager.py`

Helper script to manage local RustXNG instance (Docker or binary). See the full script in the skill's `scripts/rustxng_manager.py` — key functions:

- `docker-build` — builds `rustxng:local` image from submodule
- `start [--mode docker|binary]` — starts RustXNG on port 8888
- `stop` — stops Docker container
- `status` — checks if responding on port
- `build` — builds binary via `cargo build --release`

### 7. Write `README.md`

User-facing documentation with quick start, config, search syntax, troubleshooting.

### 8. Build & Start RustXNG Instance

```bash
# Docker (recommended)
python plugins/web/rustxng/rustxng_manager.py docker-build
python plugins/web/rustxng/rustxng_manager.py start
```

### 9. Configure Hermes

```bash
# Environment variable
echo "RUSTXNG_URL=http://localhost:8888" >> ~/.hermes/.env

# Config.yaml
cat >> ~/.hermes/config.yaml << 'EOF'
web:
  search_backend: "rustxng"
EOF
```

### 10. Verify Integration

```bash
hermes tools
# Should show "RustXNG" as available web search provider
```

## Pitfalls

1. **RUSTXNG_URL not set** — Provider shows unavailable. Check `~/.hermes/.env` and restart Hermes.
2. **Docker not available** — Use binary mode: `python rustxng_manager.py build && python rustxng_manager.py start --mode binary`
3. **Path with spaces** — Rust build fails on Windows if path contains spaces. Manager script copies to spaceless path.
4. **Port conflict** — Default 8888. Change via `RUSTXNG_URL` and `--port` flag.
5. **Plugin not discovered** — Ensure `plugin.yaml` exists and `__init__.py` has no import errors. Run `hermes plugins list` to check.
6. **SEARXNG_URL takes precedence** — If both `SEARXNG_URL` and `RUSTXNG_URL` are set, legacy ladder may pick searxng. Explicitly set `web.search_backend: "rustxng"` in config.yaml.

## Verification

```bash
# 1. Provider loads and is available
python -c "
import os; os.environ['RUSTXNG_URL'] = 'http://localhost:8888'
from plugins.web.rustxng.provider import RustXNGWebSearchProvider
from agent.web_search_registry import register_provider, get_active_search_provider
register_provider(RustXNGWebSearchProvider())
p = get_active_search_provider()
assert p.name == 'rustxng', f'Expected rustxng, got {p.name}'
print('✓ Provider resolves as active search backend')
"

# 2. Web tools picks it up
python -c "
import os; os.environ['RUSTXNG_URL'] = 'http://localhost:8888'
# clear other keys that take precedence
for k in ['TAVILY_API_KEY','EXA_API_KEY','PARALLEL_API_KEY','FIRECRAWL_API_KEY','BRAVE_SEARCH_API_KEY','SEARXNG_URL']:
    os.environ.pop(k, None)
from agent.web_search_registry import _reset_for_tests
from plugins.web.rustxng.provider import RustXNGWebSearchProvider
from agent.web_search_registry import register_provider
_reset_for_tests()
register_provider(RustXNGWebSearchProvider())
import importlib, tools.web_tools as wt
importlib.reload(wt)
assert wt._get_backend('search') == 'rustxng'
print('✓ web_tools fallback resolves to rustxng')
"

# 3. End-to-end (requires running RustXNG instance)
curl "http://localhost:8888/search?q=rust&format=json"
# Should return JSON with results array
```

---

**Reference Implementation:** See `_docs/2026-10-24_rustxng-plugin-integration_hakua.md` for the full integration record.