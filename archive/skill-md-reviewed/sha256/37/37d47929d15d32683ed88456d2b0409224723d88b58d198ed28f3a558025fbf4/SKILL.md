---
name: worldmonitor-osint
description: Skill for running the World Monitor OSINT Fusion report to generate comprehensive intelligence reports combining World Monitor, Shinka MilSpec OSINT, SitDeck crawl, and government feeds.
category: osint
---

# World Monitor OSINT Fusion Skill

## Description
This skill runs the `worldmonitor_fusion_report` tool to produce a fused OSINT report. It integrates data from World Monitor (country risk, regional brief, news digest), Shinka MilSpec OSINT scenarios, SitDeck dashboard crawl, and government RSS feeds. The user can specify topic, domain, country, data source mode (mock/real), whether to generate an LLM summary, and whether to save the report.

## When to Use
- User asks for a fused OSINT report on a topic (e.g., "認知戦", "台湾有事", "cyber_defense").
- Need to combine multiple OSINT sources into one coherent report.
- Want an LLM-generated summary of the fused data.
- Want the report saved automatically for later reference.

## Parameters
| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| `topic` | string | The topic or keyword for the report (e.g., "認知戦", "台湾有事"). | Yes | - |
| `domain` | string | OSINT domain (e.g., "cyber_defense", "taiwan", "middle_east", "cyber", etc.). | Yes | - |
| `country_code` | string | ISO country code for World Monitor focus (e.g., "JP", "US"). | No | "JP" |
| `wm_tier` | string | World Monitor tier: "auto", "free", "pro". | No | "free" |
| `source_mode` | string | Data source mode: "mock" (uses bundled test data) or "real" (live feeds). | No | "mock" |
| `llm_summary` | boolean | Whether to generate an LLM summary of the fused data. | No | false |
| `save_report` | boolean | Whether to save the generated report to file. | No | false |

## Usage Example
```bash
hermes worldmonitor-osint fusion 認知戦 --wm-tier free --source-mode mock --llm-summary --save
```
This runs a fusion report on the topic "認知戦" in the `cyber_defense` domain, using World Monitor free tier, mock data, with LLM summary, and saves the report.

## Steps
1. Confirm required parameters (`topic`, `domain`). Others have sensible defaults.
2. Invoke the `worldmonitor_fusion_report` tool with the provided parameters.
3. If `save_report` is true, the tool will persist the report under `~/.hermes/cache/worldmonitor/` (or similar location).
4. Return the generated report summary (or full JSON if needed) to the user.

## Pitfalls
- Using `source_mode=real` requires valid API keys for underlying services (World Monitor, Shinka, SitDeck, government feeds). Missing keys may cause partial or empty data.
- The `llm_summary` option consumes additional LLM tokens; use only when a summary is needed.
- The fused report can be large (hundreds of KB). Consider using `save_report` to avoid flooding the chat with raw JSON.
- Ensure the `worldmonitor_fusion_report` tool is available in the current environment (it is part of the Hermes OSINT toolset).

## Related Tools
- `worldmonitor_status` – Check World Monitor API readiness.
- `shinka_osint_status` – Check Shinka OSINT plugin readiness.
- `sitdeck_status` – Check SitDeck plugin readiness.
- `gov_feed_status` – Check government feed status.

## References
- See the tool definition for `worldmonitor_fusion_report` for exact schema and behavior.
- For details on each sub-component, refer to the respective tool documentation.