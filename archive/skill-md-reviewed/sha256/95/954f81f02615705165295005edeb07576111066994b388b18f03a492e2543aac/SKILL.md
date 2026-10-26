---
name: adaptive-skill-runtime
description: Adapt multi-skill or plugin workflows to Astra or an earlier model when model selection, unsupported tools, context limits, or legacy agent metadata need compatibility handling. Use for model migration and cross-model workflow maintenance.
---

# Adaptive Skill Runtime

Complete the requested task using the selected model and the capabilities actually exposed by the host. This skill supplies workflow guidance, not a model switch, permission grant, or substitute tool implementation.

## Model and tool contract

Preserve explicit model choices, fixed agent-role settings, authorization, and invocation policies. Otherwise inherit the session model and reasoning effort. Do not put model, temperature, token limits, or fabricated tool names into agents/openai.yaml; it is host metadata. Keep instructions in SKILL.md or linked references.

Use the live tool schema and host model catalog. A cached catalog is an observation, not proof of current availability. Do not infer a context window, tool support, cost, concurrency limit, or reasoning value from a model name. Read [compatibility.md](references/compatibility.md) when switching models or handling a missing capability.

## Execution

For Astra, express the requested outcome, relevant constraints, permitted write scope, and verification criteria once. Read only the skill and references needed by the immediate task. Batch independent read-only operations when supported; sequence dependent operations and writes. Use a plan only when it resolves real uncertainty.

For an earlier or unidentified model, preserve the same acceptance criteria. Use bounded steps and inspect each dependent result before continuing. On long work, save a concise checkpoint with decisions, changed files, evidence, and remaining work; reread the relevant state after a model switch or context reset. Do not assume every earlier model has a smaller context.

Delegation requires both available tools and authorization from the current instructions. When unavailable, perform the work sequentially in the current task and label any independent-review requirement as unmet. Do not invent subagent results. Never replace a required specialist check with a weaker check merely to finish.

Report completed work, actual verification, and any unresolved limitation. If an external mutation may already have succeeded, inspect its state before retrying. Model or tool failures never justify changing credentials, permission policy, or the user's chosen product.

## Optional diagnostic

When model/effort compatibility is uncertain, run the read-only helper from the plugin root:

```powershell
uv run --no-project python scripts/runtime_profile.py --catalog <models-json> --current-model <selected-model>
```

It prints a proposed profile, performs no model request, and edits no configuration. Omitting override parameters is the normal way to inherit settings. Run `uv run --no-project python -m unittest discover -s tests` when changing its selection logic.
