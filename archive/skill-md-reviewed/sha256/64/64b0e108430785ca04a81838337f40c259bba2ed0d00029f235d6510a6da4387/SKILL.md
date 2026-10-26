---
name: orchestrator
description: Coordinate complex work across skills when task dependencies, integration, or separate review need explicit management. Use available authorized agents or sequential local execution; ordinary single-step tasks do not need orchestration.
---

# Orchestrator

Define the requested outcome, acceptance criteria, relevant dependencies, and permitted changes. Select only the skills needed for this task. Keep the immediate blocking step local. Use [role guidance](references/role-guidance.md) for domain conventions and scope restrictions; its coordination role does not imply an installed agent framework.

## Runtime selection

Inherit the current model and reasoning effort, including Astra or an earlier model. Respect explicit user choices and fixed specialist-role settings. Consult actual host model metadata before sending any override. Never infer tool support, context size, concurrency, or effort values from a model name.

For Astra, describe each work item's objective, inputs, constraints, output, and acceptance criteria concisely. Read references only when needed and batch independent read-only operations when supported. For earlier or unknown models, use smaller work items and explicit checkpoints with the same acceptance criteria. On resume or model change, reread the saved goal, decisions, ownership, evidence, and remaining work.

## Execution and integration

Use delegation only when current instructions authorize it, a runner is available, and a bounded independent subtask can proceed alongside useful local work. Give workers minimal relevant context and disjoint write ownership. Tell them other changes may exist and must be preserved. Fixed role settings remain unchanged.

When delegation is unavailable or unauthorized, perform the same work sequentially in the current task. Do not simulate agents, invent messages, or claim independent review. If independent review is a required acceptance condition, report it as unmet until an authorized reviewer completes it.

Use real tool schemas and available capabilities. A generic tool name in an old example is not an endpoint. Do not start an MCP server or expose a network listener merely to run this skill. Use project-native commands verified by local help or documentation.

Integrate results against the actual diff and artifacts. Resolve conflicts explicitly, run relevant tests, and retain the original acceptance criteria. For an uncertain external mutation, inspect whether it succeeded before retrying. Permission or capability failures never justify relaxing controls or changing the user's product.

## Completion

Keep workflow artifacts within ./artifacts, ./workflows, or ./reports unless the task specifies another authorized location. Use goal tools only when the user explicitly requests a goal. Use a separate user-visible task only when the user asks for one.

Report the delivered result, actual verification, deferred work, and material risks. Metrics require measurements. A written workflow plan or a worker's success message alone is not proof of completion.
