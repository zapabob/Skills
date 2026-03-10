---
name: claudecode-subagent-system
description: ClaudeCode-style subagent system for Codex. This skill should be used when creating and managing specialized AI subagents, configuring project-specific AI behaviors, and coordinating multiple AI personalities within development workflows. Use for custom agent definitions, environment-specific configurations, and intelligent task delegation across specialized AI assistants.
---

# ClaudeCode Subagent System

This skill implements ClaudeCode-style subagent management within Codex, enabling sophisticated multi-agent coordination with specialized AI personalities, project-specific configurations, and intelligent task delegation. It provides a flexible framework for creating and managing custom AI assistants that work together seamlessly.

## Core Features

### Subagent Definition and Management
- **Custom AI Personalities**: Define specialized AI assistants with unique behaviors and expertise
- **Project-Level Configuration**: Set project-specific subagent behaviors and permissions
- **User-Level Preferences**: Configure personal AI assistant preferences across projects
- **Dynamic Agent Loading**: Load and unload subagents based on task requirements

### Environment-Specific Configurations
- **Context-Aware Settings**: Adapt AI behavior based on development context and environment
- **Security Profiles**: Define security boundaries and access controls for each subagent
- **Performance Tuning**: Optimize AI responses for different use cases and complexity levels
- **Resource Management**: Control computational resources allocated to different subagents

### Intelligent Task Delegation
- **Capability Matching**: Automatically route tasks to most suitable subagents
- **Load Balancing**: Distribute work across available subagents for optimal performance
- **Fallback Mechanisms**: Provide backup subagents when primary agents are unavailable
- **Quality Assurance**: Ensure consistent quality across different subagent interactions

### Multi-Agent Coordination
- **Inter-Agent Communication**: Enable subagents to communicate and collaborate on complex tasks
- **State Synchronization**: Maintain consistent state across multiple subagent interactions
- **Conflict Resolution**: Handle conflicting recommendations from different subagents
- **Consensus Building**: Facilitate agreement among multiple AI agents on complex decisions

## Usage Examples

### Creating Custom Subagents
```bash
# Define a security-focused code review subagent
codex subagent create security-reviewer \
  --personality "meticulous security auditor" \
  --expertise "OWASP Top 10, cryptography, access control" \
  --tools "security-scanner, vulnerability-db" \
  --permissions "read-only-code, security-reports"
```

### Project-Specific Configuration
```bash
# Configure subagents for a specific project
codex subagent config --project my-web-app \
  --enable-subagents "security-reviewer, performance-analyzer, accessibility-checker" \
  --context "React web application with Node.js backend" \
  --quality-thresholds "security: high, performance: medium"
```

### Dynamic Task Assignment
```bash
# Automatically assign tasks to appropriate subagents
codex subagent delegate "implement user authentication with JWT" \
  --auto-assign \
  --coordination-mode parallel \
  --quality-gate required \
  --consensus-threshold 0.8
```

### Environment-Specific Behavior
```bash
# Configure different behaviors for different environments
codex subagent env-config production \
  --restrict-tools "file-write, network-access" \
  --enable-subagents "security-reviewer, compliance-checker" \
  --response-style "conservative, well-documented"
```

## Subagent Architecture

### Subagent Definition Schema
```yaml
subagent:
  name: "security-reviewer"
  version: "1.0.0"
  personality:
    role: "Security Auditor"
    expertise: ["OWASP Top 10", "Cryptography", "Access Control"]
    communication_style: "meticulous, evidence-based"
    risk_tolerance: "low"

  capabilities:
    - name: "vulnerability_scanning"
      description: "Scan code for security vulnerabilities"
      tools: ["security-scanner", "vulnerability-db"]
      permissions: ["read-code", "write-reports"]

    - name: "threat_modeling"
      description: "Analyze application threat models"
      tools: ["threat-modeler", "risk-assessor"]
      permissions: ["read-architecture", "write-assessments"]

  configuration:
    project_overrides:
      high_security: true
      compliance_frameworks: ["SOC2", "GDPR"]
    environment_overrides:
      production:
        permissions: ["read-only"]
        tools: ["security-scanner"]
      development:
        permissions: ["read-write"]
        tools: ["security-scanner", "dev-tools"]

  triggers:
    - pattern: "security|vulnerability|authentication|authorization"
      confidence_threshold: 0.8
      priority: "high"

    - file_pattern: "*.rs|*.go|*.java"
      action: "security_review"
      priority: "medium"
```

