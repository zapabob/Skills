---
name: elt-progress-infographic
description: Analyze local ELT pipeline progress, lane metrics, bridge dataset quality, GPU/disk health, and recommended interventions; use when the user asks for ELT progress, data-log analysis, bridge/ILSD/GRPO status, or a Japanese one-page infographic/image of the run.
---

# ELT Progress Infographic

Use this skill for the local `elastic-looped-transformer` workspace when the user asks for progress, data analysis, logs, intervention recommendations, or image/infographic output.

## Workflow

1. Collect live evidence from disk and processes before concluding:
   - `H:/elt_data/pipeline_state/status.json`
   - `H:/elt_data/pipeline_state/progress_report.md` if present
   - `H:/elt_data/runs/qwen35_4b_side_lora_*_aha_ilsd_l{2,3}/metrics.jsonl`
   - `H:/elt_data/runs/grpo_side_lora_*_synthetic_v2_bridge/metrics.jsonl`
   - `H:/elt_data/synthetic_v2_hard/**/synthetic_v2_bridge_*summary.json`
   - `nvidia-smi` and `Get-PSDrive H`
2. Prefer the bundled collector:
   ```powershell
   python %USERPROFILE%/.codex/skills/elt-progress-infographic/scripts/collect_elt_progress.py --json
   ```
3. Explain progress in Japanese with concrete lane states:
   - current profile/stage
   - active process/command
   - GPU memory/utilization and H: free space
   - per-lane ILSD L2/L3 state, latest step, checkpoint freshness, tail loss, `l_dist`, `l_entropy`, `l_local`, tokens/sec
   - bridge GRPO reward metrics when available: `reward_std`, `correct_rate`, `format_rate`, `adv_abs_mean`, `verifier_reward_mean`
4. Analyze, do not merely list:
   - rising `l_dist` means teacher/student loop disagreement is increasing; it is not automatically failure, but it is the main L3 risk.
   - `l_entropy` near zero plus rising `l_dist` can indicate over-confident divergence; recommend L3 shortening or lower ILSD lambda if it persists.
   - for bridge GRPO, judge only after at least 3-6 post-start steps unless there is failure/OOM/stall.
   - if `correct_rate` is zero and `reward_std` is sparse, recommend bridge ratio increase, easy-hard mixed cases, or short lane SFT.
5. When the user asks for image output, generate one Japanese 16:9 dashboard-style infographic. Keep it legible and data-backed. Include:
   - progress pipeline
   - bridge data composition
   - ILSD/GRPO metric cards
   - interpretation
   - actionable improvements

## Image Prompt Pattern

Build the prompt from current evidence. Use this structure:

```text
16:9 one-page Japanese technical infographic/dashboard.
Title: ELT synthetic-v2 bridge/ILSD 最新進捗・データ分析・改善点.
Panels:
1. 進捗: profile, stage, lane status chips, GPU/H disk.
2. データ構成: each lane total and easy/bridge/hard split.
3. ログ解析: tail loss, l_dist, entropy/local terms, checkpoint status.
4. 読み取り: healthy/stalled/risky interpretation.
5. 改善点: concrete interventions ranked by priority.
Footer: continue/stop/reconfigure judgment.
```

Use large Japanese text. Avoid dense tables, tiny labels, decorative blobs, and ungrounded claims.

## Intervention Heuristics

- Continue when metrics/checkpoints are advancing and there is no OOM, NaN, or process exit.
- Recommend L3 caution when L2 tail `l_dist` is above about `1.5` for multiple lanes.
- Recommend lowering `lambda_final`, shortening L3, or probing validation before L3 when loss and `l_dist` rise together late in L2.
- Keep `group_size=2` by default on RTX 3060 unless the run is stable and VRAM allows more.
- Preserve replay anchors, KL, and full-layer LoRA when discussing catastrophic-forgetting avoidance.
