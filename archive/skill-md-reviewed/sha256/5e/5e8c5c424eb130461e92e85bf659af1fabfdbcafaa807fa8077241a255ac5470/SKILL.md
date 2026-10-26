---
name: shinka-mcp-skill-hub
description: Unified MCP Skill Hub integrating SpecStory Guard, Deep Research Revolution, and ShinkaEvolve OSINT with cross-skill orchestration
---

# ShinkaEvolve MCP Skill Hub

**統合スキルプラットフォーム**

MCP (Model Context Protocol) を通じて複数のスキルを統合し、スキル間の連携を実現します。

## 統合スキル一覧

| スキル | タイプ | 説明 |
|--------|--------|------|
| `skill_specstory_scan` | Security | SpecStory履歴のセキュリティスキャン |
| `skill_deepresearch_run` | Research | マルチモーダル深層研究 |
| `skill_research_with_guard` | Orchestration | セキュリティチェック付き研究 |
| `skill_research_to_osint` | Orchestration | 研究成果のOSINT変換 |
| `skill_full_intelligence_pipeline` | Orchestration | 完全な知能収集パイプライン |

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                   MCP Clients                               │
│  Claude / Codex / ChatGPT / OpenCode / Gemini CLI          │
└─────────────────────────┬───────────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────▼───────────────────────────────────┐
│              Shinka MCP Skill Hub                           │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Security  │  │   Research  │  │   OSINT     │         │
│  │    Guard    │  │  Revolution │  │   Core      │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│              ┌───────────▼────────────┐                     │
│              │  Skill Orchestration   │                     │
│              │  - Pipeline execution  │                     │
│              │  - Context sharing     │                     │
│              │  - Artifact management │                     │
│              └────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## 使用方法

### 1. stdio モード

```bash
python shinka_mcp_skill_hub.py
```

### 2. HTTP モード

```bash
python shinka_mcp_skill_hub.py --http --port 8000
```

### 3. テスト実行

```bash
python shinka_mcp_skill_hub.py --test
```

## ツール詳細

### skill_specstory_scan

SpecStory履歴をスキャンしてシークレットを検出します。

**Input:**
```json
{
  "scan_type": "full" // "full", "quick", "staged"
}
```

**Output:**
```json
{
  "status": "clean" | "secrets_found",
  "findings": [...],
  "scanned_at": "2026-02-09T22:30:00"
}
```

### skill_deepresearch_run

マルチモーダル深層研究を実行します。

**Input:**
```json
{
  "topic": "Quantum error correction",
  "depth": "deep", // "quick", "normal", "deep", "revolutionary"
  "modality": "multimodal", // "text", "vision", "audio", "multimodal"
  "enable_evolution": true
}
```

**Output:**
```json
{
  "topic": "Quantum error correction",
  "essence_count": 15,
  "artifacts": {
    "report": ".../report.md",
    "essences": ".../essences.json"
  }
}
```

### skill_research_with_guard

セキュリティチェックを行った上で研究を実行します。

**パイプライン:**
1. SpecStory Guardでスキャン
2. クリーンな場合のみ研究実行
3. 結果を統合

### skill_research_to_osint

研究成果をOSINT評価形式に変換します。

**変換内容:**
- Essences → Evidence Blocks
- Workflow YAML読み込み
- MILSPEC準拠フォーマット

### skill_full_intelligence_pipeline

完全な知能収集パイプラインを実行します。

**パイプライン:**
```
Security Scan → Deep Research → OSINT Conversion
```

**Input:**
```json
{
  "topic": "AI safety in autonomous weapons",
  "enable_vision": true
}
```

## スキル連携 (Cross-Skill Orchestration)

### コンテキスト共有

スキル間で以下を共有できます:

- **Artifacts**: ファイル、データ、レポート
- **Metadata**: セッション情報、設定
- **Pipeline Results**: 実行履歴

### パイプライン実行

複数スキルを連続実行:

```python
# Python API例
from shinka_mcp_skill_hub import SkillRegistry, SkillContext

registry = SkillRegistry()
context = SkillContext(session_id="123", workspace="./workspace")

# パイプライン実行
results = registry.execute_pipeline("full_intelligence", {
    "topic": "Target topic"
}, context)
```

## MCP 設定

### Claude Code / Codex

`.claude/mcp.json`:
```json
{
  "mcpServers": {
    "shinka-skill-hub": {
      "command": "python",
      "args": ["/path/to/shinka_mcp_skill_hub.py"]
    }
  }
}
```

### ChatGPT (HTTP)

`.chatgpt/mcp.json`:
```json
{
  "mcpServers": {
    "shinka-skill-hub": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## 環境変数

```bash
# API Keys
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."

# Optional
export FIRECRAWL_API_KEY="..."
export EXA_API_KEY="..."
```

## 特徴

### 1. 動的ツール登録

新しいスキルを簡単に追加:

```python
registry.register(
    name="my_new_skill",
    skill_type=SkillType.RESEARCH,
    handler=my_handler,
    schema={...},
    description="..."
)
```

### 2. 統一エラーハンドリング

すべてのスキルで共通のエラーフォーマット:

```json
{
  "error": "Error message",
  "traceback": "...",
  "skill": "skill_name"
}
```

### 3. 成果物管理

自動的に成果物を追跡・保存:

```python
context.add_artifact("research_result", data)
artifact = context.get_artifact("research_result")
```

## 今後の展開

- [ ] WebSocket対応
- [ ] 分散実行（複数マシン）
- [ ] スキルマーケットプレイス統合
- [ ] A/Bテストフレームワーク
- [ ] 自動最適化（進化）

## ライセンス

MIT License - ShinkaEvolve-OSINTプロジェクトと同様