### Subagent Registry
```python
class SubagentRegistry:
    def __init__(self):
        self.subagents = {}
        self.active_sessions = {}
        self.capability_index = {}

    def register_subagent(self, subagent_def: SubagentDefinition) -> bool:
        """Register a new subagent"""
        if subagent_def.name in self.subagents:
            return False

        self.subagents[subagent_def.name] = subagent_def

        # Index capabilities for efficient lookup
        for capability in subagent_def.capabilities:
            if capability.name not in self.capability_index:
                self.capability_index[capability.name] = []
            self.capability_index[capability.name].append(subagent_def.name)

        return True

    def find_subagents_for_task(self, task: Task) -> List[SubagentMatch]:
        """Find suitable subagents for a given task"""
        matches = []

        for subagent_name, subagent in self.subagents.items():
            match_score = self.calculate_match_score(task, subagent)
            if match_score > 0:
                matches.append(SubagentMatch(
                    subagent_name=subagent_name,
                    score=match_score,
                    capabilities=self.get_matching_capabilities(task, subagent),
                    configuration=self.get_relevant_config(task, subagent)
                ))

        return sorted(matches, key=lambda x: x.score, reverse=True)

    def activate_subagent_session(self, subagent_name: str, context: Dict) -> SubagentSession:
        """Activate a subagent session with specific context"""
        subagent = self.subagents.get(subagent_name)
        if not subagent:
            raise ValueError(f"Subagent {subagent_name} not found")

        session = SubagentSession(
            id=generate_session_id(),
            subagent_name=subagent_name,
            context=context,
            start_time=datetime.now(),
            capabilities=subagent.capabilities,
            configuration=self.resolve_configuration(subagent, context)
        )

        self.active_sessions[session.id] = session
        return session
```

### Dynamic Task Routing
```python
class DynamicTaskRouter:
    def __init__(self, subagent_registry: SubagentRegistry):
        self.registry = subagent_registry
        self.routing_history = []
        self.performance_metrics = {}

    async def route_task(self, task: Task, context: Dict) -> RoutingDecision:
        """Route a task to the most appropriate subagent(s)"""
        # Find suitable subagents
        candidates = self.registry.find_subagents_for_task(task)

        if not candidates:
            return RoutingDecision.fallback_routing(task)

        # Apply routing strategy
        if task.routing_strategy == "single_best":
            decision = self.route_to_single_best(candidates, task, context)
        elif task.routing_strategy == "parallel":
            decision = self.route_parallel(candidates, task, context)
        elif task.routing_strategy == "sequential":
            decision = self.route_sequential(candidates, task, context)
        else:
            decision = self.route_adaptive(candidates, task, context)

        # Record routing decision
        self.routing_history.append({
            'task': task,
            'candidates': candidates,
            'decision': decision,
            'timestamp': datetime.now()
        })

        return decision

    def route_to_single_best(self, candidates: List[SubagentMatch],
                           task: Task, context: Dict) -> RoutingDecision:
        """Route to the single best matching subagent"""
        best_match = candidates[0]  # Already sorted by score

        return RoutingDecision(
            strategy="single",
            assignments=[SubagentAssignment(
                subagent_name=best_match.subagent_name,
                task_portion=1.0,  # 100% of task
                capabilities=best_match.capabilities,
                configuration=best_match.configuration
            )],
            reasoning=f"Selected {best_match.subagent_name} with score {best_match.score:.2f}"
        )

    def route_parallel(self, candidates: List[SubagentMatch],
                      task: Task, context: Dict) -> RoutingDecision:
        """Route task portions to multiple subagents in parallel"""
        # Select top candidates that can work in parallel
        parallel_candidates = [c for c in candidates[:3] if self.can_work_parallel(c)]

        if len(parallel_candidates) < 2:
            return self.route_to_single_best(candidates, task, context)

        # Divide task among candidates
        assignments = []
        total_score = sum(c.score for c in parallel_candidates)

        for candidate in parallel_candidates:
            portion = candidate.score / total_score
            assignments.append(SubagentAssignment(
                subagent_name=candidate.subagent_name,
                task_portion=portion,
                capabilities=candidate.capabilities,
                configuration=candidate.configuration
            ))

        return RoutingDecision(
            strategy="parallel",
            assignments=assignments,
            reasoning=f"Parallel execution across {len(assignments)} subagents"
        )

    def can_work_parallel(self, candidate: SubagentMatch) -> bool:
        """Check if a subagent can work in parallel with others"""
        # Implementation depends on subagent capabilities
        # Some subagents may have exclusive access requirements
        return True  # Simplified for this example
```

