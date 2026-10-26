---
name: claudecode-parallel-subagents
description: Implement ClaudeCode-style parallel asynchronous subagent delegation for complex multi-task execution. Uses asyncio for concurrent task processing, Task tool for subagent delegation, and intelligent orchestration for coordination. Use when tasks can be parallelized, require specialized agents, or need concurrent execution across multiple domains.
---

# ClaudeCode Parallel Subagents

## Overview

This skill implements ClaudeCode-style parallel asynchronous subagent delegation for efficient concurrent task execution. It enables multiple specialized agents to work in parallel, coordinating their efforts through async/await patterns and intelligent orchestration.

## Core Features

### 1. Parallel Task Delegation
- **Async subagent execution**: Delegate tasks to specialized subagents concurrently
- **Task tool integration**: Use `Task` tool with `subagent_type` parameter
- **Concurrent coordination**: Manage multiple agents working simultaneously
- **Result aggregation**: Collect and synthesize results from parallel executions

### 2. Async/Await Patterns
- **asyncio.gather**: Execute multiple tasks in parallel
- **asyncio.create_task**: Create independent async tasks
- **asyncio.wait**: Wait for tasks with timeout and error handling
- **asyncio.Queue**: Coordinate task distribution

### 3. Subagent Orchestration
- **Agent specialization**: Assign tasks to specialized agents
- **Dependency management**: Handle task dependencies and ordering
- **Resource management**: Control concurrent agent limits
- **Error isolation**: Isolate failures to prevent cascade failures

## When to Use

Use parallel subagents when:
- ✅ Multiple independent tasks can run simultaneously
- ✅ Tasks require specialized agent capabilities
- ✅ Performance optimization through concurrency needed
- ✅ Tasks can be decomposed into parallel subtasks
- ✅ User explicitly requests parallel execution

Skip for:
- ❌ Sequential dependencies between tasks
- ❌ Single-task operations
- ❌ Tasks requiring strict ordering
- ❌ Resource-constrained environments

## Basic Pattern

### Simple Parallel Delegation

```python
import asyncio
from typing import List, Dict, Any

async def parallel_subagent_execution(tasks: List[Dict[str, Any]]):
    """並列サブエージェント実行"""

    # タスクを並列実行
    async_tasks = []
    for task in tasks:
        async_task = delegate_to_subagent(
            subagent_type=task["agent_type"],
            prompt=task["prompt"]
        )
        async_tasks.append(async_task)

    # 並列実行と結果収集
    results = await asyncio.gather(*async_tasks, return_exceptions=True)

    # 結果を処理
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Task {i} failed: {result}")
        else:
            successful_results.append(result)

    return successful_results
```

### Using Task Tool

```python
async def delegate_to_subagent(subagent_type: str, prompt: str):
    """Task toolを使用したサブエージェント委任"""
    # Task tool呼び出し（実際の実装では適切なツール呼び出しを使用）
    result = await call_task_tool(
        subagent_type=subagent_type,
        prompt=prompt
    )
    return result
```

## Advanced Patterns

### Pattern 1: Dependency-Aware Parallel Execution

```python
async def dependency_aware_parallel_execution(
    tasks: List[Dict[str, Any]],
    dependencies: Dict[str, List[str]]
):
    """依存関係を考慮した並列実行"""

    completed_tasks = set()
    task_results = {}

    while len(completed_tasks) < len(tasks):
        # 実行可能なタスクを特定
        ready_tasks = [
            task for task in tasks
            if task["id"] not in completed_tasks
            and all(dep in completed_tasks for dep in dependencies.get(task["id"], []))
        ]

        if not ready_tasks:
            # デッドロック検出
            raise RuntimeError("Circular dependency detected")

        # 並列実行
        async_tasks = []
        for task in ready_tasks:
            async_task = delegate_to_subagent(
                subagent_type=task["agent_type"],
                prompt=task["prompt"]
            )
            async_tasks.append((task["id"], async_task))

        # 実行と結果収集
        results = await asyncio.gather(
            *[task for _, task in async_tasks],
            return_exceptions=True
        )

        # 結果を保存
        for (task_id, _), result in zip(async_tasks, results):
            if not isinstance(result, Exception):
                task_results[task_id] = result
                completed_tasks.add(task_id)

    return task_results
```

### Pattern 2: Resource-Limited Parallel Execution

```python
async def resource_limited_parallel_execution(
    tasks: List[Dict[str, Any]],
    max_concurrent: int = 5
):
    """リソース制限付き並列実行"""

    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def execute_with_limit(task):
        async with semaphore:
            return await delegate_to_subagent(
                subagent_type=task["agent_type"],
                prompt=task["prompt"]
            )

    # すべてのタスクを並列実行（セマフォで制限）
    async_tasks = [execute_with_limit(task) for task in tasks]
    results = await asyncio.gather(*async_tasks, return_exceptions=True)

    return results
```

### Pattern 3: Priority-Based Parallel Execution

