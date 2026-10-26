---
name: switchyard-integration
description: Route LLM calls through Switchyard for cost/performance optimization
version: 1.0.0
tags: [routing, model-selection, cost-optimization, switchyard]
---

# Switchyard Integration Skill

## When to Use

- Use when you want to route LLM calls through Switchyard for automatic model selection based on cost and capability
- When you want to preserve native OpenAI/Anthropic API compatibility while gaining flexible model selection
- When integrating with gateways that support Switchyard (NeMo Relay, LiteLLM, standalone proxy)
- When you want to reduce LLM costs while maintaining or improving accuracy

## Prerequisites

- Switchyard installed: `pip install git+https://github.com/NVIDIA-NeMo/Switchyard.git`
- OR Switchyard server running: `switchyard-server --config routes.toml --port 4000`
- Gateway integration: NeMo Relay plugin or LiteLLM router plugin
- Configured routes.toml with model definitions and routing policies

## How to Run

### Path 1 — Via NeMo Relay Plugin

```bash
# 1. Build and register the Switchyard NeMo Relay plugin
# Follow the plugin install guide in crates/switchyard-nemo-relay-plugin/README.md

# 2. Configure Switchyard routes
# Copy routes.toml from step 2 of Path 3 below to /etc/switchyard/routes.toml

# 3. Enable the plugin in NeMo Relay
nemo-relay plugins enable nvidia.switchyard

# 4. Route requests through Relay with Switchyard enabled
# Relay will now use Switchyard algorithms for per-turn model selection
```

### Path 2 — Embed the Library

```python
from switchyard.libsy import LlmResponse, Step
from switchyard.libsy.algorithms import stage_router

# Construct the routing algorithm
algorithm = stage_router(
    "capable",
    "efficient",
    picker="efficient_first",
    confidence_threshold=0.5,
)

# Drive the router with requests
async def route_llm_call(request, models, clients):
    error = None
    for model in models:
        try:
            response = await call_model(model, request)
            return LlmResponse.Agg.collect(response)
        except Exception as e:
            error = e
            continue
    raise error
```

### Path 3 — Standalone Proxy

```bash
# Install and start the Switchyard server
cargo install --locked switchyard-server
switchyard-server --config routes.toml --port 4000

# Point your SDK client at the proxy
# All requests will be routed per-turn by Switchyard
```

## Procedure

1. **Configure routes.toml** — Define your model hierarchy with `capable` and `efficient` tiers, specifying costs, latencies, and capabilities
2. **Initialize the router** — Use `stage_router` with your model tier names and preferred picker strategy (`efficient_first`, `cheapest_first`, `performance_first`)
3. **Per-request routing** — For each LLM call, pass the request through the router which returns the selected model name
4. **Make the call** — Use your preferred model client to make the actual API call to the selected model
5. **Collect the response** — Return the model response through the LlmResponse aggregator for consistent formatting

## Pitfalls

- **Not pinning versions** — Switchyard APIs may change between releases; pin the exact version you integrate
- **Missing model capability definitions** — Ensure all models in routes.toml have proper capability tags (reasoning, vision, code, etc.)
- **Incorrect tier assignments** — Models must be correctly classified as `capable` or `efficient` for the router to work
- **Fallback not configured** — Always define a fallback model in case all primary models fail
- **Ignoring cost vs. accuracy tradeoffs** — The router optimizes for cost, but you must verify accuracy remains acceptable for your use case

## Verification

- Test with `switchyard-test` or equivalent to verify routing decisions
- Verify API compatibility — ensure routed calls maintain OpenAI/Anthropic wire format
- Check cost reduction — compare per-call costs before and after Switchyard integration
- Monitor routing accuracy — ensure the selected models maintain acceptable task performance
- Verify fallback paths work when primary models are unavailable

## Support Files

- `references/switchyard-toml-schema.md` — TOML schema for routes.toml configuration
- `templates/switchyard-routes.toml` — Example routes configuration file
- `scripts/verify-switchyard.py` — Verification script to test routing behavior

## Related Skills

- `dynamo-router-starter` — For Dynamo router integration
- `omh-meta-router` — For meta-routing within Oh My Hermes
- `model-selection` — General model selection patterns