---
name: intl-50gen-evolution
description: Run 50-generation intl_situation_jp ShinkaEvolve from Cursor via MCP or PowerShell. Prefer Cursor subscription bridge (poll/respond). Also covers mcp-proxy watcher, MoA/Fugu multi-provider合議, Deep Research + 6m forecast, shinka_start_evolution, status/get_best.
---

# Cursor subscription → 50gen closed loop

API キー不要。**Cursor のサブスク枠（Agent のモデル）**が LLM になる。

## Minimal loop（推奨）

```
1. shinka_start_evolution(example=intl_situation_jp, num_generations=50, backend=cursor)
2. Loop until status idle / evolution done:
     shinka_mcp_proxy_poll
       → (あなたが Cursor モデルで system+prompt に答える)
       → shinka_mcp_proxy_respond(id=…, content=…)
3. shinka_evolution_status / shinka_get_best
```

### Agent 応答ルール

- `system` + `prompt` をそのまま守る（EVOLVE-BLOCK マーカー維持）
- 返答全文を `content` に入れる（要約だけは NG）
- pending が空なら `shinka_evolution_status` で世代進捗を確認してから再 poll
- タイムアウト既定は 1800s/request（`SHINKA_MCP_PROXY_TIMEOUT`）

## Prerequisites

```powershell
py -3 scripts/setup_mcp.py
py -3 scripts/setup_mcp.py --check
```

`--check` は `<USER>` / `path/to/project` プレースホルダで **FAIL**。

## Backend 一覧

| backend | 課金元 |
|---------|--------|
| `cursor`（推奨） | **Cursor サブスク**（Agent が poll/respond） |
| `cursor` + `shinka_mcp_watcher_start` | ローカル LM Studio / Ollama |
| `codex` | Codex ログイン / OPENAI_API_KEY（App-Server: `codex app-server`） |
| `nvidia` | `NVIDIA_API_KEY`（NIM） |
| `moa` | **Fugu 風合議** — 利用可能プロバイダを全部プール（UCB + MoA Deep Research） |
| `antigravity` | agy OAuth |

## MoA（Sakana Fugu 風）合議

```powershell
# 50gen multi-provider pool
$env:SHINKA_MOA="1"
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend moa

# または MCP
# shinka_start_evolution(example=intl_situation_jp, num_generations=50, backend=moa)

# MILSPEC Deep Research + ≤6か月予想（キー無し dry-run）
cd examples\intl_situation_jp
py -3 run_deepresearch_moa.py --dry-run

# Live: Codex サブスク + NIM
$env:SHINKA_MOA="1"
$env:SHINKA_EVO_LLM_BACKENDS="codex,nvidia"
$env:SHINKA_CODEX_AUTH="subscription"
$env:NVIDIA_API_KEY="…"
py -3 run_deepresearch_moa.py --live
```

合議パイプライン: **propose → skeptic → aggregate**（`moa_consensus.py`）。
捏造 EvidenceBlock ID は Verifier fail-closed。

## PowerShell

```powershell
# Cursor サブスク（Agent bridge）— Watcher 不要
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend cursor -AgentBridge

# ローカル LLM watcher
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend cursor -StartWatcher -LocalModel "<model>"

# MoA multi-provider
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend moa
```

## Do not

- プレースホルダ MCP のまま起動しない
- EvidenceBlock ID を捏造しない（fail-closed −1000）
- `-IncludeMd` は MD genome 復元まで使わない
- `num_generations=1` は gen0 のみ（変異ループには ≥2）