```python
import heapq
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PrioritizedTask:
    priority: int
    task: Dict[str, Any] = field(compare=False)

    def __lt__(self, other):
        return self.priority < other.priority

async def priority_based_parallel_execution(
    tasks: List[Dict[str, Any]],
    max_concurrent: int = 5
):
    """優先度ベースの並列実行"""

    # 優先度キューを作成
    priority_queue = [PrioritizedTask(task["priority"], task) for task in tasks]
    heapq.heapify(priority_queue)

    semaphore = asyncio.Semaphore(max_concurrent)
    results = {}

    async def execute_priority_task(prioritized_task):
        async with semaphore:
            result = await delegate_to_subagent(
                subagent_type=prioritized_task.task["agent_type"],
                prompt=prioritized_task.task["prompt"]
            )
            return prioritized_task.task["id"], result

    # 優先度順に実行
    async_tasks = []
    while priority_queue:
        prioritized_task = heapq.heappop(priority_queue)
        async_tasks.append(execute_priority_task(prioritized_task))

    task_results = await asyncio.gather(*async_tasks, return_exceptions=True)

    for result in task_results:
        if not isinstance(result, Exception):
            task_id, task_result = result
            results[task_id] = task_result

    return results
```

### Pattern 4: Streaming Results with Queue

```python
async def streaming_parallel_execution(
    tasks: List[Dict[str, Any]],
    result_queue: asyncio.Queue
):
    """ストリーミング結果の並列実行"""

    async def execute_and_stream(task):
        result = await delegate_to_subagent(
            subagent_type=task["agent_type"],
            prompt=task["prompt"]
        )
        await result_queue.put({
            "task_id": task["id"],
            "result": result,
            "status": "completed"
        })
        return result

    # 並列実行
    async_tasks = [execute_and_stream(task) for task in tasks]

    # バックグラウンドで実行
    gather_task = asyncio.create_task(
        asyncio.gather(*async_tasks, return_exceptions=True)
    )

    # 結果をストリーミング
    while not gather_task.done() or not result_queue.empty():
        try:
            result = await asyncio.wait_for(result_queue.get(), timeout=1.0)
            yield result
        except asyncio.TimeoutError:
            continue

    # 最終結果を取得
    await gather_task
```

## Subagent Orchestrator

### Complete Orchestrator Implementation

```python
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class SubAgentTask:
    """サブエージェントタスク"""
    task_id: str
    subagent_type: str
    prompt: str
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class SubAgentResult:
    """サブエージェント結果"""
    task_id: str
    status: str  # "completed", "failed", "timeout"
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0

class SubAgentOrchestrator:
    """サブエージェントオーケストレーター"""

    def __init__(
        self,
        max_concurrent: int = 5,
        default_timeout: float = 300.0
    ):
        self.max_concurrent = max_concurrent
        self.default_timeout = default_timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.task_results: Dict[str, SubAgentResult] = {}
        self.completed_tasks: set = set()

    async def execute_task(
        self,
        task: SubAgentTask,
        delegate_fn: Callable
    ) -> SubAgentResult:
        """単一タスク実行"""
        start_time = datetime.now()

        async with self.semaphore:
            try:
                # タイムアウト付き実行
                result = await asyncio.wait_for(
                    delegate_fn(task.subagent_type, task.prompt),
                    timeout=task.timeout or self.default_timeout
                )

                execution_time = (datetime.now() - start_time).total_seconds()

                return SubAgentResult(
                    task_id=task.task_id,
                    status="completed",
                    result=result,
                    execution_time=execution_time
                )

            except asyncio.TimeoutError:
                execution_time = (datetime.now() - start_time).total_seconds()
                return SubAgentResult(
                    task_id=task.task_id,
                    status="timeout",
                    result=None,
                    error="Task timeout",
                    execution_time=execution_time
                )

            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                return SubAgentResult(
                    task_id=task.task_id,
                    status="failed",
                    result=None,
                    error=str(e),
                    execution_time=execution_time
                )

    async def execute_parallel(
        self,
        tasks: List[SubAgentTask],
        delegate_fn: Callable
    ) -> Dict[str, SubAgentResult]:
        """並列タスク実行"""

        # 依存関係を考慮した実行順序決定
        execution_order = self._determine_execution_order(tasks)

        # フェーズごとに実行
        for phase_tasks in execution_order:
            # フェーズ内で並列実行
            async_tasks = [
                self.execute_task(task, delegate_fn)
                for task in phase_tasks
            ]

            results = await asyncio.gather(*async_tasks, return_exceptions=True)

            # 結果を保存
            for result in results:
                if isinstance(result, SubAgentResult):
                    self.task_results[result.task_id] = result
                    self.completed_tasks.add(result.task_id)
                elif isinstance(result, Exception):
                    logger.error(f"Task execution exception: {result}")

        return self.task_results

    def _determine_execution_order(
        self,
        tasks: List[SubAgentTask]
    ) -> List[List[SubAgentTask]]:
        """実行順序を決定（依存関係を考慮）"""
        task_dict = {task.task_id: task for task in tasks}
        execution_phases = []
        completed = set()

        while len(completed) < len(tasks):
            # 実行可能なタスクを特定
            ready_tasks = [
                task for task in tasks
                if task.task_id not in completed
                and all(dep in completed for dep in task.dependencies)
            ]

            if not ready_tasks:
                # デッドロック検出
                remaining = [t.task_id for t in tasks if t.task_id not in completed]
                raise RuntimeError(f"Circular dependency detected. Remaining: {remaining}")

            # 優先度でソート
            ready_tasks.sort(key=lambda t: t.priority, reverse=True)
            execution_phases.append(ready_tasks)
            completed.update(t.task.task_id for task in ready_tasks)

        return execution_phases

    async def execute_with_retry(
        self,
        task: SubAgentTask,
        delegate_fn: Callable
    ) -> SubAgentResult:
        """リトライ付きタスク実行"""
        last_result = None

        for attempt in range(task.max_retries + 1):
            result = await self.execute_task(task, delegate_fn)

            if result.status == "completed":
                return result

            last_result = result
            task.retry_count = attempt + 1

            if attempt < task.max_retries:
                # 指数バックオフ
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                logger.info(f"Retrying task {task.task_id} (attempt {attempt + 1})")

        return last_result
```

