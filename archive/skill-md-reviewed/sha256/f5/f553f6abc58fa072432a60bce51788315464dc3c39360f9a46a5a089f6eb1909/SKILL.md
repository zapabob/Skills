---
name: a2a-communication-manager
description: Agent-to-Agent communication and coordination for Codex. This skill should be used when users need to implement inter-agent messaging, shared state management, or fault-tolerant communication between AI agents. Use for distributed AI systems, multi-agent workflows, and resilient agent networks.
---

# A2A Communication Manager

This skill provides Agent-to-Agent (A2A) communication capabilities for coordinating multiple AI agents within Codex.

## Core Features

### Agent Registration
- **Agent Discovery**: Automatic registration and discovery of agents
- **Role Assignment**: Define agent roles and capabilities
- **Trust Scoring**: Dynamic trust assessment between agents
- **Status Monitoring**: Real-time agent availability tracking

### Message Routing
- **Direct Messaging**: Point-to-point communication between agents
- **Broadcast Messaging**: Send messages to multiple agents simultaneously
- **Topic-based Routing**: Publish-subscribe pattern for message distribution
- **Priority Queuing**: Message prioritization based on urgency

### State Synchronization
- **Shared State**: Distributed state management across agents
- **Conflict Resolution**: Handle concurrent state updates
- **Consistency Guarantees**: Ensure data consistency in distributed operations
- **State Persistence**: Durable state storage with recovery

### Fault Tolerance
- **Message Retry**: Automatic retry for failed message delivery
- **Circuit Breaker**: Prevent cascade failures in agent networks
- **Health Monitoring**: Continuous agent health assessment
- **Graceful Degradation**: Maintain functionality during partial failures

## Usage Examples

### Agent Registration
```bash
# Register a new agent
python scripts/llmops_manager.py a2a register-agent --id coding-agent --role code-generation --capabilities "python,javascript,rust"
```

### Message Exchange
```bash
# Send message between agents
python scripts/llmops_manager.py a2a send-message --from coding-agent --to testing-agent --message "Code review completed"
```

### System Monitoring
```bash
# Check communication status
python scripts/llmops_manager.py a2a status
```

## Communication Protocols

### Message Types
- **Task Assignment**: Assign tasks to specialized agents
- **Status Updates**: Share progress and completion status
- **Resource Requests**: Request resources from other agents
- **Error Notifications**: Report errors and request assistance

### Routing Strategies
- **Round Robin**: Distribute load evenly across agents
- **Capability-based**: Route to agents with required capabilities
- **Geographic**: Route based on agent location/proximity
- **Load Balancing**: Route to least-loaded agents

## Integration with Codex

This skill integrates with Codex's multi-agent orchestration:

- **LLMOps Integration**: Performance monitoring of agent communications
- **Skill/MCP Coordination**: Resource sharing between skills
- **Autonomous Orchestration**: Task decomposition across agent networks
- **Fault Recovery**: Automatic agent replacement on failures

## Best Practices

### Agent Design
- **Single Responsibility**: Each agent should have one primary function
- **Capability Declaration**: Clearly define what each agent can do
- **Interface Contracts**: Define message formats and expectations
- **Resource Limits**: Set appropriate limits for agent capacity

### Communication Patterns
- **Asynchronous Messaging**: Use async communication for scalability
- **Idempotent Operations**: Ensure operations can be safely retried
- **Message Versioning**: Support backward-compatible message evolution
- **Security**: Encrypt sensitive communications

### Monitoring and Debugging
- **Message Tracing**: Track message flow through the system
- **Performance Metrics**: Monitor latency and throughput
- **Error Analysis**: Comprehensive error logging and analysis
- **Load Testing**: Validate system performance under load

### Scalability Considerations
- **Horizontal Scaling**: Add more agents as load increases
- **Message Queuing**: Use queues to handle load spikes
- **Caching**: Cache frequently accessed shared state
- **Partitioning**: Partition agents by function or geography