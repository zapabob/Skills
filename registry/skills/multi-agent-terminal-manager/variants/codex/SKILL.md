---
name: multi-agent-terminal-manager
description: Multi-agent terminal coordination and conflict prevention system for Codex. This skill should be used when managing multiple AI agents, coordinating terminal processes, preventing merge conflicts, and orchestrating complex development workflows. Use for agent lifecycle management, task distribution, workflow automation, and collaborative development processes.
---

# Multi-Agent Terminal Manager

This skill provides comprehensive multi-agent coordination and terminal management capabilities for complex development workflows. It enables intelligent agent lifecycle management, conflict prevention, and automated workflow orchestration in collaborative development environments.

## Core Features

### Agent Lifecycle Management
- **Agent Registration**: Dynamic agent discovery and registration system
- **Role-based Coordination**: Code reviewer, test runner, security auditor role assignment
- **Health Monitoring**: Continuous agent status monitoring and health checks
- **Automatic Scaling**: Dynamic agent pool scaling based on workload demands

### Terminal Process Orchestration
- **Process Launch**: Intelligent terminal process initialization with resource allocation
- **Lifecycle Management**: Complete process monitoring from launch to cleanup
- **Resource Optimization**: Memory and CPU usage optimization across processes
- **Crash Recovery**: Automatic process restart and state recovery mechanisms

### Conflict Prevention System
- **Merge Conflict Detection**: Pre-merge conflict analysis and prevention
- **Concurrent Access Control**: Safe concurrent file access management
- **Branch Strategy Enforcement**: Automated branch naming and protection rules
- **Rollback Automation**: Intelligent rollback procedures for failed operations

### Workflow Automation
- **Task Distribution**: Intelligent task routing to appropriate agents
- **Dependency Resolution**: Automatic resolution of task interdependencies
- **Progress Tracking**: Real-time workflow progress monitoring and reporting
- **Quality Gates**: Automated quality checkpoints and approval workflows

## Usage Examples

### Basic Agent Coordination
```bash
# Launch coordinated agent team for code review
python tools/multi_agent_terminal_manager.py launch-workflow code-review \
  --agents code-reviewer,test-runner,security-auditor \
  --branch feature/new-feature \
  --auto-cleanup
```

### Conflict Prevention Workflow
```bash
# Execute merge with conflict prevention
python tools/multi_agent_terminal_manager.py safe-merge \
  --source feature/implementation \
  --target main \
  --conflict-strategy intelligent \
  --backup-auto
```

### Development Workflow Automation
```bash
# Run complete development cycle
python tools/multi_agent_terminal_manager.py run-pipeline \
  --stages lint,test,security,merge \
  --parallel-execution \
  --progress-monitoring \
  --notification-webhook
```

### Terminal Management
```bash
# Monitor and manage terminal processes
python tools/multi_agent_terminal_manager.py monitor-processes \
  --filter-by-role developer \
  --health-check-interval 30 \
  --auto-restart-failed
```

## Architecture Components

### Agent Communication Protocol
```json
{
  "message_type": "task_assignment|status_update|conflict_detected",
  "agent_id": "code-reviewer-001",
  "workflow_id": "workflow-12345",
  "payload": {
    "task": "review-pull-request",
    "parameters": {
      "pr_number": 123,
      "priority": "high",
      "deadline": "2026-01-20T10:00:00Z"
    }
  },
  "timestamp": 1640995200.0
}
```

### Process Lifecycle Management
```python
class TerminalProcessManager:
    def launch_process(self, agent_config: AgentConfig) -> ProcessHandle:
        # Resource allocation
        resources = self.allocate_resources(agent_config.requirements)

        # Process initialization
        process = self.initialize_terminal(agent_config)

        # Health monitoring setup
        monitor = self.setup_health_monitor(process)

        # Cleanup registration
        self.register_cleanup_handlers(process, monitor)

        return ProcessHandle(process, monitor, resources)

    def monitor_process(self, handle: ProcessHandle) -> ProcessStatus:
        # Continuous health checking
        health = self.check_process_health(handle)

        # Resource usage monitoring
        usage = self.monitor_resource_usage(handle)

        # Automatic recovery if needed
        if not health.healthy:
            self.attempt_recovery(handle)

        return ProcessStatus(health, usage)
```

### Conflict Prevention Engine
```python
class ConflictPreventionEngine:
    def analyze_merge_conflict_risk(self, source_branch: str, target_branch: str) -> ConflictRisk:
        # Analyze file changes
        changes = self.analyze_file_changes(source_branch, target_branch)

        # Calculate conflict probability
        risk_score = self.calculate_risk_score(changes)

        # Identify high-risk files
        high_risk_files = self.identify_high_risk_files(changes)

        # Generate prevention strategies
        strategies = self.generate_prevention_strategies(risk_score, high_risk_files)

        return ConflictRisk(risk_score, high_risk_files, strategies)

    def execute_safe_merge(self, merge_request: MergeRequest) -> MergeResult:
        # Pre-merge risk assessment
        risk = self.analyze_merge_conflict_risk(merge_request.source, merge_request.target)

        if risk.score > 0.8:
            return MergeResult(status="blocked", reason="High conflict risk", alternatives=risk.strategies)

        # Execute merge with monitoring
        result = self.perform_monitored_merge(merge_request)

        # Post-merge validation
        validation = self.validate_merge_result(result)

        return MergeResult(status=result.status, validation=validation)
```

