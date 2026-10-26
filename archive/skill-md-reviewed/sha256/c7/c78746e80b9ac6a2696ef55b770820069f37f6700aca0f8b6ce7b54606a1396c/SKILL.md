---
name: comprehensive-moonshot-pipeline-system
description: Comprehensive Moonshot Pipeline system integrating web deepresearch (multi-engine search, recursive analysis, contradiction resolution), parallel subagent execution, scientific rigor with multiple comparison correction (Bonferroni/FDR/Holm), ABC testing with error bars, GGUF FP16 evaluation, and AEGIS v2.5 development. Use when executing complex ML pipelines, conducting research-backed planning, running parallel evaluations with statistical validation, or managing multi-phase model development requiring rigorous statistical analysis.
---

# Comprehensive Moonshot Pipeline System

## Overview

This skill integrates multiple advanced capabilities into a unified Moonshot Pipeline system: web deepresearch, parallel subagent execution, scientific rigor, ABC testing, GGUF FP16 evaluation, and AEGIS v2.5 development management.

## Core Components

### 1. Web Deepresearch Integration
- **Browser-based research**: Use Cursor's MCP browser tools for comprehensive research
- **Multi-source validation**: Cross-reference 3+ sources for credibility
- **Research-informed planning**: Create plans based on research findings
- **Multi-engine search**: Google, Bing, DuckDuckGo, Google Scholar, ArXiv integration
- **Recursive information gathering**: Depth-first exploration with quality thresholds
- **Contradiction resolution**: Multi-source validation and evidence-based consensus
- **Structured research reports**: Executive summaries, timeline analysis, trend forecasting

### 2. Parallel Subagent Execution
- **Async delegation**: Delegate tasks to specialized subagents concurrently
- **Dependency management**: Handle task dependencies and ordering
- **Resource optimization**: Control concurrent execution limits

### 3. Scientific Rigor
- **Statistical evaluation**: n=10 seeds with t-distribution confidence intervals
- **Error bars**: Standard deviation visualization
- **Effect size**: Cohen's d calculation
- **Significance testing**: p-value based validation
- **Multiple comparison correction**: Bonferroni, FDR (Benjamini-Hochberg), Holm-Bonferroni

### 4. ABC Testing System
- **Multi-model comparison**: A (baseline), B (Borea-phi3.5), C (Moonshot result)
- **Industry benchmarks**: GSM8K, MATH, ARC-Challenge, ELYZA Tasks 100
- **Visualization**: Error bar charts with statistical significance
- **Performance tracking**: Historical comparison and improvement detection

### 5. GGUF FP16 Evaluation
- **Memory efficiency**: 50% VRAM reduction (7.5GB → 3.8GB)
- **Fast loading**: 60% faster model loading
- **Stable execution**: CUDA memory optimization
- **Format support**: GGUF/Transformers dual compatibility

### 6. Moonshot Pipeline Management
- **Data collection**: Arxiv top 50K, defense/JAXA whitepapers
- **SFT training**: Supervised fine-tuning with collected data
- **Advanced techniques**: DeepseekGLPO, mHC, SO8T, imatrix
- **HF upload**: Conditional upload on performance improvement

## Integrated Workflow

### Phase 1: Research and Planning

```python
# Web deepresearch for planning (multi-engine search)
from scripts.deep_research import DeepResearchEngine

# Initialize deep research engine
research_engine = DeepResearchEngine(
    sources=["google", "bing", "duckduckgo", "scholar", "arxiv"],
    min_sources=3,
    credibility_threshold=0.8
)

# Comprehensive research query
research_results = await research_engine.comprehensive_research(
    query="best practices for [task] implementation 2025-2026",
    depth="comprehensive",
    max_sources=50,
    timeline_analysis=True,
    contradiction_analysis=True
)

# Browser-based validation (Cursor MCP tools)
browser_search(query="best practices for [task]")
tabs = browser_tabs(action="list")

research_data = []
for tab in tabs[:5]:
    browser_navigate(url=tab["url"])
    browser_lock()
    snapshot = browser_snapshot()
    research_data.append(extract_research_data(snapshot))
    browser_unlock()

# Synthesize multi-source research
synthesized_research = synthesize_research(research_results, research_data)

# Create research-informed plan
plan = create_research_plan(task, synthesized_research)
todo_write(merge=False, todos=plan["steps"])
```

