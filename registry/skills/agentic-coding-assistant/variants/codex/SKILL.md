---
name: agentic-coding-assistant
description: ClaudeCode-style agentic coding assistant with multi-file editing, terminal integration, and autonomous task execution. This skill should be used when performing complex coding tasks autonomously, editing multiple files simultaneously, executing terminal commands, or managing coding workflows with checkpoints and rollback capabilities. Use for refactoring, feature development, debugging, testing integration, and autonomous coding assistance.
---

# Agentic Coding Assistant

This skill brings ClaudeCode-style agentic coding capabilities to Codex, enabling autonomous, intelligent coding assistance with multi-file editing, terminal integration, and context-aware task execution. Inspired by Anthropic's ClaudeCode features from 2025-2026, it provides a comprehensive coding companion that can work across your entire codebase.

## Core Features

### Agentic Task Execution
- **Autonomous Workflow**: Execute complex coding tasks autonomously from start to finish
- **Goal-Oriented Planning**: Break down objectives into actionable coding steps
- **Self-Directed Execution**: Make decisions and execute tasks without constant supervision
- **Result Validation**: Verify outcomes and adjust approach based on feedback

### Multi-File Editing
- **Coordinated Changes**: Edit multiple files simultaneously while maintaining consistency
- **Dependency Awareness**: Understand and respect file dependencies and relationships
- **Batch Operations**: Apply changes across related files in logical sequences
- **Conflict Resolution**: Handle merge conflicts and concurrent file modifications

### Terminal Integration
- **Command Execution**: Run terminal commands with intelligent context awareness
- **Output Processing**: Parse command outputs and incorporate results into coding decisions
- **Environment Management**: Handle development environments, dependencies, and tooling
- **Error Recovery**: Diagnose and recover from command failures automatically

### Context Awareness
- **Project Understanding**: Maintain deep understanding of project structure and conventions
- **Code Pattern Recognition**: Identify and follow existing code patterns and architectural decisions
- **Dependency Mapping**: Track and manage code dependencies across modules and files
- **Historical Context**: Learn from past changes and maintain project evolution awareness

### Checkpoint & Rollback System
- **Automatic Checkpoints**: Save project state before major changes
- **Time-Travel Debugging**: Roll back to previous states for debugging and experimentation
- **Safe Experimentation**: Try risky changes with easy rollback capabilities
- **Version Control Integration**: Seamless integration with Git for state management

### Async Subagent Support
- **Parallel Processing**: Spawn subagents for parallel task execution
- **Background Tasks**: Run monitoring, testing, and analysis tasks in background
- **Task Coordination**: Manage multiple subagents working on different aspects of a project
- **Result Aggregation**: Combine results from multiple subagents into coherent outcomes

## Usage Examples

### Autonomous Feature Development
```bash
# Develop a complete feature autonomously
python tools/agentic_coding_assistant.py develop-feature \
  --description "Implement user authentication system with JWT tokens" \
  --tech-stack "React, Node.js, PostgreSQL" \
  --acceptance-criteria "users can login/logout, tokens are validated" \
  --auto-test \
  --checkpoint-enabled
```

### Multi-File Refactoring
```bash
# Refactor across multiple files
python tools/agentic_coding_assistant.py refactor-code \
  --target "authentication module" \
  --changes "extract JWT logic to separate service, add refresh token support" \
  --files-affected "auth.js, middleware.js, userService.js" \
  --validate-syntax \
  --create-backup
```

### Terminal-Integrated Development
```bash
# Development with terminal integration
python tools/agentic_coding_assistant.py integrated-development \
  --task "Set up CI/CD pipeline with automated testing" \
  --commands "npm install, npm test, docker build, docker push" \
  --error-handling "retry on network failures, rollback on build failures" \
  --progress-monitoring
```

### Context-Aware Debugging
```bash
# Intelligent debugging with full context
python tools/agentic_coding_assistant.py debug-issue \
  --symptoms "authentication fails intermittently" \
  --logs "auth.log, error.log" \
  --codebase-analysis \
  --hypothesis-generation \
  --fix-proposal
```

## Agentic Execution Engine

