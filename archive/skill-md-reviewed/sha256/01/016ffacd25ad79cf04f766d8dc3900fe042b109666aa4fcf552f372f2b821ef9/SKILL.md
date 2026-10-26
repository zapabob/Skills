---
name: cursor-claudecode-plan-mode
description: Create, manage, and execute comprehensive multi-step plans for complex tasks in Cursor/ClaudeCode style. Integrates web-search-deepresearch for intelligent research, adaptive planning with checkpoint recovery, and autonomous task execution. Use when tasks require multi-step coordination, research integration, risk management, or when explicitly requesting a plan/roadmap/phases.
---

# Cursor/ClaudeCode Plan Mode

## Overview

This skill provides Cursor/ClaudeCode-style plan mode capabilities for complex multi-step tasks. It combines intelligent planning with deep research integration, checkpoint management, and autonomous execution tracking.

## Core Features

### 1. Intelligent Plan Creation
- **Multi-step decomposition**: Break complex tasks into manageable steps
- **Dependency analysis**: Identify and order steps by dependencies
- **Research integration**: Use web-search-deepresearch for informed planning
- **Risk assessment**: Identify high-risk steps requiring special attention

### 2. Adaptive Execution
- **Checkpoint system**: Automatic saves every 5 minutes with rolling backups
- **Progress tracking**: Real-time status updates using `todo_write`
- **Error recovery**: Automatic retry and graceful degradation
- **Dynamic replanning**: Adjust plan based on execution results

### 3. Deep Research Integration
- **Pre-planning research**: Gather context before creating plan
- **Step-specific research**: Research requirements for each step
- **Validation research**: Verify assumptions and approaches
- **Multi-source validation**: Cross-reference information from multiple sources

## When to Use Plan Mode

Use plan mode when:
- ✅ Task has 3+ dependent steps
- ✅ Requires research or information gathering
- ✅ High-risk operations (data loss, breaking changes)
- ✅ Cross-cutting concerns (multiple files/components)
- ✅ User explicitly requests a plan/roadmap/phases
- ✅ Coordination needed between multiple systems

Skip plan mode for:
- ❌ Single-action tasks
- ❌ Trivial operations
- ❌ Straightforward refactoring
- ❌ Simple file edits

## Plan Creation Workflow

### Step 1: Research and Analysis

Before creating the plan, conduct research if needed:

```python
# Use web-search-deepresearch for context gathering
research_query = "best practices for [task domain]"
research_results = deep_research(research_query, sources=["scholar", "docs", "blogs"])

# Analyze current codebase state
codebase_analysis = analyze_codebase_structure()
```

### Step 2: Create Plan Structure

Create a plan with 3-7 clear, outcome-based steps:

```python
plan = {
    "id": "unique-plan-id",
    "title": "Clear plan title",
    "description": "What this plan accomplishes",
    "steps": [
        {
            "id": "1",
            "name": "Research and analyze requirements",
            "status": "pending",
            "dependencies": [],
            "research_needed": True,
            "estimated_time": "30min",
            "risk_level": "low"
        },
        {
            "id": "2",
            "name": "Design architecture",
            "status": "pending",
            "dependencies": ["1"],
            "research_needed": True,
            "estimated_time": "1h",
            "risk_level": "medium"
        },
        # ... more steps
    ],
    "checkpoint_interval": 300,  # 5 minutes
    "created_at": datetime.now().isoformat()
}
```

### Step 3: Initialize Tracking

Use `todo_write` to track plan execution:

```python
todos = [
    {"id": step["id"], "content": step["name"], "status": "pending"}
    for step in plan["steps"]
]
todo_write(merge=False, todos=todos)
```

## Plan Execution

### Progress Updates

Update todos as steps complete:

```python
# Mark step as in progress
todo_write(merge=True, todos=[
    {"id": "1", "status": "in_progress"}
])

# Complete step and start next
todo_write(merge=True, todos=[
    {"id": "1", "status": "completed"},
    {"id": "2", "status": "in_progress"}
])
```

### Checkpoint Management

Save checkpoints automatically:

```python
checkpoint = {
    "plan_id": plan["id"],
    "current_step": "2",
    "completed_steps": ["1"],
    "state": {
        "files_modified": ["file1.py", "file2.py"],
        "artifacts_created": ["output.json"],
        "errors_encountered": []
    },
    "timestamp": datetime.now().isoformat()
}

save_checkpoint(checkpoint)
```

### Research Integration

Conduct research for each step when needed:

```python
if step["research_needed"]:
    research_query = f"{step['name']} best practices implementation"
    research_results = deep_research(
        research_query,
        sources=["scholar", "docs", "stackoverflow"],
        depth="comprehensive"
    )

    # Use research results to inform step execution
    execute_step_with_research(step, research_results)
```

## Plan Revision

### When to Revise

Revise plan if:
- Scope changes significantly
- Dependencies discovered
- Better approach identified through research
- Execution reveals new requirements

### Revision Process

```python
# Identify needed changes
changes = analyze_execution_results(current_step, results)

# Update plan
revised_plan = update_plan(plan, changes)

# Update todos
todo_write(merge=True, todos=revised_plan["steps"])

# Document revision
log_plan_revision(plan["id"], changes, reason)
```