### Phase 2: Parallel Data Collection

```python
# Parallel subagent execution for data collection
tasks = [
    SubAgentTask(
        task_id="arxiv_collection",
        subagent_type="data_collector",
        prompt="Collect top 50K Arxiv papers",
        priority=1
    ),
    SubAgentTask(
        task_id="whitepaper_collection",
        subagent_type="web_researcher",
        prompt="Collect defense/JAXA whitepapers",
        priority=1
    ),
    SubAgentTask(
        task_id="dataset_verification",
        subagent_type="dataset_validator",
        prompt="Verify NSFW/drug detection datasets",
        priority=2,
        dependencies=["arxiv_collection"]
    )
]

orchestrator = SubAgentOrchestrator(max_concurrent=3)
results = await orchestrator.execute_parallel(tasks, delegate_via_task_tool)
```

### Phase 3: SFT Training

```python
# SFT with collected data
pipeline = EnhancedMoonshotPipeline(
    boreas_model_path="AXCXEPT/Borea-Phi-3.5-mini-Instruct-Jp"
)

pipeline.execute_sft_rlpo_integration()
```

### Phase 4: Advanced Techniques Integration

```python
# Integrate 2025-2026 advanced techniques
config = {
    "enable_deepseek_grpo": True,
    "enable_mhc_manifold": True,
    "enable_so8t": True,
    "enable_geometric_scaling": True,
    "enable_imatrix_protection": True
}

pipeline.execute_complete_moonshot_pipeline(config)
```

### Phase 5: Scientific ABC Testing

```python
# ABC testing with scientific rigor
abc_test_config = {
    "models": {
        "A": {"name": "baseline", "path": "models/baseline"},
        "B": {"name": "Borea-phi3.5", "path": "models/borea"},
        "C": {"name": "Moonshot-result", "path": "models/moonshot_result"}
    },
    "benchmarks": ["gsm8k", "math", "arc_challenge", "elyza_tasks"],
    "seeds": 10,  # n=10 for statistical rigor
    "confidence_level": 0.95,
    "effect_size": True
}

abc_results = execute_scientific_abc_test(abc_test_config)

# Generate error bar charts
generate_abc_error_bar_charts(abc_results)
```

### Phase 6: GGUF FP16 Evaluation

```python
# GGUF FP16 evaluation for memory efficiency
gguf_config = {
    "model_path": "models/moonshot_result",
    "format": "fp16",
    "n_gpu_layers": -1,
    "n_ctx": 4096
}

gguf_results = evaluate_with_gguf(gguf_config, abc_test_config["benchmarks"])
```

### Phase 7: Performance Comparison and HF Upload

```python
# Compare with previous results
improved = compare_performance(abc_results, previous_results)

if improved:
    # Upload HF standard files + BF16 GGUF
    upload_to_hf(
        model_path="models/moonshot_result",
        formats=["safetensors", "bf16_gguf"],
        include_evaluation_results=True
    )
```

## Scientific Rigor Implementation

### Statistical Evaluation

