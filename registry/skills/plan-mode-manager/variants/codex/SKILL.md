---
name: plan-mode-manager
description: Plan mode management for Codex, similar to Cursor/ClaudeCode plan mode. This skill should be used when users need to create execution plans, manage complex multi-step tasks, or break down large projects into manageable phases. Use for task decomposition, execution planning, progress tracking, and collaborative planning workflows.
---

# Plan Mode Manager

This skill provides advanced plan mode capabilities for Codex, inspired by Cursor and ClaudeCode's plan mode features. It enables intelligent task decomposition, execution planning, and progress management for complex multi-step workflows.

## Core Features

### Plan Creation and Management
- **Intelligent Planning**: Analyze complex tasks and create structured execution plans
- **Task Decomposition**: Break down large projects into manageable, actionable tasks
- **Dependency Mapping**: Identify task relationships and execution order
- **Timeline Optimization**: Optimize task schedules and resource allocation

### Execution Planning
- **Phase-based Execution**: Organize work into logical phases and milestones
- **Risk Assessment**: Identify potential blockers and mitigation strategies
- **Resource Planning**: Allocate appropriate resources and team members
- **Success Metrics**: Define clear success criteria and completion conditions

### Progress Tracking and Monitoring
- **Real-time Progress**: Track task completion and overall project status
- **Milestone Management**: Monitor key deliverables and deadlines
- **Status Reporting**: Generate comprehensive progress reports
- **Performance Analytics**: Analyze execution efficiency and identify improvements

### Collaborative Planning
- **Multi-stakeholder Coordination**: Support team-based planning workflows
- **Feedback Integration**: Incorporate stakeholder feedback into plans
- **Version Control**: Track plan evolution and maintain audit trails
- **Communication Tools**: Generate status updates and progress summaries

## Usage Examples

### Complex Project Planning
```bash
# Create a comprehensive plan for a full-stack application
python scripts/llmops_manager.py orchestrate submit-task \
  --name "ecommerce-platform" \
  --description "Build a complete e-commerce platform with payment integration, inventory management, and admin dashboard" \
  --priority high
```

### Task Decomposition
```bash
# Break down a complex feature into manageable tasks
python scripts/llmops_manager.py plan decompose \
  --task "implement-user-authentication" \
  --strategy "agile-sprint"
```

### Progress Monitoring
```bash
# Track progress on ongoing projects
python scripts/llmops_manager.py plan status \
  --project "mobile-app-v2" \
  --detailed
```

### Risk Assessment
```bash
# Analyze potential risks in project execution
python scripts/llmops_manager.py plan risks \
  --plan "infrastructure-migration" \
  --severity high
```

## Planning Methodologies

### Agile Planning
- **Sprint Planning**: 2-week iteration planning with user stories
- **Backlog Management**: Prioritize and refine product backlog
- **Burndown Charts**: Track sprint progress and velocity
- **Retrospectives**: Continuous improvement through reflection

### Waterfall Planning
- **Phase Gates**: Sequential execution with quality checkpoints
- **Requirements Gathering**: Comprehensive requirement analysis
- **Gantt Charts**: Timeline visualization and dependency management
- **Change Control**: Formal change management process

### Hybrid Approaches
- **ScrumBan**: Combine Scrum flexibility with Kanban visualization
- **SAFe**: Scaled Agile Framework for large organizations
- **Lean Startup**: MVP-focused planning with rapid iteration
- **Design Thinking**: User-centered planning methodology

## Integration with Codex

This skill integrates with Codex's planning ecosystem:

- **LLMOps Integration**: Performance monitoring of planning activities
- **A2A Communication**: Coordinate planning across agent teams
- **Autonomous Orchestration**: Execute plans through distributed agents
- **Skill/MCP Integration**: Leverage external tools for enhanced planning

## Best Practices

### Plan Creation
- **SMART Goals**: Specific, Measurable, Achievable, Relevant, Time-bound
- **Stakeholder Involvement**: Include all relevant parties in planning
- **Realistic Estimates**: Base estimates on historical data and expert input
- **Contingency Planning**: Prepare for unexpected challenges

### Execution Management
- **Daily Standups**: Regular check-ins to maintain momentum
- **Progress Transparency**: Keep all stakeholders informed
- **Issue Resolution**: Address blockers quickly and decisively
- **Quality Assurance**: Build quality checks into the execution process

### Risk Management
- **Proactive Identification**: Anticipate potential issues before they occur
- **Impact Assessment**: Evaluate the potential impact of risks
- **Mitigation Strategies**: Develop contingency plans for high-risk items
- **Regular Reviews**: Continuously reassess and update risk profiles

### Communication
- **Clear Documentation**: Maintain comprehensive plan documentation
- **Regular Updates**: Provide frequent status updates to stakeholders
- **Feedback Loops**: Establish mechanisms for continuous feedback
- **Escalation Procedures**: Define clear escalation paths for issues

## Advanced Features

### AI-Powered Planning
- **Predictive Analytics**: Use AI to predict project outcomes and risks
- **Automated Optimization**: AI-driven plan optimization and refinement
- **Smart Scheduling**: Intelligent resource and timeline optimization
- **Performance Prediction**: Forecast project completion and quality metrics

### Integration Capabilities
- **Tool Integration**: Connect with project management tools (Jira, Trello, etc.)
- **CI/CD Integration**: Automated deployment and testing integration
- **Version Control**: Git-based plan versioning and collaboration
- **Reporting Systems**: Automated report generation and distribution

### Adaptive Planning
- **Dynamic Replanning**: Adjust plans based on real-time feedback
- **Change Management**: Handle scope changes and requirement updates
- **Learning Systems**: Improve planning accuracy through experience
- **Scalability**: Handle projects of varying complexity and size