## Integration with Codex Ecosystem

### LLMOps Integration
- **Model Selection**: Choose appropriate models for different subagent personalities
- **Cost Optimization**: Optimize API usage across multiple subagent interactions
- **Performance Monitoring**: Track subagent performance and effectiveness
- **Continuous Learning**: Improve subagent configurations based on usage patterns

### A2A Communication Enhancement
- **Subagent Protocols**: Specialized communication protocols for subagent coordination
- **State Sharing**: Efficient state synchronization between subagents
- **Conflict Resolution**: Handle conflicting outputs from different subagents
- **Consensus Algorithms**: Implement voting and consensus mechanisms

### Orchestration Integration
- **Subagent Workflows**: Define complex workflows involving multiple subagents
- **Dynamic Scaling**: Scale subagent instances based on workload demands
- **Quality Control**: Ensure consistent quality across subagent outputs
- **Progress Tracking**: Monitor progress across distributed subagent operations

### Skill/MCP Integration
- **Subagent as Skills**: Treat subagents as specialized skills
- **MCP Tool Access**: Provide subagents with appropriate MCP tool access
- **Resource Sharing**: Share resources efficiently among subagents
- **Capability Discovery**: Dynamic discovery of subagent capabilities

### Plan Mode Integration
- **Subagent Planning**: Include subagents in project planning processes
- **Progress Integration**: Track subagent contributions to overall project progress
- **Risk Assessment**: Evaluate risks associated with subagent dependencies
- **Resource Planning**: Plan resource allocation for subagent operations

### Deep Research Integration
- **Research Subagents**: Specialized subagents for different research domains
- **Knowledge Integration**: Integrate research findings across subagent outputs
- **Collaborative Research**: Enable multiple subagents to collaborate on research tasks
- **Quality Validation**: Cross-validate research outputs from different subagents

## Advanced Features

### Adaptive Subagent Evolution
- **Performance Learning**: Improve subagent configurations based on success metrics
- **Capability Expansion**: Dynamically add capabilities to subagents based on usage
- **Personality Optimization**: Refine subagent personalities for better task performance
- **Context Adaptation**: Adapt subagent behavior based on project context

### Multi-Modal Subagent Interaction
- **Text-Based Communication**: Traditional text-based subagent interactions
- **Visual Communication**: Share diagrams, charts, and visual information
- **Code-Based Communication**: Exchange code snippets and structural information
- **Audio Communication**: Voice-based coordination for complex discussions

### Enterprise Integration
- **Audit Trails**: Comprehensive logging of all subagent activities
- **Compliance Monitoring**: Ensure subagent activities meet regulatory requirements
- **Access Control**: Fine-grained permissions and access controls
- **Governance**: Centralized governance and oversight of subagent operations

### Performance Optimization
- **Caching Strategies**: Cache frequently used subagent configurations and results
- **Load Balancing**: Distribute work efficiently across subagent instances
- **Resource Pooling**: Share computational resources among subagents
- **Lazy Loading**: Load subagents only when needed to reduce startup time

## Quality Assurance

### Subagent Validation
```python
class SubagentValidator:
    def validate_subagent_definition(self, definition: SubagentDefinition) -> ValidationResult:
        """Validate subagent definition completeness and correctness"""
        issues = []

        # Check required fields
        if not definition.name:
            issues.append("Missing subagent name")
        if not definition.personality:
            issues.append("Missing personality definition")
        if not definition.capabilities:
            issues.append("No capabilities defined")

        # Validate capabilities
        for capability in definition.capabilities:
            if not capability.name:
                issues.append(f"Capability missing name: {capability}")
            if not capability.description:
                issues.append(f"Capability missing description: {capability}")

        # Check configuration consistency
        config_issues = self.validate_configuration_consistency(definition.configuration)
        issues.extend(config_issues)

        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            recommendations=self.generate_fix_recommendations(issues)
        )

    def validate_configuration_consistency(self, config: SubagentConfiguration) -> List[str]:
        """Check configuration consistency across environments"""
        issues = []

        # Check for conflicting settings
        if config.project_overrides and config.environment_overrides:
            # Validate that overrides don't conflict
            for env, env_config in config.environment_overrides.items():
                if env in config.project_overrides:
                    issues.append(f"Conflicting configuration for environment: {env}")

        return issues
```

