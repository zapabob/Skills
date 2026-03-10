---
name: llmops-manager
description: LLMOps management and monitoring for Codex. This skill should be used when users need to manage model versions, monitor performance, optimize costs, or implement security hardening for LLM operations. Use for model versioning, prompt management, performance monitoring, cost optimization, security assessment, and observability.
---

# LLMOps Manager

This skill provides comprehensive LLMOps capabilities for managing and optimizing LLM operations within Codex.

## Core Features

### Model Management
- **Model Versioning**: Track and manage different model versions with semantic versioning
- **Provider Support**: OpenAI, Anthropic, Google, Meta, Local, and Custom providers
- **Capability Assessment**: Text generation, code generation, analysis, reasoning, multimodal support
- **Performance Metrics**: Latency, throughput, accuracy, reliability, cost per token

### Prompt Management
- **Prompt Versioning**: Version control for prompts with semantic versioning
- **Template Variables**: Support for dynamic prompt variables with validation
- **Context Requirements**: Define required context for prompt execution
- **Security Constraints**: Apply security rules to prompt templates

### Performance Monitoring
- **Real-time Metrics**: Track latency, token usage, success rates
- **Anomaly Detection**: Identify performance degradation automatically
- **Alert System**: Configurable thresholds for performance alerts
- **Historical Analysis**: Trend analysis and performance forecasting

### Cost Optimization
- **Budget Management**: Set hourly/daily cost limits
- **Cost Tracking**: Monitor costs by model, operation, and time period
- **Optimization Suggestions**: Automatic recommendations for cost reduction
- **Usage Analytics**: Detailed cost breakdown and utilization reports

### Security Hardening
- **Input Validation**: Sanitize and validate all LLM inputs
- **Output Filtering**: Remove harmful content and hallucinations
- **Rate Limiting**: Prevent abuse with configurable rate limits
- **Audit Logging**: Comprehensive security event logging

## Usage Examples

### Model Registration
```bash
# Register a new model version
python scripts/llmops_manager.py llmops register-model --name gpt-4-turbo --version 1.0.0 --provider openai
```

### Performance Monitoring
```bash
# Check system status
python scripts/llmops_manager.py llmops status
```

### Cost Management
```bash
# View cost metrics
python scripts/llmops_manager.py llmops cost-report
```

### Security Assessment
```bash
# Run security audit
python scripts/llmops_manager.py llmops security-audit
```

## Configuration

Edit `config.toml` to configure LLMOps settings:

```toml
[llmops]
enable_model_versioning = true
enable_prompt_versioning = true
enable_performance_monitoring = true
enable_cost_optimization = true
enable_security_hardening = true
max_tokens_per_request = 100000
cost_budget_per_hour = 10.0
security_level = "standard"
observability_retention_days = 30
```

## Integration with Codex

This skill integrates with Codex's core LLMOps features:

- **A2A Communication**: Inter-agent messaging for distributed operations
- **Autonomous Orchestration**: Task decomposition and agent coordination
- **Skill/MCP Integration**: Resource management and execution environment
- **MCP Servers**: Multiple MCP server support for extended capabilities

## Best Practices

### Model Selection
- Choose models based on required capabilities and cost constraints
- Monitor performance metrics regularly
- Update model versions when better alternatives become available

### Cost Management
- Set appropriate budget limits based on usage patterns
- Monitor cost trends and optimize expensive operations
- Use cost-effective models for non-critical tasks

### Security
- Always validate inputs and filter outputs
- Implement rate limiting for production deployments
- Regularly audit security logs and update policies

### Monitoring
- Set up alerts for performance degradation
- Monitor token usage and cost trends
- Review observability data for optimization opportunities