## Integration with Codex Ecosystem

### LLMOps Integration
- **Performance Monitoring**: Agent performance tracking and optimization
- **Cost Management**: API usage monitoring across coordinated agents
- **Model Selection**: Intelligent model selection based on task requirements

### A2A Communication Enhancement
- **Coordination Protocols**: Advanced inter-agent communication protocols
- **State Synchronization**: Real-time state sharing across distributed agents
- **Fault Tolerance**: Automatic agent replacement and workload redistribution

### Orchestration Integration
- **Workflow Templates**: Pre-defined multi-agent workflow templates
- **Dynamic Scaling**: Automatic agent pool scaling based on orchestration demands
- **Quality Assurance**: Integrated quality checks within orchestration flows

### Skill/MCP Integration
- **Resource Management**: Centralized resource allocation for skill execution
- **Tool Orchestration**: Coordinated tool usage across multiple skills
- **Context Sharing**: Shared context management across skill boundaries

## Advanced Features

### Intelligent Task Routing
- **Capability Matching**: Route tasks to agents with appropriate capabilities
- **Load Balancing**: Distribute workload evenly across available agents
- **Performance Optimization**: Route to highest-performing agents for critical tasks
- **Learning-based Routing**: Improve routing decisions through experience

### Predictive Conflict Prevention
- **Historical Analysis**: Learn from past merge conflicts and success patterns
- **Risk Prediction**: Predict merge conflict likelihood based on change patterns
- **Proactive Mitigation**: Implement prevention measures before conflicts occur
- **Continuous Learning**: Update prevention strategies based on outcomes

### Autonomous Workflow Management
- **Self-Healing Systems**: Automatic problem detection and resolution
- **Adaptive Scaling**: Dynamic resource allocation based on system load
- **Quality Optimization**: Continuous improvement of workflow quality metrics
- **Predictive Maintenance**: Anticipate and prevent system issues

### Cross-Platform Coordination
- **Multi-OS Support**: Windows, macOS, Linux agent coordination
- **Container Orchestration**: Docker/Kubernetes integration for isolated environments
- **Cloud Integration**: AWS/GCP/Azure agent deployment and management
- **Hybrid Deployments**: Mix of local and cloud-based agents

## Best Practices

### Agent Management
- **Role Definition**: Clearly define agent roles and responsibilities
- **Capability Declaration**: Document agent capabilities and limitations
- **Health Monitoring**: Implement comprehensive health checks and monitoring
- **Lifecycle Management**: Proper agent startup, operation, and shutdown procedures

### Process Orchestration
- **Resource Planning**: Adequate resource allocation for agent processes
- **Dependency Management**: Clear understanding of process interdependencies
- **Failure Handling**: Robust error handling and recovery mechanisms
- **Performance Monitoring**: Continuous monitoring of process performance metrics

### Conflict Prevention
- **Branch Strategy**: Implement clear branching and merging strategies
- **Code Review Integration**: Mandatory code reviews before merge operations
- **Testing Requirements**: Comprehensive testing before merge approval
- **Documentation**: Clear documentation of merge processes and requirements

### Workflow Automation
- **Template Usage**: Utilize proven workflow templates for common scenarios
- **Customization**: Allow workflow customization while maintaining standards
- **Version Control**: Version control of workflow definitions and configurations
- **Audit Trail**: Comprehensive logging of workflow execution and decisions

## Success Metrics

### Operational Metrics
- **Agent Uptime**: 99.9% agent availability and responsiveness
- **Process Success Rate**: 95% successful process completion without intervention
- **Conflict Prevention Rate**: 90% reduction in merge conflicts
- **Workflow Completion Time**: 50% reduction in average workflow duration

### Quality Metrics
- **Error Rate**: < 1% process failure rate
- **Recovery Time**: < 5 minutes average recovery time from failures
- **User Satisfaction**: > 4.5/5.0 user satisfaction with coordination features
- **Automation Coverage**: > 80% of development tasks fully automated

### Business Impact
- **Development Velocity**: 40% increase in development team productivity
- **Quality Improvement**: 60% reduction in post-merge defects
- **Time to Market**: 30% reduction in feature delivery time
- **Cost Efficiency**: 25% reduction in development infrastructure costs

## Implementation Roadmap

### Phase 1: Core Infrastructure (Current)
- [x] Agent lifecycle management system
- [x] Basic terminal process orchestration
- [x] Fundamental conflict prevention mechanisms

### Phase 2: Advanced Coordination (Next Sprint)
- [ ] Intelligent task routing and load balancing
- [ ] Predictive conflict prevention with ML
- [ ] Advanced workflow automation templates

### Phase 3: Autonomous Operation (Future)
- [ ] Self-healing and self-optimizing systems
- [ ] Full autonomous workflow management
- [ ] Predictive maintenance and issue prevention

### Phase 4: Ecosystem Integration (Future)
- [ ] Cross-platform agent coordination
- [ ] Enterprise-scale deployment capabilities
- [ ] Advanced analytics and reporting dashboards

## Conclusion

The Multi-Agent Terminal Manager represents a significant advancement in collaborative AI development environments. By providing intelligent coordination, conflict prevention, and automated workflow management, it enables development teams to achieve unprecedented levels of productivity, quality, and reliability in their AI-assisted development processes.

This skill serves as the coordination backbone for complex multi-agent systems, ensuring that individual AI agents work together seamlessly to deliver exceptional development outcomes.