```python
def scientific_evaluation(scores: List[float], baseline: float):
    """科学的厳密性のある評価"""
    import numpy as np
    from scipy import stats

    n = len(scores)
    mean_score = np.mean(scores)
    std_score = np.std(scores, ddof=1)

    # t分布による95%信頼区間 (df=n-1)
    t_critical = stats.t.ppf(0.975, df=n-1)
    ci_95 = t_critical * std_score / np.sqrt(n)

    # Cohen's d効果量
    cohens_d = (mean_score - baseline) / std_score

    # t検定
    t_stat, p_value = stats.ttest_1samp(scores, baseline)

    return {
        "mean": mean_score,
        "std": std_score,
        "ci_95": ci_95,
        "cohens_d": cohens_d,
        "p_value": p_value,
        "significant": p_value < 0.05
    }

def apply_multiple_comparison_correction(p_values: Dict[str, float],
                                        method: str = 'bonferroni') -> Dict[str, Any]:
    """
    多重比較補正を適用

    Args:
        p_values: ベンチマーク名をキー、p値を値とする辞書
        method: 補正方法（'bonferroni', 'fdr', 'holm'）

    Returns:
        補正後のp値とメタデータの辞書
    """
    import numpy as np

    if method == 'bonferroni':
        # Bonferroni補正: α/m (m=比較数)
        n_comparisons = len(p_values)
        alpha = 0.05 / n_comparisons if n_comparisons > 0 else 0.05
        corrected_p_values = {k: min(v * n_comparisons, 1.0)
                            for k, v in p_values.items()}
        return {
            'corrected_p_values': corrected_p_values,
            'alpha': alpha,
            'method': 'bonferroni',
            'n_comparisons': n_comparisons
        }

    elif method == 'fdr':
        # FDR補正（Benjamini-Hochberg法）
        sorted_p = sorted(p_values.items(), key=lambda x: x[1])
        n = len(sorted_p)
        corrected_p_values = {}

        for i, (benchmark, p_value) in enumerate(sorted_p):
            rank = i + 1
            corrected_p = min(p_value * n / rank, 1.0)
            corrected_p_values[benchmark] = corrected_p

        return {
            'corrected_p_values': corrected_p_values,
            'alpha': 0.05,
            'method': 'fdr_benjamini_hochberg',
            'n_comparisons': n
        }

    elif method == 'holm':
        # Holm-Bonferroni補正（ステップダウン法）
        sorted_p = sorted(p_values.items(), key=lambda x: x[1])
        n = len(sorted_p)
        corrected_p_values = {}
        alpha = 0.05

        for i, (benchmark, p_value) in enumerate(sorted_p):
            rank = n - i  # 逆順ランク
            corrected_p = min(p_value * rank, 1.0)
            corrected_p_values[benchmark] = corrected_p

        return {
            'corrected_p_values': corrected_p_values,
            'alpha': alpha,
            'method': 'holm_bonferroni',
            'n_comparisons': n
        }

    else:
        raise ValueError(f"Unknown correction method: {method}. Use 'bonferroni', 'fdr', or 'holm'")
```

### Error Bar Visualization

```python
def create_error_bar_chart(models: List[str], means: Dict, errors: Dict):
    """エラーバー付きグラフ作成"""
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(12, 6))

    x_pos = np.arange(len(models))
    bars = ax.bar(x_pos, [means[m] for m in models],
                  yerr=[errors[m] for m in models],
                  capsize=8, alpha=0.7)

    # 値ラベル
    for i, (model, mean_val) in enumerate(zip(models, [means[m] for m in models])):
        ax.text(i, mean_val + errors[models[i]],
               f'{mean_val:.1f}', ha='center', va='bottom')

    ax.set_ylabel('Score (%)')
    ax.set_title('ABC Test Results with Error Bars')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('abc_test_error_bars.png', dpi=300)
```

## ABC Testing with Error Bars

### Test Execution

```python
async def execute_scientific_abc_test(config: Dict):
    """科学的厳密性のあるABCテスト（多重比較補正付き）"""
    results = {}
    all_p_values = {}

    for model_name, model_config in config["models"].items():
        model_scores = {}

        for benchmark in config["benchmarks"]:
            scores = []

            # 複数シードで評価
            for seed in range(config["seeds"]):
                score = evaluate_benchmark(
                    model_config["path"],
                    benchmark,
                    seed=seed
                )
                scores.append(score)

            # 統計分析
            stats = scientific_evaluation(scores, baseline_scores[benchmark])
            model_scores[benchmark] = stats

            # p値を収集（多重比較補正用）
            if model_name == "C":  # Moonshot結果のみ
                all_p_values[benchmark] = stats["p_value"]

        results[model_name] = model_scores

    # 多重比較補正適用
    correction_method = config.get("correction_method", "bonferroni")
    correction_results = apply_multiple_comparison_correction(
        all_p_values,
        method=correction_method
    )

    # 補正後の有意性判定
    for benchmark, corrected_p in correction_results["corrected_p_values"].items():
        if benchmark in results.get("C", {}):
            results["C"][benchmark]["corrected_p_value"] = corrected_p
            results["C"][benchmark]["significant_after_correction"] = (
                corrected_p < correction_results["alpha"]
            )

    # エラーバーグラフ生成（補正後p値も表示）
    generate_error_bar_charts(results, correction_results)

    return {
        "results": results,
        "correction": correction_results
    }
```

## GGUF FP16 Integration

### Memory-Efficient Evaluation

