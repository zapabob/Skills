---
name: moa-ai-company-orchestration
description: "Class-level pattern for running AI employee profiles as a Mixture-of-Agents (MoA) company in the browser/gateway, with domain-specific workflow integration (e.g., antique dealer license acquisition)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [moa, ai-employee, kanban, fugu-pattern, browser-automation, domain-workflow]
    category: autonomous-ai-agents
    related_skills: [ai-employee-org, moa-fugu-orchestrator, moa-cost-routing, hermes-agent]
---

# MoA AI Company Orchestration

Run multiple Hermes profiles as a **Mixture-of-Agents (MoA) company** that works in the browser via the gateway. Each profile (secretary, job-recruiter, job-seeker, self-improver, delivery-worker) uses the **SAKANA AI "fugu" pattern**: fixed strong orchestrator (GPT-5.6 Luna / Grok-4.5) as aggregator, daily-rotated free models as reference panel.

## When to Use

- User wants AI employees to operate as a coordinated company in the browser (Dashboard/Kanban)
- Domain-specific workflows (antique dealer license, e-commerce, research, etc.) need to be decomposed across roles
- Cost control via fugu MoA: premium only for aggregation, free models for sensory panel
- Durable work queue via Kanban (survives restarts, unlike `delegate_task`)

## Prerequisites

- Hermes gateway running (`hermes gateway run`)
- `ai-employee-org` plugin enabled (bundled) — provides 5 profiles + Kanban board `ai-company`
- `moa-fugu-orchestrator` pattern configured in `~/.hermes/config.yaml`
- API keys in `~/.hermes/.env`: `OPENAI_CODEX_KEY` (for GPT-5.6 Luna), `XAI_API_KEY` (for Grok-4.5), plus free provider keys

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GATEWAY (single dispatcher)              │
│  kanban.dispatch_in_gateway: true  (secretary profile only) │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  secretary    │     │ job-recruiter │     │  job-seeker   │
│  (orchestrator)│     │               │     │               │
│  MoA: fugu    │     │  MoA: fugu    │     │  MoA: fugu    │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    KANBAN BOARD: ai-company                 │
│  Triage → Decompose → Assign → Execute → Review → Archive  │
└─────────────────────────────────────────────────────────────┘
```

## Setup Procedure

### 1. Enable Plugin & Bootstrap Profiles (one-time)

```powershell
hermes plugins enable ai-employee-org
hermes ai-employees install --telegram-chat-id <YOUR_CHAT_ID>  # or --dry-run first
hermes gateway run
```

### 2. Apply Fugu MoA to All 5 Profiles

**Critical**: The aggregator MUST be a strong fixed model (GPT-5.6 Luna or Grok-4.5), NOT a free model. The current `hakuapulse-orchestrator` preset uses `freebuff:deepseek/deepseek-v4-flash` as aggregator — **this violates the fugu pattern** and must be fixed first.

```powershell
# Fix the aggregator in config.yaml (run once)
python - <<'PY'
import yaml
from pathlib import Path
cfg = Path.home() / ".hermes" / "config.yaml"
data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
# Correct the aggregator to GPT-5.6 Luna (fugu pattern)
data["moa"]["presets"]["hakuapulse-orchestrator"]["aggregator"] = {
    "provider": "openai-codex", "model": "gpt-5.6-luna"
}
cfg.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
print("Fixed aggregator to GPT-5.6 Luna")
PY
```

Then assign the fugu preset to all profiles:

```powershell
$profiles = "secretary","job-recruiter","job-seeker","self-improver","delivery-worker"
foreach ($p in $profiles) {
    hermes -p $p config set model.provider moa
    hermes -p $p config set model.default hakuapulse-orchestrator
}

# Only secretary runs the dispatcher
hermes -p secretary config set kanban.dispatch_in_gateway true
$others = "job-recruiter","job-seeker","self-improver","delivery-worker"
foreach ($p in $others) {
    hermes -p $p config set kanban.dispatch_in_gateway false
}

hermes gateway restart
```

### 3. Schedule Daily Reference Model Rotation

```powershell
# Copy selector script
cp plugins/ai-employee-org/scripts/daily_moa_provider_selector.py scripts/

# Register cron (runs at 04:00, no_agent = zero LLM cost)
hermes cron create "0 4 * * *" `
  --script scripts/daily_moa_provider_selector.py `
  --no-agent `
  --name "daily-moa-rotation" `
  --deliver local
```

### 4. Inject Domain Workflow (e.g., Antique Dealer License)

Secretary decomposes the high-level goal into role-specific Kanban tasks:

```bash
# Human or webhook creates the epic
hermes kanban create "古物商許可証取得プロジェクト" --assignee secretary --priority 1