### Task Planning & Decomposition
```python
class TaskPlanner:
    def plan_agentic_execution(self, task_description: str, constraints: Dict) -> ExecutionPlan:
        # Parse task requirements
        requirements = self.parse_requirements(task_description)

        # Analyze codebase context
        context = self.analyze_codebase_context(requirements)

        # Generate execution steps
        steps = self.generate_execution_steps(requirements, context, constraints)

        # Validate plan feasibility
        validation = self.validate_plan_feasibility(steps, context)

        return ExecutionPlan(
            steps=steps,
            estimated_duration=self.estimate_duration(steps),
            risk_assessment=self.assess_execution_risks(steps),
            rollback_plan=self.create_rollback_plan(steps),
            validation=validation
        )

    def parse_requirements(self, description: str) -> TaskRequirements:
        # Extract technical requirements, constraints, and success criteria
        # Analyze dependencies and prerequisites
        # Identify required skills and tools
        pass

    def generate_execution_steps(self, requirements: TaskRequirements,
                               context: CodebaseContext, constraints: Dict) -> List[ExecutionStep]:
        # Break down task into atomic steps
        # Order steps based on dependencies
        # Assign appropriate tools and techniques for each step
        pass
```

### Multi-File Coordination
```python
class MultiFileCoordinator:
    def coordinate_file_changes(self, changes: List[FileChange]) -> CoordinationResult:
        # Analyze change dependencies
        dependencies = self.analyze_change_dependencies(changes)

        # Create change execution order
        execution_order = self.create_execution_order(changes, dependencies)

        # Validate change consistency
        consistency_check = self.validate_change_consistency(changes, execution_order)

        # Execute changes with rollback capability
        execution_result = self.execute_coordinated_changes(
            changes, execution_order, consistency_check
        )

        return CoordinationResult(
            execution_order=execution_order,
            consistency_check=consistency_check,
            execution_result=execution_result,
            rollback_available=execution_result.success
        )

    def analyze_change_dependencies(self, changes: List[FileChange]) -> DependencyGraph:
        # Build dependency graph between files
        # Identify circular dependencies
        # Determine safe execution order
        pass

    def validate_change_consistency(self, changes: List[FileChange],
                                  execution_order: List[int]) -> ConsistencyValidation:
        # Check for conflicting changes
        # Validate syntax across all files
        # Ensure logical consistency
        pass
```

### Terminal Integration Manager
```python
class TerminalIntegrationManager:
    def execute_terminal_workflow(self, commands: List[TerminalCommand],
                                context: ExecutionContext) -> TerminalResult:
        # Set up execution environment
        environment = self.setup_execution_environment(context)

        # Execute commands with monitoring
        results = []
        for command in commands:
            result = self.execute_command_with_monitoring(command, environment)
            results.append(result)

            # Handle command failures
            if not result.success:
                recovery_action = self.determine_recovery_action(result, context)
                if recovery_action == "rollback":
                    self.rollback_to_checkpoint(context.checkpoint_id)
                    break
                elif recovery_action == "retry":
                    result = self.retry_command(command, environment)
                    results[-1] = result

        # Aggregate results
        aggregated_result = self.aggregate_terminal_results(results, context)

        # Clean up environment
        self.cleanup_execution_environment(environment)

        return aggregated_result

    def execute_command_with_monitoring(self, command: TerminalCommand,
                                      environment: ExecutionEnvironment) -> CommandResult:
        # Start monitoring
        monitor = self.start_command_monitoring(command)

        # Execute command
        result = self.execute_terminal_command(command, environment)

        # Collect monitoring data
        monitoring_data = monitor.collect_data()

        # Analyze execution
        analysis = self.analyze_command_execution(result, monitoring_data)

        return CommandResult(
            command=command,
            success=result.success,
            output=result.output,
            error=result.error,
            execution_time=result.execution_time,
            monitoring_data=monitoring_data,
            analysis=analysis
        )
```