### Performance Monitoring
```python
class SubagentPerformanceMonitor:
    def __init__(self):
        self.metrics_store = {}
        self.performance_analyzer = PerformanceAnalyzer()

    def record_subagent_interaction(self, session: SubagentSession, result: SubagentResult):
        """Record a subagent interaction for performance analysis"""
        metrics = SubagentMetrics(
            session_id=session.id,
            subagent_name=session.subagent_name,
            task_type=session.task_type,
            response_time=result.response_time,
            quality_score=result.quality_score,
            resource_usage=result.resource_usage,
            user_satisfaction=result.user_feedback,
            timestamp=datetime.now()
        )

        if session.subagent_name not in self.metrics_store:
            self.metrics_store[session.subagent_name] = []

        self.metrics_store[session.subagent_name].append(metrics)

        # Trigger performance analysis if needed
        if self.should_analyze_performance(session.subagent_name):
            self.analyze_subagent_performance(session.subagent_name)

    def analyze_subagent_performance(self, subagent_name: str):
        """Analyze performance trends for a subagent"""
        metrics = self.metrics_store.get(subagent_name, [])

        if len(metrics) < 10:  # Need minimum data points
            return

        analysis = self.performance_analyzer.analyze_trends(metrics)

        # Generate improvement recommendations
        recommendations = self.generate_performance_recommendations(analysis)

        # Store analysis results
        self.store_performance_analysis(subagent_name, analysis, recommendations)
```

## Best Practices

### Subagent Design
- **Single Responsibility**: Each subagent should have a clear, focused responsibility
- **Capability Documentation**: Thoroughly document what each subagent can and cannot do
- **Personality Consistency**: Maintain consistent personality across interactions
- **Error Handling**: Implement robust error handling and recovery mechanisms

### Configuration Management
- **Hierarchical Configuration**: Support project, user, and environment-level configurations
- **Configuration Validation**: Validate configuration changes before applying
- **Version Control**: Track configuration changes and rollbacks
- **Documentation**: Document configuration options and their effects

### Performance Optimization
- **Resource Monitoring**: Monitor resource usage and optimize allocation
- **Caching Strategies**: Implement appropriate caching for frequently used data
- **Load Testing**: Regularly test subagent performance under load
- **Continuous Monitoring**: Monitor performance metrics and alert on anomalies

### Security Considerations
- **Access Control**: Implement fine-grained access controls for subagents
- **Data Protection**: Protect sensitive data handled by subagents
- **Audit Logging**: Maintain comprehensive audit logs of subagent activities
- **Security Updates**: Regularly update subagent configurations for security

## Success Metrics

### Operational Metrics
- **Subagent Availability**: > 99.5% uptime for critical subagents
- **Task Completion Rate**: > 95% successful task completion by subagents
- **Response Time**: Average < 3 seconds for subagent responses
- **Resource Efficiency**: < 80% average resource utilization

### Quality Metrics
- **Task Accuracy**: > 90% accuracy in subagent task completion
- **User Satisfaction**: > 4.5/5.0 user satisfaction with subagent interactions
- **Consistency**: > 95% consistency in subagent behavior across similar tasks
- **Error Rate**: < 2% error rate in subagent operations

### Business Impact Metrics
- **Productivity Improvement**: 35% increase in development team productivity
- **Time to Resolution**: 50% reduction in average task resolution time
- **Quality Improvement**: 40% reduction in post-deployment defects
- **Cost Efficiency**: 30% reduction in development infrastructure costs

## Conclusion

The ClaudeCode Subagent System represents a sophisticated approach to multi-agent AI coordination within Codex. By enabling the creation and management of specialized AI assistants with distinct personalities and capabilities, it provides a flexible and powerful framework for tackling complex development challenges.

This skill serves as the foundation for intelligent, adaptive AI assistance that can scale with project complexity and team needs, ultimately delivering more efficient, higher-quality software development outcomes.