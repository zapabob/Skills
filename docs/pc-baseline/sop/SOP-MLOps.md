# SOP MLOps

## Scope

Apply this SOP to data pipelines, feature generation, training, model packaging, validation, deployment, monitoring, and retraining workflows.

## Mandatory Controls

1. Version datasets, labels, features, training code, and model artifacts.
2. Preserve experiment configuration and reproducibility metadata.
3. Separate training, validation, test, and production monitoring concerns.
4. Define acceptance thresholds for accuracy, robustness, drift, bias, latency, and cost.
5. Use controlled promotion from experiment to candidate to approved model.

## Data Governance

1. Record provenance, licensing, and permitted use of data sources.
2. Reject untraceable or policy-incompatible data.
3. Preserve lineage from raw data to features to model artifact.

## Validation

1. Require offline validation before deployment.
2. Add canary or staged rollout for production changes where practical.
3. Monitor drift, skew, degradation, and data quality continuously where the system is long-lived.

## Incident and Rollback

1. Keep previous known-good models available.
2. Define rollback triggers for degraded quality or unsafe behavior.
3. Record post-incident root cause and corrective actions.