### Checkpoint & Recovery System
```python
class CheckpointRecoverySystem:
    def create_checkpoint(self, context: ExecutionContext) -> Checkpoint:
        # Capture current state
        file_states = self.capture_file_states(context.files)
        environment_state = self.capture_environment_state(context.environment)
        execution_state = self.capture_execution_state(context.execution)

        # Store checkpoint
        checkpoint_id = self.store_checkpoint(Checkpoint(
            id=self.generate_checkpoint_id(),
            timestamp=datetime.now(),
            file_states=file_states,
            environment_state=environment_state,
            execution_state=execution_state,
            metadata={
                "task": context.task_description,
                "user": context.user_id,
                "agent_version": self.get_agent_version()
            }
        ))

        return self.get_checkpoint(checkpoint_id)

    def rollback_to_checkpoint(self, checkpoint_id: str) -> RollbackResult:
        # Retrieve checkpoint
        checkpoint = self.get_checkpoint(checkpoint_id)

        # Validate rollback feasibility
        validation = self.validate_rollback_feasibility(checkpoint)

        if not validation.can_rollback:
            return RollbackResult(
                success=False,
                reason=validation.failure_reason,
                alternative_actions=validation.alternatives
            )

        # Execute rollback
        rollback_result = self.execute_rollback(checkpoint)

        # Verify rollback integrity
        verification = self.verify_rollback_integrity(checkpoint, rollback_result)

        return RollbackResult(
            success=rollback_result.success,
            checkpoint_restored=checkpoint,
            verification=verification,
            warnings=rollback_result.warnings
        )

    def capture_file_states(self, files: List[str]) -> Dict[str, FileState]:
        # Capture file contents and metadata
        file_states = {}
        for file_path in files:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    stat = os.stat(file_path)
                    file_states[file_path] = FileState(
                        path=file_path,
                        content=content,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                        permissions=stat.st_mode
                    )
        return file_states
```

## Integration with Codex Ecosystem

### LLMOps Integration
- **Model Selection**: Choose appropriate models for different coding tasks
- **Cost Optimization**: Optimize API usage based on task complexity
- **Performance Monitoring**: Track agent performance and success rates

### A2A Communication Enhancement
- **Subagent Coordination**: Manage multiple coding subagents
- **Result Sharing**: Share coding insights across agents
- **Collaborative Coding**: Enable multiple agents to work on the same codebase

### Orchestration Integration
- **Workflow Templates**: Pre-defined coding workflow templates
- **Task Decomposition**: Break down complex coding tasks into manageable steps
- **Progress Integration**: Integrate coding progress with overall project tracking

### Skill/MCP Integration
- **Tool Orchestration**: Coordinate coding tools and utilities
- **Resource Management**: Manage development resources and environments
- **Execution Optimization**: Optimize coding task execution across tools

### Plan Mode Integration
- **Coding Task Planning**: Plan complex coding tasks with dependencies
- **Progress Tracking**: Track coding progress within project plans
- **Milestone Management**: Manage coding milestones and deliverables

### Deep Research Integration
- **Code Investigation**: Research existing code patterns and architectures
- **Technology Research**: Investigate new technologies and frameworks
- **Best Practice Discovery**: Find coding best practices and patterns

## Advanced Features

### Autonomous Learning
- **Pattern Recognition**: Learn coding patterns from successful executions
- **Technique Adaptation**: Adapt coding techniques based on project context
- **Performance Optimization**: Optimize execution based on historical performance
- **Error Recovery Learning**: Learn from past errors to improve recovery strategies

### Intelligent Code Generation
- **Context-Aware Generation**: Generate code that fits existing codebase patterns
- **Multi-Language Support**: Generate code in multiple programming languages
- **Framework Integration**: Generate code that integrates with existing frameworks
- **Quality Assurance**: Ensure generated code meets quality standards

### Collaborative Coding Support
- **Pair Programming**: Support virtual pair programming with AI agents
- **Code Review Integration**: Integrate AI-generated code with human review processes
- **Knowledge Sharing**: Share coding insights and techniques across sessions
- **Team Learning**: Learn from team coding patterns and preferences

### Enterprise Integration
- **Security Compliance**: Ensure generated code meets security standards
- **Audit Trail**: Maintain comprehensive audit trails of AI-generated code
- **Governance**: Implement governance controls for AI-assisted coding
- **Scalability**: Support large-scale, enterprise-level coding projects

## Quality Assurance

