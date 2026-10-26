---
name: bpneat-submission-audit-skill
description: BPNEAT submission pipeline の TransferPrior 構造化、Phase 0/0.5/1 の監査性強化、phase1-only・reduced sweep・optional decay/HGT artifact 配線を最小差分で進める Skill。
---

# BPNEAT Submission Pipeline Auditability And Research Extension Skill

## Purpose

この Skill は、BPNEAT submission pipeline を次の研究ストーリーで明示化しつつ、ログ・manifest・checkpoint・CSV・artifact・CLI を監査しやすく整えるために使う。

- Phase 0 = forward-NEAT volleyball pretraining
- Phase 0.5 = ablation-based transfer-prior selection
- Phase 1 = downstream BackpropNEAT classification using the selected transfer prior

加えて、以下を optional extension として additive に導入する。

- long-lived-individual exponential decay 条件群
- 既存 HGT tracking / survival analysis の submission pipeline 配線

この Skill の主眼はアルゴリズムの大改造ではなく、**structured handoff / auditability / provenance / reduced sweep / optional research export** の追加である。

## Trigger Keywords

次の語や意図を含む依頼で、この Skill を優先的に使う。

- `TransferPrior`
- `phase1-only`
- `run_manifest.json`
- `no_codons audit`
- `full_with_decay`
- `HGT artifact`
- `structured prior`
- `Phase 0.5 weight stats`
- `reduced sweep`
- `conditions/tasks/activations/seeds`
- `submission pipeline provenance`
- `research_pipeline wiring`
- `transfer prior`
- `phase 0.5`
- `structured handoff`
- `manifest provenance`
- `checkpoint provenance`

## When To Use

この Skill は、次のような依頼に使う。

- submission pipeline の研究ストーリーをコード上で明示したい
- Phase 0.5 の `(w_mean, w_std)` を `TransferPrior` に置き換えたい
- Phase 1 がどの prior を使ったか log / manifest / checkpoint で追いたい
- `--phase1-only` を追加したい
- `conditions/tasks/activations/seeds` で縮約 sweep をしたい
- `no_codons` が no-op かどうかを監査しやすくしたい
- `full_with_decay` / `no_codons_with_decay` を additive に導入したい
- 既存 HGT research analysis を submission pipeline から呼びたい

## When Not To Use

次の依頼にはこの Skill は過剰。

- typo 修正だけ
- 単発の log 文言修正だけ
- 可視化画像だけの軽微修正
- NEAT コアアルゴリズムの全面再設計
- unrelated な UI / データ処理修正

## Non-Goals

- single best weight vector の直接転送に変えること
- 既存 `--quick`, `--full`, 従来 custom 実行の挙動変更
- retrovirus / topology search / JAX training の本質的ロジック変更
- `no_codons` の挙動を、根拠なく強制的に divergence させること

## Design Principles

- 変更は小さく局所的にする
- 新しい挙動は additive に入れる
- backward compatibility を可能な範囲で維持する
- new logs は ASCII-only を優先する
- auditability を algorithmic reinterpretation より優先する
- `TransferPrior` は initialization prior であり、single best model transfer ではない

## Required Implementation

### 1. Add `TransferPrior`

`submission/pipeline/phase_context.py` に frozen dataclass `TransferPrior` を追加する。

Required fields:
- `source_phase`
- `selected_condition`
- `weight_mean`
- `weight_std`
- `sigma_scale`
- `sigma_cap`
- `sigma_floor`
- `seed_summary`
- `created_at`

Requirements:
- `to_dict()` / `from_dict()` を持つ
- JSON/YAML/checkpoint serializable
- minimal and additive

### 2. Extend `PhaseExecutionConfig`

`submission/pipeline/phase_context.py` の `PhaseExecutionConfig` に以下を追加する。

- `phase1_only`
- `transfer_prior_path`
- `conditions`
- `tasks`
- `activations`
- `seeds`
- `research_pipeline`

既存の `condition`, `task`, `activation` は維持し、plural filter は sweep selection 時のみ override とする。

### 3. Update CLI Parsing

`submission/pipeline/configuration.py` を更新する。

Requirements:
- `allow_abbrev=False`
- 追加 CLI:
  - `--phase1-only`
  - `--transfer-prior-path`
  - `--conditions`
  - `--tasks`
  - `--activations`
  - `--seeds`
- list 入力を normalize
- 新規フラグ未使用時は従来挙動を保つ

