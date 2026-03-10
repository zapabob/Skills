---
name: dynamic-skill-dispatcher
description: Intelligent dynamic skill and MCP dispatching system for Codex. This skill should be used when dynamically selecting and executing skills or MCP servers based on task requirements, optimizing resource utilization, and enabling seamless integration across the Codex ecosystem. Use for intelligent task routing, cross-component communication, and adaptive workflow execution.
---

# Dynamic Skill Dispatcher

This skill provides intelligent dynamic dispatching capabilities for skills and MCP servers within the Codex ecosystem. It enables adaptive task routing, optimized resource utilization, and seamless cross-component integration for complex multi-step workflows.

## Core Features

### Intelligent Task Routing
- **Dynamic Target Selection**: Automatically select optimal skills/MCP servers based on task characteristics
- **Capability Matching**: Match task requirements with available component capabilities
- **Performance Optimization**: Route to highest-performing components for critical tasks
- **Load Balancing**: Distribute workload across available instances

### Cross-Component Communication
- **Unified Protocol**: Standardized communication protocol across all components
- **State Synchronization**: Real-time state sharing between skills and MCP servers
- **Error Propagation**: Intelligent error handling and recovery across components
- **Event-Driven Architecture**: Reactive responses to system events and changes

### Adaptive Workflow Execution
- **Runtime Optimization**: Adjust execution strategies based on real-time performance
- **Fallback Mechanisms**: Automatic fallback to alternative components on failure
- **Progressive Enhancement**: Start simple and enhance based on available capabilities
- **Self-Healing Systems**: Automatic problem detection and resolution

### Resource Optimization
- **Dynamic Resource Allocation**: Allocate resources based on task complexity and urgency
- **Caching Strategies**: Intelligent caching of frequently used components and data
- **Connection Pooling**: Efficient connection management for MCP servers
- **Memory Management**: Optimized memory usage across distributed components

## Usage Examples

### Dynamic Skill Execution
```bash
# タスクに基づいて最適なスキルを自動選択・実行
python tools/dynamic_skill_dispatcher.py dispatch-task \
  --task "analyze-code-security" \
  --code-path "src/auth/login.rs" \
  --auto-select \
  --performance-optimized
```

### Cross-Component Workflow
```bash
# 複数コンポーネントを協調させたワークフロー実行
python tools/dynamic_skill_dispatcher.py execute-workflow \
  --workflow "code-review-pipeline" \
  --components "qa-review,security-scan,performance-test" \
  --parallel-execution \
  --result-aggregation
```

### External AI Integration
```bash
# GeminiCLIやClaudeCode等の外部AIを動的呼び出し
python tools/dynamic_skill_dispatcher.py call-external-ai \
  --provider "gemini" \
  --task "code-optimization" \
  --code "complex_algorithm.py" \
  --context-compression \
  --token-optimization
```

### Adaptive Resource Allocation
```bash
# タスク特性に基づく動的リソース割り当て
python tools/dynamic_skill_dispatcher.py allocate-resources \
  --task-complexity "high" \
  --time-constraint "urgent" \
  --preferred-components "gpu-accelerated,high-memory" \
  --fallback-enabled
```

## Dynamic Dispatching Engine

### Task Analysis and Classification
```python
class TaskAnalyzer:
    def analyze_task_requirements(self, task: Dict) -> TaskProfile:
        # タスク特性分析
        complexity = self.assess_complexity(task)
        domain = self.identify_domain(task)
        resource_requirements = self.determine_resource_needs(task)
        time_sensitivity = self.evaluate_time_sensitivity(task)

        # スキル適合性スコアリング
        skill_scores = {}
        for skill_id, skill_profile in self.skill_registry.items():
            compatibility = self.calculate_compatibility(
                task_profile=TaskProfile(complexity, domain, resource_requirements, time_sensitivity),
                skill_profile=skill_profile
            )
            skill_scores[skill_id] = compatibility

        # MCP適合性スコアリング
        mcp_scores = {}
        for mcp_id, mcp_profile in self.mcp_registry.items():
            compatibility = self.calculate_mcp_compatibility(
                task_profile=TaskProfile(complexity, domain, resource_requirements, time_sensitivity),
                mcp_profile=mcp_profile
            )
            mcp_scores[mcp_id] = compatibility

        return TaskAnalysis(
            task_profile=TaskProfile(complexity, domain, resource_requirements, time_sensitivity),
            skill_scores=skill_scores,
            mcp_scores=mcp_scores,
            recommended_targets=self.select_top_candidates(skill_scores, mcp_scores)
        )
```

