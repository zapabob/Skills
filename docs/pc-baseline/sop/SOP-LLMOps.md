# SOP LLMOps

## Scope

Apply this SOP to prompt systems, model integrations, RAG systems, agent workflows, tool use, safety rails, evaluation pipelines, and production LLM operations.

## Mandatory Controls

1. Version prompts, system instructions, tool schemas, safety policies, and evaluation sets.
2. Track model name, provider, version, temperature, context policy, and tool configuration per release.
3. Separate offline evaluation, staging validation, and production rollout decisions.
4. Define prompt injection, data leakage, hallucination, unsafe tool use, and availability failure modes.
5. Require human override or circuit breakers for high-impact actions.

## Data and Privacy

1. Classify data before sending it to external models or APIs.
2. Minimize secrets, PII, proprietary source, and regulated content in prompts.
3. Log sensitive workflows in a way that preserves auditability without leaking secrets.

## Evaluation

1. Use regression evals for safety, factuality, tool selection, and task success.
2. Keep golden cases and adversarial cases under version control.
3. Promotion decisions must cite evaluation evidence, not intuition alone.

## Runtime Operations

1. Capture latency, cost, token use, failure rates, and fallback behavior.
2. Make provider failures, timeout behavior, and degraded-mode behavior explicit.
3. Disable unsafe autonomous actions when confidence, policy, or dependency health degrades.

## Release Gate

- Prompt and model changes are versioned
- Evaluation evidence exists
- Safety and rollback behavior is defined
- Internet connectivity and secret handling follow `SOP-Internet-Connectivity.md`