### 4. Clarify Phase Semantics In `phase_runner.py`

`submission/pipeline/phase_runner.py` を更新する。

Requirements:
- raw tuple handoff を `TransferPrior | None` に置き換える
- phase headers を intent-based / ASCII-only にする

Required phase headers:
- `>>> Phase 0: Forward-NEAT pretraining on volleyball <<<`
- `>>> Phase 0.5: Condition ablation -> select transfer prior <<<`
- `>>> Phase 1: Downstream BackpropNEAT classification <<<`

`--phase1-only` 時は:
- Phase 0 / 0.5 を明示 skip
- prior を disk から load
- prior 未発見時は明確に fail
- per-phase timestamp を runtime metadata に記録

### 5. Update `submission/run.py`

Requirements:
- `run_vb_pretrain_phase()` は `TransferPrior(source_phase="phase0", selected_condition=None, ...)` を返す
- `run_vb_ablation_phase()` は `TransferPrior(source_phase="phase0p5", selected_condition=<selected_condition>, ...)` を返す
- phase-local YAML を保存
- top-level `output_dir/transfer_prior.json` を保存
- Phase 1 開始時に以下を log する:

`USING_TRANSFER_PRIOR source=... condition=... w_mean=... w_std=... sigma_scale=... sigma_cap=... sigma_floor=...`

- classification visualization にも同じ prior を必要に応じて渡す

### 6. Update `checkpoint_manager.py`

Requirements:
- structured `transfer_prior` payload を保存
- 既存 `vb_weight_*`, `phase0p5_weight_*` は読み取り互換を維持
- 新規保存は structured payload を優先

### 7. Expand Runtime Metadata

更新対象:
- `submission/runtime_metadata.py`
- `submission/pipeline/runtime_services.py`

Requirements:
- `manifest.yaml` は維持
- `run_manifest.json` を追加
- 両方に可能な範囲で以下を含める:
  - mode
  - task
  - activation
  - condition
  - seed / seeds
  - n_gens
  - bp_iters
  - transfer_prior
  - backend / device
  - research_pipeline
  - fresh
  - no_resume
  - output_dir
  - phase start/end timestamps
- research artifact があれば manifest から参照する

### 8. Strengthen Ablation Auditability

`submission/experiments/ablation.py` を更新する。

Requirements:
- public boundary では `pretrain_weight_stats` より `transfer_prior` を優先語彙にする
- 小さな condition-resolution helper を追加して、`AblationFlags` と audit dict を返す

Audit dict minimum fields:
- `retrovirus`
- `codons`
- `elite_cross`
- `arch_penalty`
- `sigma_scale`
- `sigma_cap`
- `sigma_floor`
- `bp_iters`
- `seed`

Decay enabled 時の追加 fields:
- `fitness_decay`
- `decay_lambda`
- `decay_start_gen`

各 run 前に ASCII-only の `COND_APPLY ...` を出す。例:

`COND_APPLY task=xor act=tanh condition=no_codons seed=42 n_gens=30 bp_iters=500 retrovirus=1 codons=0 elite_cross=1 arch_penalty=1 sigma_scale=1.0 sigma_cap=0.5 sigma_floor=0.01`

- codon 監査のため `enable_codons` alias/property を明示可能にする
- full mode は `conditions/tasks/activations/seeds` filter を尊重する
- Phase 1 CSV に transfer prior provenance を残す:
  - `transfer_prior_source`
  - `transfer_prior_condition`
  - `transfer_prior_weight_mean`
  - `transfer_prior_weight_std`
  - `transfer_sigma_scale`
  - `transfer_sigma_cap`
  - `transfer_sigma_floor`

### 9. Optional Decay Extension

`submission/experiments/ablation.py` に long-lived-individual exponential decay を optional condition family として追加する。

Requirements:
- additive な small fitness modifier のみ
- default 条件は変更しない
- config surface:
  - `fitness_decay`
  - `decay_lambda`
  - `decay_start_gen`
- long-surviving elites / incumbents の fitness 補正に留める
- topology / retrovirus / JAX training の本体ロジックは変えない

`config/ablation_config.yaml` に新条件を追加:
- `full_with_decay`
- `no_codons_with_decay`

Decay 有効時の `COND_APPLY` には以下を含める:
- `fitness_decay=1`
- `decay_lambda=...`
- `decay_start_gen=...`

### 10. Clarify Prior Use In BackpropNEAT

`src/evolutionary/neat/jax_backprop_neat.py` を更新する。

