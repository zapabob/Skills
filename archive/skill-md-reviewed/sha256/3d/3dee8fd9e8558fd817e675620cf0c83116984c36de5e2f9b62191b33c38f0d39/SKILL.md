---
name: autonomous-orchestration-manager
description: Autonomous task orchestration and coordination for Codex. This skill should be used when users need to decompose complex tasks, coordinate multiple agents, or manage token budgets across distributed operations. Use for complex multi-step workflows, agent coordination, and intelligent task planning.
---

# Autonomous Orchestration Manager

This skill provides autonomous task orchestration capabilities for coordinating complex multi-agent workflows within Codex.

## Core Features

### Task Decomposition
- **Intelligent Planning**: Break down complex tasks into manageable subtasks
- **Dependency Analysis**: Identify task dependencies and execution order
- **Resource Allocation**: Assign appropriate agents and resources to tasks
- **Timeline Optimization**: Optimize task execution schedules

### Agent Coordination
- **Load Balancing**: Distribute work across available agents
- **Capability Matching**: Assign tasks to agents with required capabilities
- **Progress Tracking**: Monitor task completion and agent performance
- **Conflict Resolution**: Handle resource conflicts and scheduling issues

### Token Management
- **Budget Allocation**: Distribute token budgets across tasks and agents
- **Usage Monitoring**: Track token consumption in real-time
- **Cost Optimization**: Optimize token usage for cost efficiency
- **Quota Management**: Enforce token limits and prevent overuse

### Workflow Execution
- **Parallel Processing**: Execute independent tasks concurrently
- **Sequential Control**: Manage dependent task execution order
- **Error Handling**: Implement retry logic and failure recovery
- **Result Aggregation**: Combine results from multiple agents

## Usage Examples

### Task Submission
```bash
# Submit a complex task for orchestration
python scripts/llmops_manager.py orchestrate submit-task --name "full-stack-app" --description "Build a complete web application with frontend, backend, and database" --priority high
```

### Task Execution
```bash
# Execute an orchestrated task
python scripts/llmops_manager.py orchestrate execute-task --id task_1234567890_0
```

### Progress Monitoring
```bash
# Check task status
python scripts/llmops_manager.py orchestrate task-status --id task_1234567890_0
```

### System Overview
```bash
# View orchestration system status
python scripts/llmops_manager.py orchestrate status
```

## Orchestration Strategies

### Task Types
- **Sequential**: Tasks that must execute in order
- **Parallel**: Independent tasks that can run concurrently
- **Conditional**: Tasks with branching logic based on results
- **Iterative**: Tasks that repeat until conditions are met

### Agent Assignment
- **Specialist Assignment**: Route to agents with specific expertise
- **Load-based Assignment**: Distribute based on current agent load
- **Capability Matching**: Match tasks to agent capabilities
- **Cost Optimization**: Choose cost-effective agents when possible

## Integration with Codex

This skill integrates with Codex's orchestration framework:

- **LLMOps Integration**: Performance monitoring and cost optimization
- **A2A Communication**: Inter-agent coordination and messaging
- **Skill/MCP Integration**: Resource sharing and tool access
- **Multi-agent Systems**: Distributed task execution across agents

## Best Practices

### Task Design
- **Modular Tasks**: Break complex tasks into smaller, manageable units
- **Clear Dependencies**: Define task relationships and prerequisites
- **Resource Requirements**: Specify required capabilities and resources
- **Success Criteria**: Define clear completion conditions

### Agent Management
- **Agent Pooling**: Maintain pools of specialized agents
- **Health Monitoring**: Monitor agent availability and performance
- **Scaling**: Add/remove agents based on workload demands
- **Backup Systems**: Implement fallback agents for critical tasks

### Performance Optimization
- **Caching**: Cache frequently used results and data
- **Batch Processing**: Group similar tasks for efficient processing
- **Load Prediction**: Anticipate workload changes and scale accordingly
- **Resource Sharing**: Maximize resource utilization across tasks

### Error Handling
- **Retry Logic**: Implement intelligent retry mechanisms
- **Fallback Plans**: Define alternative execution paths
- **Error Propagation**: Communicate errors effectively across agents
- **Recovery Procedures**: Automate recovery from common failure modes

## Advanced Features

### Dynamic Orchestration
- **Runtime Adaptation**: Adjust orchestration based on real-time conditions
- **Learning Systems**: Improve orchestration through experience
- **Predictive Scaling**: Anticipate resource needs and scale proactively
- **Quality Assurance**: Validate results and ensure quality standards

### Integration Patterns
- **API Orchestration**: Coordinate multiple API calls and services
- **Data Pipelines**: Manage complex data processing workflows
- **Event-driven Orchestration**: Respond to events and triggers
- **State Machines**: Implement complex business logic workflows