### Code Generation Validation
```python
class CodeGenerationValidator:
    def validate_generated_code(self, code: str, language: str,
                              context: CodebaseContext) -> ValidationResult:
        # Syntax validation
        syntax_check = self.validate_syntax(code, language)

        # Semantic validation
        semantic_check = self.validate_semantics(code, language, context)

        # Consistency validation
        consistency_check = self.validate_consistency(code, context)

        # Security validation
        security_check = self.validate_security(code, language)

        # Performance validation
        performance_check = self.validate_performance(code, language)

        return ValidationResult(
            syntax_valid=syntax_check.valid,
            semantic_valid=semantic_check.valid,
            consistent=consistency_check.consistent,
            security_clear=security_check.clear,
            performance_acceptable=performance_check.acceptable,
            suggestions=self.generate_improvement_suggestions(
                syntax_check, semantic_check, consistency_check,
                security_check, performance_check
            )
        )

    def validate_syntax(self, code: str, language: str) -> SyntaxValidation:
        # Language-specific syntax checking
        if language == "python":
            return self.validate_python_syntax(code)
        elif language == "javascript":
            return self.validate_javascript_syntax(code)
        elif language == "rust":
            return self.validate_rust_syntax(code)
        # Add more languages as needed
        pass
```

### Execution Monitoring
```python
class ExecutionMonitor:
    def monitor_agentic_execution(self, execution: AgenticExecution) -> MonitoringResult:
        # Performance monitoring
        performance_metrics = self.monitor_performance(execution)

        # Quality monitoring
        quality_metrics = self.monitor_quality(execution)

        # Progress monitoring
        progress_metrics = self.monitor_progress(execution)

        # Error monitoring
        error_metrics = self.monitor_errors(execution)

        # Generate insights
        insights = self.generate_execution_insights(
            performance_metrics, quality_metrics,
            progress_metrics, error_metrics
        )

        return MonitoringResult(
            performance=performance_metrics,
            quality=quality_metrics,
            progress=progress_metrics,
            errors=error_metrics,
            insights=insights,
            recommendations=self.generate_recommendations(insights)
        )

    def generate_execution_insights(self, performance, quality, progress, errors) -> List[Insight]:
        insights = []

        # Performance insights
        if performance.execution_time > performance.expected_time * 1.5:
            insights.append(Insight(
                type="performance",
                severity="medium",
                message="Execution time significantly longer than expected",
                suggestion="Consider optimizing the approach or breaking down the task"
            ))

        # Quality insights
        if quality.error_rate > 0.1:
            insights.append(Insight(
                type="quality",
                severity="high",
                message="High error rate detected during execution",
                suggestion="Review error handling and validation logic"
            ))

        # Progress insights
        if progress.completion_rate < 0.5 and progress.time_elapsed > progress.expected_duration * 0.8:
            insights.append(Insight(
                type="progress",
                severity="medium",
                message="Progress behind schedule",
                suggestion="Reassess approach or request additional resources"
            ))

        return insights
```

## Success Metrics

### Execution Quality Metrics
- **Task Completion Rate**: > 95% successful autonomous task completion
- **Code Generation Accuracy**: > 90% syntactically correct generated code
- **Error Recovery Rate**: > 98% automatic recovery from execution errors
- **User Satisfaction**: > 4.5/5.0 satisfaction with autonomous assistance

### Performance Metrics
- **Execution Speed**: < 50% increase in task completion time vs manual execution
- **Resource Efficiency**: < 20% resource overhead for autonomous execution
- **Scalability**: Support for projects with 100k+ lines of code
- **Reliability**: 99.5% uptime for autonomous execution services

### Quality Assurance Metrics
- **Code Quality Score**: > 85% adherence to project coding standards
- **Security Compliance**: 100% compliance with security best practices
- **Test Coverage**: > 90% test coverage for generated code
- **Maintainability Score**: > 80% maintainability index for generated code

## Conclusion

The Agentic Coding Assistant represents the future of AI-assisted software development, bringing ClaudeCode-style autonomous coding capabilities to the Codex ecosystem. By combining intelligent task execution, multi-file editing, terminal integration, and comprehensive context awareness, it enables developers to accomplish complex coding tasks with unprecedented efficiency and quality.

This skill serves as the intelligent coding companion that understands your codebase, anticipates your needs, and executes complex development tasks autonomously while maintaining the highest standards of code quality, security, and maintainability.