### Intelligent Target Selection
```python
class TargetSelector:
    def select_optimal_target(self, task_analysis: TaskAnalysis,
                            system_state: SystemState) -> DispatchTarget:
        # パフォーマンス指標取得
        performance_metrics = self.get_performance_metrics(system_state)

        # 負荷分散考慮
        load_distribution = self.analyze_load_distribution(system_state)

        # 可用性チェック
        availability_status = self.check_component_availability(system_state)

        # 総合評価による最適ターゲット選択
        optimal_target = self.calculate_optimal_target(
            task_analysis=task_analysis,
            performance_metrics=performance_metrics,
            load_distribution=load_distribution,
            availability_status=availability_status
        )

        return optimal_target

    def calculate_optimal_target(self, task_analysis: TaskAnalysis,
                               performance_metrics: Dict,
                               load_distribution: Dict,
                               availability_status: Dict) -> DispatchTarget:
        candidates = []

        # スキル候補評価
        for skill_id, score in task_analysis.skill_scores.items():
            if availability_status.get(f"skill:{skill_id}", False):
                adjusted_score = self.adjust_score_for_conditions(
                    base_score=score,
                    performance=performance_metrics.get(f"skill:{skill_id}", 1.0),
                    load=load_distribution.get(f"skill:{skill_id}", 0.0),
                    availability=True
                )
                candidates.append(DispatchCandidate(
                    target_type="skill",
                    target_id=skill_id,
                    score=adjusted_score,
                    reasoning=self.generate_selection_reasoning(skill_id, adjusted_score)
                ))

        # MCP候補評価
        for mcp_id, score in task_analysis.mcp_scores.items():
            if availability_status.get(f"mcp:{mcp_id}", False):
                adjusted_score = self.adjust_score_for_conditions(
                    base_score=score,
                    performance=performance_metrics.get(f"mcp:{mcp_id}", 1.0),
                    load=load_distribution.get(f"mcp:{mcp_id}", 0.0),
                    availability=True
                )
                candidates.append(DispatchCandidate(
                    target_type="mcp",
                    target_id=mcp_id,
                    score=adjusted_score,
                    reasoning=self.generate_selection_reasoning(mcp_id, adjusted_score)
                ))

        # 最適候補選択
        if not candidates:
            return DispatchTarget.fallback_target()

        best_candidate = max(candidates, key=lambda c: c.score)

        return DispatchTarget(
            target_type=best_candidate.target_type,
            target_id=best_candidate.target_id,
            confidence_score=best_candidate.score,
            selection_reasoning=best_candidate.reasoning,
            alternative_targets=self.get_alternative_targets(candidates, best_candidate)
        )
```

