---
name: multimodal-deepresearch-revolution
description: Multimodal Deep Research with Evolutionary Essence Extraction. Combines ViT vision analysis, audio processing, Arxiv integration, and ShinkaEvolve-OSINT bridge for revolutionary research that evolves or eliminates insights based on their essence.
---

# Multimodal Deep Research with Revolution

**進化的本質抽出によるマルチモーダル深層研究**

ViTによる視覚分析 + 動画/音声処理 + Arxiv連携 + ShinkaEvolve-OSINTブリッジ

## Core Concept / 核心概念

従来のDeep Researchは情報を集めるだけでした。このシステムは**本質を抽出し、進化させ、または淘汰します**。

入力された情報が本質的な洞察として進化するか、あるいはバイアス・ハルシネーション・不十分な証拠により淘汰されるかを厳密に判定します。

数学的な同型性（isomorphism）を検出し、異なる分野間の構造的類似性を明らかにします。

## Features / 機能

### 1. Multimodal Input / マルチモーダル入力
- **👁 Vision (ViT)**: 論文の図表、数式、ダイアグラムを解析
- **🔊 Audio**: 講演、ポッドキャスト、動画から洞察を抽出
- **📚 Arxiv**: 最新の論文をAPI経由で取得・解析
- **🌐 Web**: Exa.aiによるセマンティック検索

### 2. Essence Extraction / 本質抽出
各ソースから以下を抽出：
- **Core Claim**: 核心となる主張
- **Evidence**: 証拠
- **Assumptions**: 前提条件
- **Limitations**: 限界
- **Mathematical Isomorphisms**: 数学的同型性
- **Bias Indicators**: バイアス指標

### 3. Evolutionary Selection / 進化的選択
```
Generation 0: 初期エッセンス群
      ↓
Fitness評価 (Novelty × Validity × Utility × Coherence)
      ↓
Selection: 低適応度の淘汰
      ↓
Mutation: 生存者の組み合わせによる新エッセンス生成
      ↓
Generation N: 進化した高品質エッセンス群
```

### 4. ShinkaEvolve-OSINT Bridge
研究結果をShinkaEvolve-OSINTのIntel Labワークフローに変換：
- Workflow YAML生成
- Run Manifest作成
- Verifier設定の最適化
- 改善提案の自動生成

## Usage / 使用方法

### CLI

```bash
# 基本的な使用法
bun run src/index.ts "Quantum error correction advances"

# 革命レベルの深さ
bun run src/index.ts "Large language model reasoning" --depth revolutionary

# GPT-5使用
bun run src/index.ts "Neural network architectures" --model gpt5

# Arxivのみ
bun run src/index.ts "Transformer alternatives" --arxiv-only

# 出力指定
bun run src/index.ts "Cognitive architectures" --output ./my-research

# JSON出力も含める
bun run src/index.ts "Multi-agent systems" --json
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--depth` | Research depth: quick, normal, deep, revolutionary | normal |
| `--model` | LLM: claude, openai, gpt5 | claude |
| `--modality` | Input type: text, vision, audio, multimodal | multimodal |
| `--no-evolution` | Disable essence evolution | enabled |
| `--no-arxiv` | Disable Arxiv | enabled |
| `--no-shinka` | Disable Shinka bridge | enabled |
| `--output` | Output directory | ./research-output |
| `--json` | Save sources as JSON | false |

## Requirements / 要件

環境変数：
```bash
# Required
export ANTHROPIC_API_KEY="your-key"
# OR
export OPENAI_API_KEY="your-key"

# Optional (for enhanced features)
export FIRECRAWL_API_KEY="your-key"
```

## Output Structure / 出力構造

```
research-{timestamp}/
├── report.md              # メインレポート
├── report.json            # 構造化データ
├── essences.json          # 抽出された本質
├── shinka-workflow.yaml   # ShinkaEvolveワークフロー
└── run-manifest.json      # 実行マニフェスト
```

## Workflow Integration / ワークフロー統合

生成された`shinka-workflow.yaml`はそのままShinkaEvolve-OSINTで使用可能：

```yaml
roles:
  - Analyst
  - Skeptic
  - QuantChecker
  - Editor
  - IsomorphismDetector  # Deep Research特有
  - BiasAuditor         # Deep Research特有

steps:
  - retrieve:
      strategy: "Semantic + Structural search with isomorphism mapping"
  - essence_extraction:
      enable_evolution: true
      generations: 3
  # ...
```

## Example Output / 出力例

```
🧬 Multimodal Deep Research Revolution
=====================================

Topic: Transformer alternatives for long sequences
Depth: revolutionary
Model: claude
Modality: multimodal
Evolution: ✓
Arxiv: ✓
Shinka Bridge: ✓

🔍 Phase 1: Source Acquisition
   📚 Querying Arxiv...
   ✓ 20 papers from Arxiv
   👁 Vision analysis would run here (ViT integration)

🧠 Phase 2: Essence Extraction
   ✓ Extracted 47 essences

🧬 Phase 3: Evolutionary Selection
   Running 5 generations...
   ✓ Evolution complete

📊 Evolution Summary:
  Generation 0: 47 survivors, 0 eliminated, 23 mutations
  Generation 1: 35 survivors, 12 eliminated, 17 mutations
  Generation 2: 26 survivors, 9 eliminated, 13 mutations
  Generation 3: 20 survivors, 6 eliminated, 10 mutations
  Generation 4: 15 survivors, 5 eliminated, 7 mutations

✅ Research complete!
📄 Report saved to: ./research-output/research-1234567890
🔄 ShinkaEvolve-OSINT workflow generated
```

## Architecture / アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│              Input Layer (Multimodal)                    │
│  👁 Vision    🔊 Audio    📚 Arxiv    🌐 Web             │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Essence Extraction Engine                  │
│  Core Claim ← Evidence + Assumptions + Limitations     │
│  + Mathematical Isomorphisms + Bias Detection          │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Evolutionary Selection                     │
│  Fitness(novelty, validity, utility, coherence)        │
│  → Selection → Mutation → Next Generation              │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              ShinkaEvolve-OSINT Bridge                  │
│  Workflow YAML + Run Manifest + Improvement Suggestions │
└─────────────────────────────────────────────────────────┘
```

## References / 参考文献

- ShinkaEvolve: Evolutionary Code Optimization
- Exa.ai: Semantic Search API
- Arxiv API: Academic Paper Access
- GPT-4V: Vision Analysis
- Whisper: Audio Transcription

## License / ライセンス

MIT