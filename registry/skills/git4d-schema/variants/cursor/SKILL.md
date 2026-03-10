---
name: git4d-schema
description: "Git4D Schema Auditor - Validate Git4D configurations, schema definitions, and DevOps pipeline integrity."
short_description: Git4D Schema Auditor - Validate Git4D configurations, schema definitions, and DevOps pipeline integrity.
---

# Git4D Schema Auditor Agent Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

Git4D Schema Auditor validates Git4D configurations, schema definitions, and DevOps pipeline integrity. Ensures all Git4D configurations follow best practices and maintain pipeline consistency.

## Capabilities

- **Schema Validation**: Validate Git4D schema definitions
- **Configuration Audit**: Audit Git4D configuration files
- **Pipeline Integrity**: Verify DevOps pipeline configurations
- **Best Practices Enforcement**: Ensure Git4D best practices
- **Version Compatibility**: Check schema version compatibility
- **Documentation Validation**: Validate documentation consistency

## Cursor Tools

This skill uses the following Cursor-native tools:

| Tool | Purpose |
|------|---------|
| `Read` | Read files from the codebase |
| `Grep` | Search for patterns in code (regex) |
| `SemanticSearch` | Find code by meaning, not exact text |
| `Write` | Create new files |
| `StrReplace` | Edit existing files with precise replacements |
| `Shell` | Execute terminal commands |
| `WebSearch` | Search the web for documentation/references |
| `WebFetch` | Fetch content from URLs |
| `Task` | Launch subagents for complex parallel work |
| `ReadLints` | Check for linter errors after edits |

## Usage Examples

### Basic Schema Validation

### Configuration Audit

### Pipeline Integrity Check

## Git4D Schema Structure

```
.git4d/
├── schema/
│   ├── v1.0/
│   │   ├── pipeline.schema.json
│   │   ├── config.schema.json
│   │   └── runtime.schema.json
│   └── current -> v1.0/
├── configs/
│   ├── pipeline.yaml
│   ├── runtime.yaml
│   └── deployment.yaml
└── .git4drc
```

## Schema Validation Rules

| Rule            | Severity | Description                        |
| --------------- | -------- | ---------------------------------- |
| required_fields | Error    | Required fields must exist         |
| type_check      | Error    | Fields must have correct types     |
| enum_values     | Error    | Enum fields must have valid values |
| pattern_match   | Warning  | String fields must match patterns  |
| best_practice   | Info     | Should follow best practices       |

## Configuration Validation

### Pipeline Configuration

```yaml
pipeline:
  stages:
    - name: build
      type: docker
      image: rust:1.75
    - name: test
      type: shell
      script: cargo test
    - name: deploy
      type: approval
      requires: test
```

### Runtime Configuration

```yaml
runtime:
  gpu:
    required: true
    min_memory: "16GB"
    cuda_version: "12.0"
  cpu:
    cores: 4
    architecture: "x86_64"
```

## Output Format

The git4d-schema agent provides:

- Schema validation report
- Configuration audit results
- Pipeline integrity status
- Best practices scorecard
- Version compatibility matrix

- [Git4D GitHub](https://github.com/zapabob/codex-git4d)
- [Schema Validation](https://json-schema.org/)
- [YAML Best Practices](https://yaml.org/spec/)
- [DevOps Pipeline](https://docs.github.com/en/actions/pipelines)

---

$ the skill-install skill https://github.com/zapabob/codex-git4d-schema-skill`
**Version**: 1.0.0
