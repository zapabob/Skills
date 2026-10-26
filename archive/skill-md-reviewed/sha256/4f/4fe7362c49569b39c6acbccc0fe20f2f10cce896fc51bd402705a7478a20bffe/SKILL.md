---
name: intl-50gen-evolution
description: Run 50-generation intl_situation_jp ShinkaEvolve from Cursor via MCP or PowerShell. Prefer Cursor subscription bridge (poll/respond). Also covers mcp-proxy watcher, shinka_start_evolution, status/get_best.
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
| `codex` | Codex ログイン / OPENAI_API_KEY |
| `antigravity` | agy OAuth |

## PowerShell

```powershell
# Cursor サブスク（Agent bridge）— Watcher 不要
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend cursor -AgentBridge

# ローカル LLM watcher
powershell -ExecutionPolicy Bypass -File scripts\launch_intl_50gen_cursor.ps1 `
  -Generations 50 -Backend cursor -StartWatcher -LocalModel "<model>"
```

## Do not

- プレースホルダ MCP のまま起動しない
- EvidenceBlock ID を捏造しない（fail-closed −1000）
- `-IncludeMd` は MD genome 復元まで使わない
