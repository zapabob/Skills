---
name: intl-50gen-cursor
description: Launch and monitor 50-generation intl_situation_jp ShinkaEvolve from Cursor (MCP tools or PowerShell). Use when the user asks for 50gen evolution, Cursor evolution, mcp-proxy, or intl OSINT evolution runs.
---

# intl_situation_jp — 50gen from Cursor

## Goal
Run **50 generations** of `examples/intl_situation_jp` evolution from Cursor, with MILSPEC fail-closed scoring.

## Preferred path (MCP tools)

1. Ensure project MCP server is `shinka_mcp_server.py` (`py -3 scripts/setup_mcp.py` → `.cursor/mcp.json`).
2. Choose LLM backend:
   - **cursor / mcp-proxy** (no cloud API key): start LM Studio or Ollama, then call `shinka_mcp_watcher_start` with `backend` + `model`.
   - **codex**: `backend=codex` (needs `codex login` / subscription or `OPENAI_API_KEY`).
   - **antigravity**: `backend=antigravity` (needs `agy` CLI OAuth).
3. Call `shinka_start_evolution`:
   - `example`: `intl_situation_jp`
   - `num_generations`: `50` (default for this example)
   - `backend`: `cursor` | `codex` | `antigravity` | `auto`
4. Poll `shinka_evolution_status` / `shinka_get_best` / `shinka_mcp_watcher_status`.

## Shell path (PowerShell)

```powershell
# Option A: Cursor mcp-proxy + LM Studio watcher
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend cursor -StartWatcher -LocalModel "<your-local-model-id>"

# Option B: Codex subscription (no watcher)
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend codex

# Option C: Antigravity Gemini OAuth
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend antigravity
```

Or manually:

```powershell
cd examples\intl_situation_jp
$env:SHINKA_EVO_LLM_BACKENDS = "cursor"
$env:SHINKA_MCP_MODE = "1"
$env:SHINKA_NUM_GENERATIONS = "50"
$env:PYTHONUTF8 = "1"
py -3 run_evo.py --num-generations 50 --results-dir results_cursor_manual
```

## Monitor

```powershell
Get-Content examples\intl_situation_jp\results_cursor_*\evolution_run.log -Wait -Tail 40
# or launcher log under _docs\logs\*intl_cursor_50gen.log
```

Manifest: `examples/intl_situation_jp/.shinka_evo_run.json` (pid, results_dir, log_path).

## Do not

- Do not invent EvidenceBlock IDs; verifier fail-closes fabricated citations.
- Do not claim green without `shinka_evolution_status` / log evidence.
- Dual MD line (`run_evo_scenario_md.py`) is still empty — use Python evolution only.

## Related

- `examples/intl_situation_jp/run_evo.py`
- `scripts/launch_intl_50gen_cursor.ps1`
- `scripts/mcp_proxy_watcher.py`
- MCP tools: `shinka_start_evolution`, `shinka_mcp_watcher_start`, `shinka_mcp_watcher_status`
