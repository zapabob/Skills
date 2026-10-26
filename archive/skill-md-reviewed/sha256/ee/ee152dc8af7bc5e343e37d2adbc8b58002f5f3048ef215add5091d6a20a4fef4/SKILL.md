---
name: hermes-custom-model-registration
description: Register custom models with Hermes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [configuration, model-registration, custom-providers]
    related_skills: []
---
# Hermes Custom Model Registration

**Trigger:** When a model is not appearing in Hermes model selection despite being configured for a local or custom provider.

**Context:** This skill documents how to register custom models with Hermes when they don't appear in the default model selection UI.

**Problem:** Model `qwen3.8-27b-abliterated-mtp` was not appearing in model selection despite being configured for local llama-server at `127.0.0.1:8080`.

**Root Cause:** The `load_config()` function reads from the profile-specific config at `$HOME/.hermes/profiles/job-seeker/config.yaml`, which was missing the model entry in the `custom_providers` section.

**Fix:** Add the model to the `custom_providers` section in the profile-specific config file:

```yaml
custom_providers:
  - api_key: local
    base_url: http://127.0.0.1:8080/v1
    context_length: 65536
    model: qwen3.8-27b-abliterated-mtp
    name: 127.0.0.1-8080
```

**File:** `$HOME/.hermes/profiles/job-seeker/config.yaml`

**Verification:** After the fix, `get_compatible_custom_providers()` returns the model, and it's available for model selection.

**Related:**
- Profile config: `$HOME/.hermes/profiles/<profile>/config.yaml`
- Root config: `~/.hermes/config.yaml` (project-level, not used by `load_config()` by default)
- `get_compatible_custom_providers()` function in `hermes_cli/config.py`