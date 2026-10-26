# SOP AIOps

## Scope

Apply this SOP to AI-assisted incident detection, alert triage, remediation recommendations, automated runbooks, and operational decision support.

## Mandatory Controls

1. Keep human authority over destructive, privileged, or high-blast-radius actions.
2. Version automation rules, prompts, thresholds, and remediation playbooks.
3. Record who or what triggered an action, why it triggered, and what evidence supported it.
4. Require explicit containment logic for false positives and model mistakes.

## Operational Safety

1. Prefer recommendation mode before autonomous action mode.
2. Gate automated remediation behind policy checks and environment safety checks.
3. Enforce rate limits, retries, and suppression rules to avoid alert storms or remediation loops.

## Observability

1. Capture alert input, AI reasoning summary, selected action, and final outcome.
2. Preserve correlation IDs across logs, incidents, and remediation runs.
3. Keep audit evidence suitable for postmortem review.