### Token Compression for Sub-Agent Communication
```python
class SubAgentTokenOptimizer:
    def __init__(self):
        self.semantic_compressor = SemanticCompressor()
        self.structural_compressor = StructuralCompressor()
        self.context_analyzer = ContextAnalyzer()

    async def optimize_tokens_for_sub_agent(self, context: Dict, target_agent: str) -> OptimizedContext:
        # エージェントプロファイル分析
        agent_profile = await self.analyze_agent_profile(target_agent)

        # コンテキスト重要度分析
        context_importance = await self.context_analyzer.analyze_importance(context, agent_profile)

        # 最適圧縮戦略選択
        compression_strategy = self.select_compression_strategy(agent_profile, context_importance)

        # 圧縮実行
        compressed_data = await self.execute_compression(context, compression_strategy)

        # 圧縮品質検証
        quality_metrics = await self.validate_compression_quality(context, compressed_data)

        # 最適化結果生成
        return OptimizedContext(
            original_size=self.calculate_token_size(context),
            compressed_size=self.calculate_token_size(compressed_data),
            compression_ratio=self.calculate_compression_ratio(context, compressed_data),
            estimated_savings=self.calculate_token_savings(context, compressed_data),
            decompression_metadata=self.generate_decompression_metadata(compressed_data, compression_strategy),
            quality_metrics=quality_metrics,
            compression_strategy=compression_strategy
        )

    async def execute_compression(self, context: Dict, strategy: CompressionStrategy) -> CompressedData:
        if strategy.algorithm == "semantic":
            return await self.semantic_compressor.compress(context, strategy.parameters)
        elif strategy.algorithm == "structural":
            return await self.structural_compressor.compress(context, strategy.parameters)
        else:
            # デフォルト: 構造的圧縮
            return await self.structural_compressor.compress(context, {})

    def select_compression_strategy(self, agent_profile: AgentProfile,
                                  context_importance: ContextImportance) -> CompressionStrategy:
        # エージェントの処理能力に基づく戦略選択
        if agent_profile.processing_capability == "high" and context_importance.critical_elements > 0.8:
            # 高性能エージェント + 重要コンテキスト → 軽量圧縮
            return CompressionStrategy(
                algorithm="lightweight",
                parameters={"preserve_critical": True, "compression_level": "low"}
            )
        elif agent_profile.token_efficiency == "high":
            # トークン効率の高いエージェント → セマンティック圧縮
            return CompressionStrategy(
                algorithm="semantic",
                parameters={"semantic_preservation": True, "context_window_optimization": True}
            )
        else:
            # デフォルト: 構造的圧縮
            return CompressionStrategy(
                algorithm="structural",
                parameters={"hierarchical_compression": True, "reference_preservation": True}
            )
```

### Execution Orchestration
```python
class ExecutionOrchestrator:
    def __init__(self, target_selector: TargetSelector,
                 token_optimizer: SubAgentTokenOptimizer,
                 result_aggregator: ResultAggregator):
        self.target_selector = target_selector
        self.token_optimizer = token_optimizer
        self.result_aggregator = result_aggregator
        self.execution_tracker = ExecutionTracker()

    async def execute_dynamic_dispatch(self, task: Dict, context: Dict) -> DispatchResult:
        # タスク分析
        task_analysis = await self.target_selector.analyze_task_requirements(task)

        # 最適ターゲット選択
        optimal_target = await self.target_selector.select_optimal_target(task_analysis)

        # トークン最適化（サブエージェントの場合）
        if optimal_target.target_type in ["agent", "external_ai"]:
            optimized_context = await self.token_optimizer.optimize_tokens_for_sub_agent(
                context, optimal_target.target_id
            )
            execution_context = optimized_context
        else:
            execution_context = context

        # 実行追跡開始
        execution_id = await self.execution_tracker.start_execution(task, optimal_target)

        try:
            # ターゲット別実行
            if optimal_target.target_type == "skill":
                result = await self.execute_skill(
                    optimal_target.target_id, task, execution_context
                )
            elif optimal_target.target_type == "mcp":
                result = await self.execute_mcp(
                    optimal_target.target_id, task, execution_context
                )
            elif optimal_target.target_type == "agent":
                result = await self.execute_agent(
                    optimal_target.target_id, task, execution_context
                )
            elif optimal_target.target_type == "external_ai":
                result = await self.execute_external_ai(
                    optimal_target.target_id, task, execution_context
                )
            else:
                raise ValueError(f"Unsupported target type: {optimal_target.target_type}")

            # 結果集計
            aggregated_result = await self.result_aggregator.aggregate_result(
                result, optimal_target, execution_context
            )

            # 実行完了記録
            await self.execution_tracker.complete_execution(execution_id, aggregated_result)

            return DispatchResult(
                success=True,
                result=aggregated_result,
                target_used=optimal_target,
                execution_metadata=self.execution_tracker.get_execution_metadata(execution_id)
            )

        except Exception as e:
            # エラーハンドリング
            error_result = await self.handle_execution_error(e, optimal_target, execution_id)
            await self.execution_tracker.fail_execution(execution_id, error_result)

            return DispatchResult(
                success=False,
                error=error_result,
                target_used=optimal_target,
                execution_metadata=self.execution_tracker.get_execution_metadata(execution_id)
            )
```