Requirements:
- algorithm は基本変更しない
- comment / docstring で明示:
  - transfer prior は downstream enabled-edge initialization bias
  - `weight_mean` / `weight_std` は初期 enabled-edge sampling に効く
  - mutation sigma / crossover / topology search には直接効かない
  - それらへ効かせるのは caller が明示的に forwarding した場合のみ

### 11. Keep Visualization Provenance-Consistent

`submission/analysis/classification_viz.py` を更新する。

Requirements:
- optional に `TransferPrior` を受け取れる
- viz が `zero_init` / `transfer_prior_init` のどちらで動いたか log に残す

### 12. Reuse Existing HGT Research Code

以下を再利用する:
- `submission/experiments/research/gene_survival_analysis.py`
- `submission/analysis/plot_hgt_experiment.py`

Requirements:
- 新 subsystem は作らない
- `research_pipeline` 有効時、または full analysis 時に薄い hook で以下を export:
  - HGT transfer logs
  - gene survival curves
  - gene spread/adoption graph
  - compact HGT effect summary figure set
- observational integration に留める
- `ClassificationEvolver._gene_transfer_log` や tracking subclass pattern を優先再利用
- retrovirus operator 本体は作り変えない

Suggested outputs:
- `output_dir/research/hgt_gene_survival_curve.png`
- `output_dir/research/hgt_gene_spread_graph.png`
- `output_dir/research/hgt_effect_metrics.json`
- `output_dir/research/hgt_effect_figures/...`

manifest から参照可能にする。

## Required Audit Surface

### CLI
- `--phase1-only`
- `--transfer-prior-path`
- `--conditions`
- `--tasks`
- `--activations`
- `--seeds`

### Artifacts
- `output_dir/transfer_prior.json`
- `output_dir/manifest.yaml`
- `output_dir/run_manifest.json`

### Required Logs
- `>>> Phase 0: Forward-NEAT pretraining on volleyball <<<`
- `>>> Phase 0.5: Condition ablation -> select transfer prior <<<`
- `>>> Phase 1: Downstream BackpropNEAT classification <<<`
- `USING_TRANSFER_PRIOR ...`
- `COND_APPLY ... codons=0/1 ...`
- decay enabled 時は `fitness_decay=1 ...`

## Tests

### `tests/test_run_parser.py`
- `allow_abbrev=False`
- shortened / ambiguous flag rejection
- plural filters parse
- plural filters が selection behavior に効く

### `tests/test_transfer_prior_manifest.py`
- `TransferPrior` round-trip
- `manifest.yaml` に required transfer-prior / backend / output metadata
- `run_manifest.json` に required transfer-prior / backend / output metadata

### `tests/test_condition_config.py`
- `full` vs `no_codons` の auditable difference
- codon audit payload に `enable_codons` または equivalent
- decay condition が `fitness_decay=True`
- decay parameter が surface される

### Extend Existing Tests
- Phase 0.5 が structured prior artifact を返す
- Phase 1 が `USING_TRANSFER_PRIOR` を log
- `--phase1-only` が saved prior を load して使える
- transfer-weight tests は raw tuple 期待から structured prior artifact へ更新

### Research Tests
- saved tracking data から HGT artifact emission が可能
- artifact 生成時 manifest が参照を持つ

## Deliverables

実装後は必ず以下を返す。

1. changed file list
2. what changed and why
3. transfer-prior flow の 1 paragraph 説明
4. `no_codons` audit path の 1 paragraph 説明
5. decay extension path の 1 paragraph 説明
6. HGT artifact wiring の 1 paragraph 説明
7. example commands:
   - minimal probe
   - full run
   - no_codons audit
   - phase1-only
   - decay-enabled run
8. unresolved assumptions / limitations

## Example Commands

Minimal probe:
`python -u submission/run.py --condition no_elite_cross --task xor --activation tanh --output-dir results/probe`

Full run:
`python -u submission/run.py --full --fresh --output-dir results/full_run`

no_codons audit:
`python -u submission/run.py --condition no_codons --task xor --activation tanh --output-dir results/check_nocodons`

phase1-only:
`python -u submission/run.py --phase1-only --transfer-prior-path results/full_run/transfer_prior.json --condition no_elite_cross --task xor --activation tanh --output-dir results/phase1_only_probe`

decay-enabled:
`python -u submission/run.py --condition full_with_decay --task xor --activation tanh --output-dir results/decay_probe`