## Integration with Cursor Task Tool

### Task Tool Delegation

```python
async def delegate_via_task_tool(
    subagent_type: str,
    prompt: str,
    timeout: float = 300.0
) -> Dict[str, Any]:
    """Task toolを使用したサブエージェント委任"""

    # Task tool呼び出し（実際の実装では適切なツール呼び出しを使用）
    # ここでは疑似コードとして表現
    try:
        result = await asyncio.wait_for(
            call_task_tool_async(
                subagent_type=subagent_type,
                prompt=prompt
            ),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        raise TimeoutError(f"Subagent {subagent_type} timeout")
    except Exception as e:
        raise RuntimeError(f"Subagent {subagent_type} error: {e}")
```

## Error Handling

### Graceful Degradation

```python
async def execute_with_fallback(
    primary_task: SubAgentTask,
    fallback_task: Optional[SubAgentTask],
    delegate_fn: Callable
) -> SubAgentResult:
    """フォールバック付き実行"""

    result = await orchestrator.execute_task(primary_task, delegate_fn)

    if result.status != "completed" and fallback_task:
        logger.warning(f"Primary task failed, using fallback: {primary_task.task_id}")
        result = await orchestrator.execute_task(fallback_task, delegate_fn)

    return result
```

### Error Isolation

```python
async def isolated_parallel_execution(
    tasks: List[SubAgentTask],
    delegate_fn: Callable
) -> Dict[str, SubAgentResult]:
    """エラー分離付き並列実行"""

    results = {}

    async def isolated_execute(task):
        try:
            return await orchestrator.execute_task(task, delegate_fn)
        except Exception as e:
            logger.error(f"Task {task.task_id} isolated error: {e}")
            return SubAgentResult(
                task_id=task.task_id,
                status="failed",
                result=None,
                error=str(e)
            )

    async_tasks = [isolated_execute(task) for task in tasks]
    task_results = await asyncio.gather(*async_tasks)

    for result in task_results:
        results[result.task_id] = result

    return results
```

## Best Practices

### Task Design
1. **Independent tasks**: Design tasks to be as independent as possible
2. **Clear interfaces**: Define clear input/output for each subagent
3. **Timeout settings**: Set appropriate timeouts for each task type
4. **Error handling**: Plan for failure scenarios
5. **Resource limits**: Consider system resources when setting concurrency

### Performance Optimization
1. **Batch similar tasks**: Group similar tasks for better resource utilization
2. **Priority ordering**: Execute high-priority tasks first
3. **Resource pooling**: Reuse connections/resources when possible
4. **Caching**: Cache results when appropriate
5. **Monitoring**: Track execution times and success rates

### Error Management
1. **Isolate failures**: Prevent one failure from affecting others
2. **Retry logic**: Implement exponential backoff retries
3. **Fallback strategies**: Provide fallback tasks when possible
4. **Error reporting**: Log errors with context
5. **Graceful degradation**: Continue with partial results when possible

## Example Usage

### Multi-Domain Parallel Processing

```python
async def process_multiple_domains():
    """複数ドメインの並列処理"""

    tasks = [
        SubAgentTask(
            task_id="research",
            subagent_type="research_agent",
            prompt="Research best practices for X",
            priority=1
        ),
        SubAgentTask(
            task_id="analysis",
            subagent_type="analysis_agent",
            prompt="Analyze data for Y",
            priority=2
        ),
        SubAgentTask(
            task_id="generation",
            subagent_type="generation_agent",
            prompt="Generate code for Z",
            priority=3,
            dependencies=["research", "analysis"]
        )
    ]

    orchestrator = SubAgentOrchestrator(max_concurrent=3)
    results = await orchestrator.execute_parallel(tasks, delegate_via_task_tool)

    return results
```

---

*This skill enables ClaudeCode-style parallel asynchronous subagent execution for efficient concurrent task processing.*