```python
def evaluate_with_gguf(model_path: str, benchmarks: List[str]):
    """GGUF FP16を使用したメモリ効率的評価"""
    from llama_cpp import Llama

    # GGUFモデルロード（メモリ効率的）
    model = Llama(
        model_path=f"{model_path}.gguf",
        n_gpu_layers=-1,  # 全レイヤーGPU
        n_ctx=4096,
        n_threads=8
    )

    results = {}
    for benchmark in benchmarks:
        scores = evaluate_benchmark_gguf(model, benchmark)
        results[benchmark] = scores

    return results
```

## Checkpoint and Recovery

### Automatic Checkpointing

```python
class PipelineCheckpoint:
    """パイプラインチェックポイント管理"""

    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_interval = 300  # 5 minutes
        self.max_backups = 3

    def save_checkpoint(self, phase: str, state: Dict):
        """チェックポイント保存（ローリングバックアップ）"""
        checkpoint = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "state": state
        }

        # ローリングバックアップ
        self._rotate_backups()

        # 保存
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{int(time.time())}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        # 最新リンク更新
        latest_link = self.checkpoint_dir / "latest_checkpoint.json"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(checkpoint_file.name)
```

## Integration Points

### Web Deepresearch → Plan Mode
- Research findings inform plan structure
- Source URLs documented in plan
- Research validation during execution

### Parallel Subagents → Data Collection
- Concurrent data collection tasks
- Specialized agents for different sources
- Result aggregation and synthesis

### Scientific Rigor → ABC Testing
- n=10 seeds for statistical validity
- Error bars for visualization
- Significance testing for improvements
- **Multiple comparison correction**: Bonferroni/FDR/Holm for multiple benchmarks
- Both uncorrected and corrected p-values reported
- Corrected p-values used for final significance decisions

### GGUF FP16 → Evaluation
- Memory-efficient model loading
- Stable execution on RTX 3080
- Fast evaluation cycles

## Best Practices

### Research Strategy
1. Start broad, then narrow focus
2. Validate with 3+ independent sources
3. Document source URLs
4. Check recency for fast-moving domains

### Parallel Execution
1. Identify independent tasks
2. Set appropriate concurrency limits
3. Handle dependencies correctly
4. Isolate failures

### Statistical Evaluation
1. Use n≥10 seeds for validity
2. Calculate t-distribution CIs
3. Report effect sizes (Cohen's d)
4. Visualize with error bars
5. **Apply multiple comparison correction** for multiple benchmarks:
   - **Bonferroni**: Conservative, α/m (m=comparisons)
   - **FDR (Benjamini-Hochberg)**: Less conservative, controls false discovery rate
   - **Holm-Bonferroni**: Step-down method, more powerful than Bonferroni
6. Report both uncorrected and corrected p-values
7. Use corrected p-values for significance decisions

### Memory Management
1. Use GGUF FP16 for evaluation
2. Monitor VRAM usage
3. Implement checkpointing
4. Clean up unused resources

## Example: Complete Pipeline

```python
async def execute_comprehensive_moonshot_pipeline():
    """統合ムーンショットパイプライン実行"""

    # 1. Research and planning
    research_plan = create_research_informed_plan("Moonshot Pipeline 2025-2026")

    # 2. Parallel data collection
    data_tasks = create_data_collection_tasks()
    data_results = await orchestrator.execute_parallel(data_tasks, delegate_fn)

    # 3. SFT training
    sft_model = execute_sft_training(data_results)

    # 4. Advanced techniques integration
    final_model = integrate_advanced_techniques(sft_model)

    # 5. Scientific ABC testing with multiple comparison correction
    abc_results = await execute_scientific_abc_test({
        "models": {"A": baseline, "B": borea, "C": final_model},
        "seeds": 10,
        "correction_method": "fdr"  # or "bonferroni", "holm"
    })

    # 6. GGUF FP16 evaluation
    gguf_results = evaluate_with_gguf(final_model, benchmarks)

    # 7. Performance comparison and upload
    if performance_improved(abc_results):
        upload_to_hf(final_model, formats=["safetensors", "bf16_gguf"])

    return {
        "research_plan": research_plan,
        "data_results": data_results,
        "sft_model": sft_model,
        "final_model": final_model,
        "abc_results": abc_results,
        "gguf_results": gguf_results
    }
```

---

*This skill integrates web deepresearch, parallel subagents, scientific rigor, ABC testing, GGUF FP16, and Moonshot Pipeline management into a unified system.*
