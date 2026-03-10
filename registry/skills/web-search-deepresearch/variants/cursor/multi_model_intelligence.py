#!/usr/bin/env python3
"""
Multi-Model Intelligence - Manus/Genspark風AIエージェント
複数のAIモデルをインテリジェントに選択・統合する高度システム
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib

# 外部ライブラリ（必要に応じてインストール）
try:
    import openai
    import anthropic
    import google.generativeai as genai
except ImportError:
    # フォールバック
    print("Warning: AIライブラリが見つかりません。モック実装を使用します。")


class ModelProvider(Enum):
    """AIモデルプロバイダー"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    MOCK = "mock"


class TaskComplexity(Enum):
    """タスク複雑さ"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class ContentType(Enum):
    """コンテンツタイプ"""
    TEXT = "text"
    CODE = "code"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    RESEARCH = "research"
    TECHNICAL = "technical"


@dataclass
class ModelCapability:
    """モデル能力プロファイル"""
    provider: ModelProvider
    model_name: str
    context_window: int
    strengths: List[str]
    weaknesses: List[str]
    cost_per_token: float
    performance_score: float
    supported_types: List[ContentType]


@dataclass
class TaskAnalysis:
    """タスク分析結果"""
    complexity: TaskComplexity
    primary_type: ContentType
    secondary_types: List[ContentType]
    required_capabilities: List[str]
    estimated_tokens: int
    urgency: str
    context_length: int


@dataclass
class ModelSelection:
    """モデル選択結果"""
    primary_model: ModelCapability
    fallback_models: List[ModelCapability]
    reasoning: str
    expected_performance: float
    estimated_cost: float
    execution_strategy: str


class MultiModelIntelligence:
    """
    マルチモデルインテリジェンスシステム
    Manus/Genspark風の高度なモデル選択・統合システム
    GeminiCLI統合対応
    """

    def __init__(self):
        self.logger = logging.getLogger("MultiModelIntelligence")

        # モデル能力データベース
        self.model_capabilities = self._initialize_model_capabilities()

        # パフォーマンス履歴
        self.performance_history = {}

        # 学習データ
        self.learning_data = {}

        # コスト最適化設定
        self.cost_optimization = True
        self.performance_priority = 0.7  # 0.0-1.0 (コスト vs パフォーマンス)

        # GeminiCLI統合
        self.gemini_integration = None
        self.gemini_available = False

    async def initialize_gemini_integration(self):
        """GeminiCLI統合初期化"""
        try:
            self.logger.info("GeminiCLI統合初期化開始")

            # GeminiCLI Skillの動的importと初期化
            try:
                from gemini_cli_skill import GeminiCLISkill, GeminiCLIConfig

                config = GeminiCLIConfig()
                self.gemini_integration = GeminiCLISkill(config)

                # 初期化
                success = await self.gemini_integration.initialize()
                if success:
                    self.gemini_available = True

                    # GeminiCLIモデルをモデル能力データベースに追加
                    gemini_model = self._create_gemini_model_capability()
                    self.model_capabilities["gemini_cli"] = gemini_model

                    # A2Aネットワークに登録
                    await self.gemini_integration.register_with_a2a_network()

                    self.logger.info("GeminiCLI統合初期化完了")
                    return True
                else:
                    self.logger.warning("GeminiCLI初期化失敗")
                    return False

            except ImportError as e:
                self.logger.warning(f"GeminiCLI Skill import失敗: {e}")
                self.logger.info("GeminiCLI統合をスキップ")
                return False

        except Exception as e:
            self.logger.error(f"GeminiCLI統合初期化エラー: {e}")
            return False

    def _create_gemini_model_capability(self) -> ModelCapability:
        """GeminiCLIモデル能力定義"""
        return ModelCapability(
            provider=ModelProvider.GOOGLE,
            model_name="gemini-cli",
            context_window=32768,  # Geminiの制限に基づく
            strengths=[
                "creativity", "reasoning", "multilingual",
                "real_time_streaming", "markdown_support",
                "cost_effective", "fast_response"
            ],
            weaknesses=[
                "local_execution", "api_rate_limits",
                "context_length_restrictions", "cli_dependency"
            ],
            cost_per_token=0.00025,  # Gemini APIコスト
            performance_score=0.85,
            supported_types=[
                ContentType.TEXT, ContentType.ANALYSIS,
                ContentType.RESEARCH, ContentType.CREATIVE
            ]
        )

    def _initialize_model_capabilities(self) -> Dict[str, ModelCapability]:
        """モデル能力データベース初期化"""
        return {
            "gpt4": ModelCapability(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                context_window=8192,
                strengths=["reasoning", "analysis", "code_generation", "multilingual"],
                weaknesses=["real_time", "cost"],
                cost_per_token=0.03,
                performance_score=0.95,
                supported_types=[ContentType.TEXT, ContentType.CODE, ContentType.ANALYSIS,
                               ContentType.RESEARCH, ContentType.TECHNICAL]
            ),

            "gpt4_turbo": ModelCapability(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4-turbo",
                context_window=128000,
                strengths=["long_context", "efficiency", "multimodal"],
                weaknesses=["complex_reasoning"],
                cost_per_token=0.01,
                performance_score=0.88,
                supported_types=[ContentType.TEXT, ContentType.CODE, ContentType.ANALYSIS,
                               ContentType.RESEARCH, ContentType.TECHNICAL]
            ),

            "claude3_opus": ModelCapability(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-opus",
                context_window=200000,
                strengths=["long_context", "reasoning", "analysis", "safety"],
                weaknesses=["code_generation"],
                cost_per_token=0.015,
                performance_score=0.92,
                supported_types=[ContentType.TEXT, ContentType.ANALYSIS, ContentType.RESEARCH,
                               ContentType.TECHNICAL]
            ),

            "claude3_sonnet": ModelCapability(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-sonnet",
                context_window=200000,
                strengths=["balance", "reasoning", "code_generation"],
                weaknesses=["very_long_context"],
                cost_per_token=0.003,
                performance_score=0.89,
                supported_types=[ContentType.TEXT, ContentType.CODE, ContentType.ANALYSIS,
                               ContentType.RESEARCH, ContentType.TECHNICAL]
            ),

            "gemini_pro": ModelCapability(
                provider=ModelProvider.GOOGLE,
                model_name="gemini-pro",
                context_window=32768,
                strengths=["multimodal", "creativity", "speed"],
                weaknesses=["reasoning_depth"],
                cost_per_token=0.00025,
                performance_score=0.82,
                supported_types=[ContentType.TEXT, ContentType.CREATIVE, ContentType.ANALYSIS]
            ),

            "local_llama": ModelCapability(
                provider=ModelProvider.LOCAL,
                model_name="llama-2-70b",
                context_window=4096,
                strengths=["privacy", "cost", "customization"],
                weaknesses=["performance", "context_limit"],
                cost_per_token=0.0,
                performance_score=0.75,
                supported_types=[ContentType.TEXT, ContentType.CODE, ContentType.ANALYSIS]
            )
        }

    async def select_model(self, task_description: str, context: Dict[str, Any] = None) -> ModelSelection:
        """
        タスクに最適なモデルを選択（GeminiCLI統合版）

        Args:
            task_description: タスク説明
            context: 実行コンテキスト

        Returns:
            モデル選択結果
        """
        # タスク分析
        task_analysis = await self.analyze_task(task_description, context)

        # 利用可能なモデル取得（GeminiCLIを含む）
        available_models = await self.get_available_models()

        # GeminiCLI優先チェック
        gemini_preferred = self._is_gemini_preferred(task_description, context)

        if gemini_preferred and self.gemini_available:
            # GeminiCLIが優先される場合
            gemini_model = self.model_capabilities.get("gemini_cli")
            if gemini_model:
                # GeminiCLIの実行可能性チェック
                if await self._check_gemini_availability(task_analysis):
                    fallback_models = self._select_fallback_models(gemini_model, available_models)

                    return ModelSelection(
                        primary_model=gemini_model,
                        fallback_models=fallback_models,
                        reasoning="GeminiCLI preferred for streaming and creativity",
                        expected_performance=self._estimate_performance(gemini_model, task_analysis),
                        estimated_cost=self._estimate_cost(gemini_model, task_analysis),
                        execution_strategy="mcp_streaming"
                    )

        # 標準的なモデル選択
        primary_model, reasoning = self._select_optimal_model(task_analysis, available_models)
        fallback_models = self._select_fallback_models(primary_model, available_models)

        # パフォーマンス・コスト見積もり
        expected_performance = self._estimate_performance(primary_model, task_analysis)
        estimated_cost = self._estimate_cost(primary_model, task_analysis)

        # 実行戦略決定
        execution_strategy = self._determine_execution_strategy(task_analysis, primary_model)

        return ModelSelection(
            primary_model=primary_model,
            fallback_models=fallback_models,
            reasoning=reasoning,
            expected_performance=expected_performance,
            estimated_cost=estimated_cost,
            execution_strategy=execution_strategy
        )

    async def analyze_task(self, task_description: str, context: Dict[str, Any] = None) -> TaskAnalysis:
        """タスク詳細分析"""
        # テキスト分析
        text_analysis = self._analyze_text_complexity(task_description)

        # コンテキスト分析
        context_analysis = self._analyze_context(context or {})

        # タスクタイプ分類
        task_types = self._classify_task_types(task_description)

        # 複雑さ評価
        complexity = self._assess_complexity(text_analysis, context_analysis, task_types)

        # 推定トークン数
        estimated_tokens = self._estimate_token_count(task_description, context_analysis)

        # 緊急度評価
        urgency = self._assess_urgency(task_description, context_analysis)

        return TaskAnalysis(
            complexity=complexity,
            primary_type=task_types[0] if task_types else ContentType.TEXT,
            secondary_types=task_types[1:],
            required_capabilities=self._extract_capabilities(task_types),
            estimated_tokens=estimated_tokens,
            urgency=urgency,
            context_length=context_analysis.get("length", 0)
        )

    async def get_available_models(self) -> List[ModelCapability]:
        """利用可能なモデルを取得"""
        # 実際の実装ではAPIキーの存在確認などを行う
        available = []
        for model in self.model_capabilities.values():
            # 簡易的な利用可能チェック
            if model.provider == ModelProvider.MOCK:
                available.append(model)
            # 実際にはAPIキーチェックを行う
        return list(self.model_capabilities.values())

    def _select_optimal_model(self, task_analysis: TaskAnalysis,
                            available_models: List[ModelCapability]) -> Tuple[ModelCapability, str]:
        """最適モデル選択"""
        best_model = None
        best_score = -1
        reasoning_parts = []

        for model in available_models:
            score = 0
            reasons = []

            # タイプ適合性スコア
            type_score = self._calculate_type_compatibility(model, task_analysis)
            score += type_score * 0.4
            if type_score > 0.7:
                reasons.append(f"タイプ適合性高い ({model.supported_types})")

            # 複雑さ適合性スコア
            complexity_score = self._calculate_complexity_compatibility(model, task_analysis.complexity)
            score += complexity_score * 0.3
            if complexity_score > 0.8:
                reasons.append(f"複雑さ処理能力: {task_analysis.complexity.value}")

            # コスト効率スコア
            cost_score = self._calculate_cost_efficiency(model, task_analysis)
            score += cost_score * (1 - self.performance_priority) * 0.3

            # コンテキスト長適合性
            context_score = self._calculate_context_compatibility(model, task_analysis)
            score += context_score * 0.1

            # パフォーマンス履歴考慮
            history_score = self._get_performance_history_score(model, task_analysis.primary_type)
            score += history_score * 0.2

            if score > best_score:
                best_score = score
                best_model = model
                reasoning_parts = reasons

        reasoning = f"最適モデル選択: {'; '.join(reasoning_parts)} (スコア: {best_score:.2f})"

        # デフォルトモデル選択（見つからない場合）
        if not best_model:
            best_model = available_models[0] if available_models else self.model_capabilities["gpt4"]
            reasoning = "デフォルトモデル選択（最適モデルが見つからない）"

        return best_model, reasoning

    def _select_fallback_models(self, primary_model: ModelCapability,
                              available_models: List[ModelCapability]) -> List[ModelCapability]:
        """フォールバックモデル選択"""
        fallbacks = []
        for model in available_models:
            if model != primary_model:
                # 異なるプロバイダーのモデルを優先
                if model.provider != primary_model.provider:
                    fallbacks.append(model)
                elif len(fallbacks) < 2:  # 最大2つのフォールバック
                    fallbacks.append(model)

        return fallbacks[:2]

    def _is_gemini_preferred(self, task: str, context: Dict[str, Any]) -> bool:
        """GeminiCLIが優先されるタスクの判定"""
        if not self.gemini_available:
            return False

        task_lower = task.lower()
        context = context or {}

        # GeminiCLIが適しているキーワード
        gemini_keywords = [
            "creative", "brainstorm", "stream", "real-time",
            "markdown", "multilingual", "gemini", "google",
            "creative writing", "story", "poem", "art",
            "design", "concept", "idea generation"
        ]

        # キーワードマッチング
        keyword_match = any(keyword in task_lower for keyword in gemini_keywords)

        # コンテキストベースの判定
        context_indicators = context.get("preferred_model", "").lower()
        context_match = "gemini" in context_indicators

        # ストリーミング要求
        streaming_requested = context.get("streaming_required", False) or context.get("streaming", False)

        # コスト優先
        cost_priority = context.get("cost_priority", False)

        # GeminiCLIの強みを活かす条件
        gemini_advantage = (
            keyword_match or
            context_match or
            streaming_requested or
            (cost_priority and len(task.split()) < 100)  # 短いタスクでコスト優先
        )

        if gemini_advantage:
            self.logger.debug(f"GeminiCLI preferred for task: {task[:50]}...")

        return gemini_advantage

    async def _check_gemini_availability(self, task_analysis: TaskAnalysis) -> bool:
        """GeminiCLIの利用可能性チェック"""
        if not self.gemini_integration:
            return False

        try:
            # タスクがGeminiCLIの能力範囲内かチェック
            if task_analysis.estimated_tokens > 30000:  # コンテキスト制限チェック
                return False

            # GeminiCLI Skillの状態チェック
            capabilities = await self.gemini_integration._get_capabilities()

            # ストリーミング対応チェック
            if task_analysis.urgency == "high" and not capabilities.get("streaming_supported", False):
                return False

            return True

        except Exception as e:
            self.logger.warning(f"GeminiCLI availability check failed: {e}")
            return False

    def _analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """テキスト複雑さ分析"""
        words = text.split()
        sentences = text.split('。')

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "has_technical_terms": any(term in text.lower() for term in
                                     ["api", "algorithm", "database", "neural", "quantum"]),
            "has_code_indicators": any(indicator in text for indicator in
                                     ["function", "class", "import", "def ", "const "])
        }

    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """コンテキスト分析"""
        length = 0
        if "history" in context:
            length = sum(len(str(msg)) for msg in context["history"])

        return {
            "length": length,
            "has_files": "files" in context and len(context["files"]) > 0,
            "has_images": "images" in context and len(context["images"]) > 0,
            "urgency": context.get("urgency", "normal"),
            "domain": context.get("domain", "general")
        }

    def _classify_task_types(self, task_description: str) -> List[ContentType]:
        """タスクタイプ分類"""
        types = []

        text_lower = task_description.lower()

        # 研究タイプ
        if any(word in text_lower for word in ["research", "調査", "analyze", "分析"]):
            types.append(ContentType.RESEARCH)

        # コードタイプ
        if any(word in text_lower for word in ["code", "function", "class", "プログラム"]):
            types.append(ContentType.CODE)

        # 分析タイプ
        if any(word in text_lower for word in ["analyze", "analysis", "解析", "data"]):
            types.append(ContentType.ANALYSIS)

        # クリエイティブタイプ
        if any(word in text_lower for word in ["create", "design", "creative", "創作"]):
            types.append(ContentType.CREATIVE)

        # テクニカルタイプ
        if any(word in text_lower for word in ["technical", "api", "system", "技術"]):
            types.append(ContentType.TECHNICAL)

        # デフォルトはテキスト
        if not types:
            types.append(ContentType.TEXT)

        return types

    def _assess_complexity(self, text_analysis: Dict, context_analysis: Dict,
                          task_types: List[ContentType]) -> TaskComplexity:
        """複雑さ評価"""
        score = 0

        # テキストベースの複雑さ
        if text_analysis["word_count"] > 100:
            score += 2
        elif text_analysis["word_count"] > 50:
            score += 1

        # 技術的複雑さ
        if text_analysis["has_technical_terms"]:
            score += 2
        if text_analysis["has_code_indicators"]:
            score += 1

        # コンテキスト複雑さ
        if context_analysis["length"] > 10000:
            score += 2
        elif context_analysis["length"] > 5000:
            score += 1

        if context_analysis["has_files"] or context_analysis["has_images"]:
            score += 1

        # タスクタイプ複雑さ
        complex_types = [ContentType.RESEARCH, ContentType.ANALYSIS, ContentType.TECHNICAL]
        if any(t in complex_types for t in task_types):
            score += 1

        # スコアに基づく複雑さ判定
        if score >= 5:
            return TaskComplexity.VERY_COMPLEX
        elif score >= 3:
            return TaskComplexity.COMPLEX
        elif score >= 1:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE

    def _estimate_token_count(self, task_description: str, context_analysis: Dict) -> int:
        """トークン数見積もり"""
        # 簡易見積もり: 1トークン ≈ 4文字
        text_tokens = len(task_description) // 4
        context_tokens = context_analysis["length"] // 4

        return text_tokens + context_tokens

    def _assess_urgency(self, task_description: str, context_analysis: Dict) -> str:
        """緊急度評価"""
        urgent_keywords = ["urgent", "asap", "immediately", "緊急", "急ぎ"]
        if any(word in task_description.lower() for word in urgent_keywords):
            return "high"

        if context_analysis.get("urgency") == "high":
            return "high"

        return "normal"

    def _extract_capabilities(self, task_types: List[ContentType]) -> List[str]:
        """必要な能力抽出"""
        capabilities = []

        type_capability_map = {
            ContentType.CODE: ["code_generation", "syntax_analysis"],
            ContentType.RESEARCH: ["information_synthesis", "source_evaluation"],
            ContentType.ANALYSIS: ["data_processing", "logical_reasoning"],
            ContentType.CREATIVE: ["creative_generation", "innovation"],
            ContentType.TECHNICAL: ["technical_expertise", "system_design"]
        }

        for task_type in task_types:
            if task_type in type_capability_map:
                capabilities.extend(type_capability_map[task_type])

        return list(set(capabilities))

    def _calculate_type_compatibility(self, model: ModelCapability, task_analysis: TaskAnalysis) -> float:
        """タイプ適合性計算"""
        if task_analysis.primary_type in model.supported_types:
            return 1.0

        # セカンダリタイプとの適合性
        for secondary_type in task_analysis.secondary_types:
            if secondary_type in model.supported_types:
                return 0.7

        return 0.3

    def _calculate_complexity_compatibility(self, model: ModelCapability, complexity: TaskComplexity) -> float:
        """複雑さ適合性計算"""
        # 高性能モデルは複雑なタスクに適する
        base_score = model.performance_score

        if complexity == TaskComplexity.VERY_COMPLEX and model.context_window > 50000:
            return min(base_score * 1.2, 1.0)
        elif complexity == TaskComplexity.COMPLEX and model.context_window > 10000:
            return min(base_score * 1.1, 1.0)

        return base_score

    def _calculate_cost_efficiency(self, model: ModelCapability, task_analysis: TaskAnalysis) -> float:
        """コスト効率計算"""
        estimated_cost = model.cost_per_token * task_analysis.estimated_tokens

        # コストスコア（低いほど良い）
        if estimated_cost < 0.01:
            return 1.0
        elif estimated_cost < 0.1:
            return 0.8
        elif estimated_cost < 1.0:
            return 0.6
        else:
            return 0.3

    def _calculate_context_compatibility(self, model: ModelCapability, task_analysis: TaskAnalysis) -> float:
        """コンテキスト長適合性計算"""
        required_context = task_analysis.context_length + task_analysis.estimated_tokens

        if required_context <= model.context_window:
            return 1.0
        elif required_context <= model.context_window * 1.5:
            return 0.7
        else:
            return 0.3

    def _get_performance_history_score(self, model: ModelCapability, content_type: ContentType) -> float:
        """パフォーマンス履歴スコア取得"""
        key = f"{model.model_name}_{content_type.value}"
        return self.performance_history.get(key, 0.5)

    def _estimate_performance(self, model: ModelCapability, task_analysis: TaskAnalysis) -> float:
        """パフォーマンス見積もり"""
        base_performance = model.performance_score

        # タスク適合性ボーナス
        if task_analysis.primary_type in model.supported_types:
            base_performance += 0.1

        # 複雑さペナルティ
        if task_analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
            if model.context_window < task_analysis.estimated_tokens * 2:
                base_performance -= 0.2

        return max(0.0, min(1.0, base_performance))

    def _estimate_cost(self, model: ModelCapability, task_analysis: TaskAnalysis) -> float:
        """コスト見積もり"""
        return model.cost_per_token * task_analysis.estimated_tokens

    def _determine_execution_strategy(self, task_analysis: TaskAnalysis, model: ModelCapability) -> str:
        """実行戦略決定"""
        if task_analysis.complexity == TaskComplexity.VERY_COMPLEX:
            return "parallel_processing"
        elif task_analysis.urgency == "high":
            return "prioritized_execution"
        elif task_analysis.estimated_tokens > model.context_window * 0.8:
            return "chunked_processing"
        else:
            return "standard_execution"

    async def execute_with_fallback(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        フォールバック付き実行（Manus/Genspark風 + GeminiCLI統合）
        """
        selection = await self.select_model(task_description, context)

        # GeminiCLI特別処理
        if (selection.primary_model.model_name == "gemini-cli" and
            self.gemini_available and self.gemini_integration):
            try:
                self.logger.info("GeminiCLI実行開始")
                result = await self.gemini_integration.execute_research_task(task_description, context)
                result["model_used"] = "gemini-cli"
                result["execution_strategy"] = selection.execution_strategy
                result["integration_method"] = "mcp_a2a"

                # パフォーマンス学習
                task_analysis = await self.analyze_task(task_description, context)
                await self._learn_from_execution(selection.primary_model, result, task_analysis)

                return result

            except Exception as e:
                self.logger.warning(f"GeminiCLI実行失敗: {e}")

                # GeminiCLIが失敗した場合は通常のモデル選択にフォールバック
                selection = await self.select_model(task_description, {**context, "exclude_gemini": True})

        # プライマリモデルで実行
        try:
            result = await self._execute_with_model(selection.primary_model, task_description, context)
            result["model_used"] = selection.primary_model.model_name
            result["execution_strategy"] = selection.execution_strategy

            # パフォーマンス学習
            task_analysis = await self.analyze_task(task_description, context)
            await self._learn_from_execution(selection.primary_model, result, task_analysis)

            return result

        except Exception as e:
            self.logger.warning(f"プライマリモデル実行失敗: {e}")

            # フォールバック実行
            for fallback_model in selection.fallback_models:
                try:
                    self.logger.info(f"フォールバックモデル使用: {fallback_model.model_name}")
                    result = await self._execute_with_model(fallback_model, task_description, context)
                    result["model_used"] = fallback_model.model_name
                    result["fallback_used"] = True
                    return result

                except Exception as fallback_error:
                    self.logger.warning(f"フォールバックモデル実行失敗: {fallback_error}")
                    continue

            # すべてのモデルが失敗
            return {
                "success": False,
                "error": "すべてのモデルで実行失敗",
                "attempted_models": [selection.primary_model.model_name] +
                                  [m.model_name for m in selection.fallback_models]
            }

    async def _execute_with_model(self, model: ModelCapability, task_description: str,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """指定モデルでの実行"""
        # モック実装（実際には各プロバイダーのAPIを呼び出し）
        self.logger.info(f"モデル実行: {model.model_name}")

        # シミュレートされた実行
        await asyncio.sleep(0.1)  # ネットワーク遅延シミュレーション

        return {
            "success": True,
            "response": f"Mock response from {model.model_name}",
            "model": model.model_name,
            "execution_time": 0.1,
            "tokens_used": len(task_description.split()) * 2
        }

    async def _learn_from_execution(self, model: ModelCapability, result: Dict[str, Any],
                                  task_analysis: TaskAnalysis):
        """実行からの学習"""
        if result.get("success"):
            key = f"{model.model_name}_{task_analysis.primary_type.value}"
            current_score = self.performance_history.get(key, 0.5)

            # シンプルな学習: 成功時はスコアを上げる
            new_score = min(1.0, current_score + 0.05)
            self.performance_history[key] = new_score

            self.logger.debug(f"学習更新: {key} = {new_score}")


# グローバルインスタンス
_multi_model_instance = None

def get_multi_model_intelligence() -> MultiModelIntelligence:
    """シングルトンインスタンス取得"""
    global _multi_model_instance
    if _multi_model_instance is None:
        _multi_model_instance = MultiModelIntelligence()
    return _multi_model_instance


async def main():
    """テスト用メイン関数"""
    intelligence = get_multi_model_intelligence()

    test_tasks = [
        "PythonでシンプルなWebスクレイパーを書いてください",
        "量子コンピューティングの最新トレンドを調査・分析してください",
        "機械学習モデルのバイアスを軽減する方法について詳しく説明してください",
        "Reactコンポーネントのデザインシステムを作成してください"
    ]

    for task in test_tasks:
        print(f"\n=== タスク: {task[:50]}... ===")

        # モデル選択
        selection = await intelligence.select_model(task)
        print(f"選択モデル: {selection.primary_model.model_name}")
        print(f"理由: {selection.reasoning}")
        # print(".2f")  # 不要な行をコメントアウトまたは削除
        # print(".4f")  # 不要な行をコメントアウトまたは削除
        # 実行（モック）
        result = await intelligence.execute_with_fallback(task)
        print(f"実行結果: {'成功' if result.get('success') else '失敗'}")

if __name__ == "__main__":
    asyncio.run(main())