## Integration with Codex Ecosystem

### LLMOps Integration
- **Dynamic Model Selection**: Task requirements based model routing
- **Cost Optimization**: Efficient resource utilization across dispatches
- **Performance Learning**: Continuous improvement of dispatch decisions

### A2A Communication Enhancement
- **Intelligent Routing**: Smart message routing between agents
- **Protocol Optimization**: Efficient communication protocols
- **State Synchronization**: Real-time state sharing across components

### Orchestration Integration
- **Workflow Optimization**: Dynamic workflow restructuring based on dispatch results
- **Resource Coordination**: Coordinated resource allocation across orchestrated tasks
- **Adaptive Planning**: Real-time plan adjustments based on execution feedback

### Skill/MCP Integration
- **Unified Interface**: Consistent interface across skills and MCP servers
- **Resource Sharing**: Efficient resource utilization through intelligent sharing
- **Capability Discovery**: Dynamic discovery and utilization of component capabilities

### Plan Mode Integration
- **Execution Tracking**: Detailed tracking of dispatch operations within plans
- **Progress Integration**: Seamless integration with project progress tracking
- **Risk Mitigation**: Proactive risk identification and mitigation in dispatches

### Deep Research Integration
- **Knowledge Routing**: Intelligent routing of research queries to appropriate sources
- **Result Synthesis**: Aggregation and synthesis of results from multiple sources
- **Learning Integration**: Incorporation of research insights into dispatch decisions

## Advanced Features

### Predictive Dispatching
- **Historical Analysis**: Learning from past dispatch performance
- **Predictive Modeling**: Forecasting optimal dispatch targets
- **Adaptive Learning**: Continuous improvement of dispatch algorithms

### Multi-Modal Optimization
- **Performance Profiling**: Detailed performance analysis of dispatch operations
- **Bottleneck Identification**: Automatic detection and resolution of performance bottlenecks
- **Scalability Optimization**: Ensuring system performance at scale

### Intelligent Fallback Systems
- **Graceful Degradation**: Maintaining functionality when optimal targets unavailable
- **Alternative Routing**: Automatic routing to backup targets when primary targets fail
- **Recovery Optimization**: Learning from failures to improve future dispatch reliability

### Real-time Adaptation
- **Dynamic Reconfiguration**: Adapting to changing system conditions
- **Load-based Routing**: Routing decisions based on current system load
- **Quality-based Selection**: Selecting targets based on quality metrics and SLAs

## Performance Optimization

### Caching Strategies
```python
class DispatchCache:
    def __init__(self):
        self.target_cache = TTLCache(maxsize=1000, ttl=300)  # 5分TTL
        self.result_cache = TTLCache(maxsize=500, ttl=600)   # 10分TTL
        self.performance_cache = TTLCache(maxsize=200, ttl=1800)  # 30分TTL

    async def get_cached_target(self, task_signature: str) -> Optional[DispatchTarget]:
        return self.target_cache.get(task_signature)

    async def cache_target_selection(self, task_signature: str, target: DispatchTarget):
        self.target_cache[task_signature] = target

    async def get_similar_results(self, task_pattern: str) -> List[DispatchResult]:
        # パターンに基づく類似結果検索
        similar_keys = [key for key in self.result_cache.keys() if task_pattern in key]
        return [self.result_cache[key] for key in similar_keys if key in self.result_cache]
```