## Error Handling

### Retry Logic

```python
def execute_step_with_retry(step, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = execute_step(step)
            return result
        except TransientError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
            raise
        except PermanentError as e:
            # Update plan to handle error
            add_recovery_step(plan, step, e)
            break
```

### Graceful Degradation

```python
def execute_with_fallback(step, primary_method, fallback_method):
    try:
        return primary_method(step)
    except Exception as e:
        logger.warning(f"Primary method failed: {e}, using fallback")
        return fallback_method(step)
```

## Research-Enhanced Planning

### Pre-Planning Research

```python
def create_research_informed_plan(task_description):
    # Research task domain
    domain_research = deep_research(
        f"{task_description} implementation approaches",
        sources=["scholar", "docs", "github"],
        depth="comprehensive"
    )

    # Research best practices
    best_practices = deep_research(
        f"{task_description} best practices patterns",
        sources=["blogs", "docs", "stackoverflow"],
        depth="moderate"
    )

    # Create plan informed by research
    plan = synthesize_plan_from_research(
        task_description,
        domain_research,
        best_practices
    )

    return plan
```

### Step-Specific Research

```python
def execute_step_with_research(step):
    if step.get("research_needed"):
        # Research step-specific requirements
        research = deep_research(
            f"{step['name']} implementation details",
            sources=["docs", "examples", "tutorials"],
            depth="focused"
        )

        # Execute with research context
        return execute_step(step, research_context=research)
    else:
        return execute_step(step)
```

## Plan Templates

### Feature Development Plan

```python
feature_plan_template = {
    "steps": [
        {"name": "Research feature requirements", "research_needed": True},
        {"name": "Design feature architecture", "research_needed": True},
        {"name": "Implement core functionality", "research_needed": False},
        {"name": "Add unit tests", "research_needed": False},
        {"name": "Update documentation", "research_needed": False},
        {"name": "Integration testing", "research_needed": False}
    ]
}
```

### Refactoring Plan

```python
refactoring_plan_template = {
    "steps": [
        {"name": "Analyze current codebase", "research_needed": False},
        {"name": "Research refactoring patterns", "research_needed": True},
        {"name": "Design refactored architecture", "research_needed": True},
        {"name": "Implement refactoring incrementally", "research_needed": False},
        {"name": "Run test suite", "research_needed": False},
        {"name": "Verify functionality", "research_needed": False}
    ]
}
```

### Integration Plan

```python
integration_plan_template = {
    "steps": [
        {"name": "Research integration approaches", "research_needed": True},
        {"name": "Analyze integration points", "research_needed": False},
        {"name": "Design integration architecture", "research_needed": True},
        {"name": "Implement integration layer", "research_needed": False},
        {"name": "Test integration", "research_needed": False},
        {"name": "Monitor and validate", "research_needed": False}
    ]
}
```

## Best Practices

### Plan Design
1. **Keep steps focused**: Each step should accomplish one clear outcome
2. **Order by dependencies**: Complete dependencies before dependent steps
3. **Include verification**: Always include validation/testing steps
4. **Estimate realistically**: Provide time estimates for planning
5. **Identify risks**: Mark high-risk steps for special attention

### Execution
1. **Update frequently**: Update todos as work progresses
2. **Save checkpoints**: Ensure automatic checkpoint saving works
3. **Research when needed**: Don't skip research steps
4. **Handle errors gracefully**: Use retry and fallback mechanisms
5. **Document changes**: Log plan revisions and reasons

### Research Integration
1. **Research before planning**: Gather context first
2. **Research per step**: Conduct step-specific research when needed
3. **Validate assumptions**: Use research to verify approaches
4. **Multi-source validation**: Cross-reference from multiple sources
5. **Keep research focused**: Don't over-research simple steps

## Integration with Cursor Features

### File Management
- Plan file edits in logical groups
- Consider file dependencies
- Batch related changes together

### Terminal Integration
- Plan command execution steps
- Consider command dependencies
- Include verification commands

### Code Analysis
- Use semantic search for understanding
- Plan refactoring with codebase search
- Leverage code intelligence

## Output Style

- **Concise and scannable**: Keep plans easy to read
- **Specific step names**: Use clear, actionable names
- **Markdown formatting**: Use bold, code blocks, lists
- **Progress indicators**: Show completion status clearly
- **Research citations**: Reference research sources when used

## Example Usage

### Creating a Plan

```python
# User request: "Add authentication system"

# Step 1: Research
auth_research = deep_research(
    "JWT authentication best practices Python FastAPI",
    sources=["docs", "scholar", "github"],
    depth="comprehensive"
)

# Step 2: Create plan
plan = create_plan([
    "Research authentication approaches",
    "Design authentication architecture",
    "Implement JWT token generation",
    "Add authentication middleware",
    "Create login/logout endpoints",
    "Add unit tests",
    "Update API documentation"
])

# Step 3: Initialize tracking
todo_write(merge=False, todos=plan["steps"])

# Step 4: Execute
execute_plan(plan)
```

---

*This skill integrates web-search-deepresearch for intelligent planning and Cursor's todo system for progress tracking.*