# Secretary (auto or manual) creates children:
hermes kanban create "必要書類チェックリスト作成・様式ダウンロード(警視庁)" --assignee job-recruiter --parent <epic-id>
hermes kanban create "自宅営業所の図面・賃貸契約書コピー準備" --assignee delivery-worker --parent <epic-id>
hermes kanban create "申請書類一式完成→日野警察署生活安全課へ相談・提出" --assignee secretary --parent <epic-id>
hermes kanban create "許可取得後の古物台帳テンプレート(Excel/Notion)作成" --assignee self-improver --parent <epic-id>
hermes kanban create "求人・スカウト監視継続(並行タスク)" --assignee job-seeker --parent <epic-id>
```

Each worker profile runs its cron + Kanban-picked tasks, reporting back via `kanban_complete`.

## Key Config Points

| Setting | Value | Why |
|---------|-------|-----|
| `model.provider` | `moa` | Enables Mixture-of-Agents |
| `model.default` | `hakuapulse-orchestrator` | Fugu preset (fixed aggregator + rotating refs) |
| `moa.presets.hakuapulse-orchestrator.aggregator` | `openai-codex:gpt-5.6-luna` | **Must be strong fixed orchestrator** |
| `moa.save_traces` | `true` | Capture consensus for local distillation |
| `kanban.dispatch_in_gateway` | `true` (secretary only) | Single dispatcher avoids race conditions |
| `delegation.max_concurrent_children` | `3` | Parallel sub-tasks during triage |

## Antique Dealer License (古物商許可証) — Domain Workflow Reference

See `references/antique-dealer-license-workflow.md` for the complete step-by-step, required documents, timeline, and Kanban task templates.

## Pitfalls

- **Aggregator mismatch**: If `hakuapulse-orchestrator.aggregator` is a free model, the fugu pattern is broken — premium spend doesn't decrease, quality drops. Fix before enabling.
- **Dispatcher duplication**: Only ONE profile (secretary) should have `dispatch_in_gateway: true`. Others `false`.
- **`delegate_task` not durable**: Use Kanban for work that must survive restarts.
- **Free model alias staleness**: Never hard-code `auto-free` real IDs; the daily selector re-resolves them.
- **FreeLLMAPI port**: `:31415` not `:3001`; key from web UI, not chat paste.
- **freebuff proxy**: Runs on `:8765` only when CLI is active; needs `FREEBUFF_PROXY_API_KEY`.

## Verification

```bash
# All 5 profiles on MoA + fugu preset
hermes profile list | grep -E "secretary|job-recruiter|job-seeker|self-improver|delivery-worker"

# Kanban board active
hermes kanban list --board ai-company --status ready,running

# MoA aggregator check
python - <<'PY'
import yaml
from pathlib import Path
from hermes_cli.moa_config import normalize_moa_config, resolve_moa_preset
data = yaml.safe_load((Path.home()/".hermes"/"config.yaml").read_text(encoding="utf-8"))
moa = normalize_moa_config(data["moa"])
p = resolve_moa_preset(data["moa"], moa["default_preset"])
assert p["aggregator"]["provider"] == "openai-codex"
assert p["aggregator"]["model"] == "gpt-5.6-luna"
print("OK: Aggregator =", p["aggregator"]["model"], "| Refs =", len(p["reference_models"]))
PY
```

## 3D MOA Office Visualization

See `references/3d-office-server.md` for the **verified** recipe. Used by the
`warashibe-reselling` plugin's `/moa` slash command.

**Critical corrections (old version silently failed to render):**
- Use **UMD** Three.js (`three@0.147.0/build/three.min.js` + `examples/js/controls/OrbitControls.js`), NOT ES-module `importmap`. Module builds break under `file://` (CORS) and in headless browsers — blank page.
- Add a **2D `<canvas>` org-chart fallback** when WebGL is unavailable or `THREE` is missing.
- The local server serves `/api/gateway-status` itself (same-origin, no CORS). **Never call the Hermes gateway `/moa/status` from the page — it 503s.** Fall back to a redacted `config.yaml` read and label the UI "デモモード".
- Override `SimpleHTTPRequestHandler.extensions_map` so `.js` → `application/javascript`.

Key elements: local vendor bundling (zero CDN, pinned 0.147.0), role-colored avatars per AI employee, same-origin status proxy, auto-start from slash handler.

## Related Skills

- `ai-employee-org` — bundled plugin providing profiles, Kanban, cron templates
- `moa-fugu-orchestrator` — fugu pattern details, rotation script, distillation
- `moa-cost-routing` — alternative cost-saving MoA (free aggregator)
- `warashibe-reselling` — せどり automation with integrated MOA visualization
- `hermes-agent` — CLI, gateway, config, profiles reference