### Connection Pooling
```python
class ConnectionPoolManager:
    def __init__(self, max_connections_per_target: int = 10):
        self.pools = {}
        self.max_connections = max_connections_per_target
        self.connection_monitor = ConnectionMonitor()

    async def get_connection(self, target_id: str, target_type: str) -> Connection:
        pool_key = f"{target_type}:{target_id}"

        if pool_key not in self.pools:
            self.pools[pool_key] = ConnectionPool(
                max_connections=self.max_connections,
                target_id=target_id,
                target_type=target_type
            )

        pool = self.pools[pool_key]
        connection = await pool.acquire()

        # 接続監視
        await self.connection_monitor.track_connection(connection)

        return connection

    async def release_connection(self, connection: Connection):
        pool_key = f"{connection.target_type}:{connection.target_id}"
        if pool_key in self.pools:
            await self.pools[pool_key].release(connection)
            await self.connection_monitor.untrack_connection(connection)
```

## Quality Assurance

### Dispatch Validation
```python
class DispatchValidator:
    def validate_dispatch_decision(self, task: Dict, selected_target: DispatchTarget,
                                 system_state: SystemState) -> ValidationResult:
        # 決定論的検証
        deterministic_checks = self.perform_deterministic_validation(task, selected_target)

        # 確率的検証
        probabilistic_checks = self.perform_probabilistic_validation(task, selected_target, system_state)

        # パフォーマンス予測
        performance_prediction = self.predict_dispatch_performance(task, selected_target, system_state)

        # リスク評価
        risk_assessment = self.assess_dispatch_risks(task, selected_target, system_state)

        return ValidationResult(
            is_valid=all([
                deterministic_checks.passed,
                probabilistic_checks.passed,
                performance_prediction.acceptable,
                risk_assessment.acceptable_risk
            ]),
            deterministic_checks=deterministic_checks,
            probabilistic_checks=probabilistic_checks,
            performance_prediction=performance_prediction,
            risk_assessment=risk_assessment,
            confidence_score=self.calculate_validation_confidence(
                deterministic_checks, probabilistic_checks,
                performance_prediction, risk_assessment
            )
        )
```

### Continuous Learning
```python
class DispatchLearner:
    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.decision_optimizer = DecisionOptimizer()
        self.feedback_processor = FeedbackProcessor()

    async def learn_from_dispatch(self, dispatch_record: DispatchRecord):
        # パフォーマンス分析
        performance_insights = await self.performance_analyzer.analyze_dispatch_performance(dispatch_record)

        # 決定最適化
        optimization_suggestions = await self.decision_optimizer.generate_optimizations(
            dispatch_record, performance_insights
        )

        # フィードバック処理
        feedback_summary = await self.feedback_processor.process_feedback(dispatch_record)

        # 学習適用
        await self.apply_learning_insights(
            performance_insights, optimization_suggestions, feedback_summary
        )

        return LearningResult(
            performance_insights=performance_insights,
            optimization_suggestions=optimization_suggestions,
            feedback_summary=feedback_summary,
            applied_improvements=self.get_applied_improvements()
        )
```

## Success Metrics

### Operational Efficiency
- **Dispatch Success Rate**: > 98% successful dispatches
- **Average Dispatch Time**: < 500ms for target selection
- **Token Compression Ratio**: > 60% token reduction for sub-agent calls
- **Cache Hit Rate**: > 85% for repeated task patterns

### System Performance
- **Throughput**: > 100 dispatches per second under normal load
- **Latency**: < 2 seconds end-to-end for complex dispatches
- **Resource Utilization**: < 70% average CPU/memory usage
- **Scalability**: Linear performance scaling up to 1000 concurrent dispatches

### Quality Metrics
- **Decision Accuracy**: > 95% optimal target selection
- **Error Recovery Rate**: > 99% automatic error recovery
- **User Satisfaction**: > 4.8/5.0 user satisfaction with dispatch results
- **System Reliability**: 99.99% uptime

## Conclusion

The Dynamic Skill Dispatcher represents the intelligent orchestration layer of the Codex ecosystem. By providing adaptive, optimized, and reliable dispatching of tasks across skills, MCP servers, and external AI systems, it enables seamless integration and optimal performance across the entire AI development platform.

This skill serves as the nervous system of Codex, ensuring that every task finds its optimal execution path while maintaining system-wide efficiency, reliability, and intelligence. Through continuous learning and adaptation, it evolves to meet the changing needs of the ecosystem, providing increasingly sophisticated orchestration capabilities.