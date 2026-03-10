---
name: cicd-integration
description: Comprehensive CI/CD integration agent that manages continuous integration and deployment pipelines with automated quality assurance, multi-platform support, and intelligent workflow orchestration. Seamlessly integrates with GitHub Actions, GitLab CI, Jenkins, CircleCI, and Azure DevOps for end-to-end DevOps automation.
short_description: Comprehensive CI/CD integration agent that manages continuous integration and deployment pipelines with automated quality assurance, multi-p
---
# CI/CD Integration Agent Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

Comprehensive CI/CD integration agent that manages continuous integration and deployment pipelines with automated quality assurance, multi-platform support, and intelligent workflow orchestration. Seamlessly integrates with GitHub Actions, GitLab CI, Jenkins, CircleCI, and Azure DevOps for end-to-end DevOps automation.

## Capabilities

- **Pipeline Generation**: Automated CI/CD pipeline creation for multiple platforms
- **Quality Gates**: Intelligent merge blocking based on QA analysis results
- **Multi-Platform Support**: Unified interface across all major CI/CD platforms
- **Artifact Management**: Automated build artifact handling and deployment
- **Notification Integration**: Real-time status updates via Slack, Discord, Email
- **Performance Monitoring**: Pipeline performance tracking and optimization
- **Security Scanning**: Automated security vulnerability detection in pipelines

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

### Generate CI/CD Pipeline

### Setup GitHub Actions Workflow

### Multi-Platform CI/CD Setup

### Pipeline Optimization

## Output Format

### CI/CD Pipeline Report
```
ð CI/CD Integration Report - Multi-Platform Pipeline Setup
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
Project: zapabob/codex
Generated: 2026-01-04 16:30:00 UTC
Platforms: GitHub Actions, GitLab CI, Jenkins
Duration: 45.2 seconds

ð Pipeline Overview
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
Total Pipelines: 3
Active Stages: 5 (test, qa, build, deploy, monitor)
Quality Gates: 4 (code-review, qa-analysis, security, performance)
Environments: development, staging, production

ð Pipeline Flow
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
1. ð Code Analysis (GitHub Actions)
   âââ Lint & Format: âEPASSED
   âââ Type Check: âEPASSED
   âââ Security Scan: âEPASSED
   âââ Duration: 2.3 minutes

2. ð§ª Testing & QA (All Platforms)
   âââ Unit Tests: âEPASSED (94% coverage)
   âââ Integration Tests: âEPASSED
   âââ QA Analysis: âEPASSED (A- grade)
   âââ Duration: 8.7 minutes

3. ð¦ Build & Package (Parallel)
   âââ Linux Build: âEPASSED (x86_64)
   âââ macOS Build: âEPASSED (x86_64, arm64)
   âââ Windows Build: âEPASSED (x86_64)
   âââ Docker Images: âEPASSED (3 variants)
   âââ Duration: 12.4 minutes

4. ð Deployment (Staged)
   âââ Development: âEDEPLOYED
   âââ Staging: âEDEPLOYED
   âââ Production: â³ PENDING (manual approval)
   âââ Rollback Plan: âEGENERATED

5. ð Monitoring & Alerts (Continuous)
   âââ Health Checks: âEACTIVE
   âââ Performance Monitoring: âEACTIVE
   âââ Error Tracking: âEACTIVE
   âââ Alert Rules: âECONFIGURED

ð¡EEQuality Gates Status
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
âââââââââââââââââââ¬âââââââââââââ¬âââââââââââââ¬ââââââââââââââââââ¬ââââââââââââââE
âEGate            âEStatus     âEPlatform   âEDuration        âEConfidence  âE
âââââââââââââââââââ¼âââââââââââââ¼âââââââââââââ¼ââââââââââââââââââ¼ââââââââââââââ¤
âECode Review     âEâEPASSED  âEAll        âE3.2s            âE98%         âE
âESecurity Scan   âEâEPASSED  âEGitHub     âE45.7s           âE95%         âE
âEQA Analysis     âEâEPASSED  âEAll        âE127.3s          âE92%         âE
âEPerformance     âEâEPASSED  âEJenkins    âE89.4s           âE88%         âE
âEManual Review   âEâ³ PENDING âEProduction âE-               âE-           âE
âââââââââââââââââââ´âââââââââââââ´âââââââââââââ´ââââââââââââââââââ´ââââââââââââââE

ð Generated Artifacts
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
GitHub Actions:
âââ .github/workflows/ci.yml (2.3KB)
âââ .github/workflows/qa.yml (3.1KB)
âââ .github/workflows/deploy.yml (4.2KB)
âââ .github/dependabot.yml (1.8KB)

GitLab CI:
âââ .gitlab-ci.yml (5.6KB)
âââ .gitlab/deploy.yml (2.1KB)
âââ .gitlab/monitoring.yml (1.9KB)

Jenkins:
âââ Jenkinsfile (3.7KB)
âââ jenkins/pipeline.groovy (2.8KB)
âââ jenkins/deploy.groovy (1.6KB)

Docker:
âââ Dockerfile (1.2KB)
âââ docker-compose.yml (2.4KB)
âââ .dockerignore (0.8KB)
âââ build/Dockerfile.multiarch (1.9KB)

Kubernetes:
âââ k8s/deployment.yml (3.1KB)
âââ k8s/service.yml (1.4KB)
âââ k8s/ingress.yml (2.2KB)
âââ k8s/configmap.yml (1.7KB)

Monitoring:
âââ monitoring/prometheus.yml (2.9KB)
âââ monitoring/grafana-dashboard.json (4.3KB)
âââ monitoring/alert-rules.yml (1.6KB)
âââ monitoring/health-checks.sh (0.9KB)

âï¸EConfiguration Files
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
âââ cicd-config.yml (3.2KB) - Main CI/CD configuration
âââ environments/dev.yml (1.8KB) - Development environment
âââ environments/staging.yml (2.1KB) - Staging environment
âââ environments/prod.yml (2.4KB) - Production environment
âââ secrets/encrypted (2.1KB) - Encrypted secrets
âââ scripts/deploy.sh (3.7KB) - Deployment automation

ð Performance Metrics
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
Total Pipeline Time: 28.7 minutes
Average Stage Time: 5.7 minutes
Resource Utilization: 67% CPU, 2.3GB RAM
Cost Efficiency: $0.23 per build
Success Rate: 94.2% (last 30 days)

ð¨ Active Alerts
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
1. â EEPerformance Regression
   - Pipeline duration increased by 23%
   - Affected: QA Analysis stage
   - Recommendation: Optimize QA rules or increase compute resources

2. ð Resource Usage High
   - Memory usage above 80% threshold
   - Duration: Last 3 builds
   - Recommendation: Implement resource limits or scale compute

ð Integration Status
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
GitHub Actions: âEConnected (12 workflows active)
GitLab CI: âEConnected (8 pipelines active)
Jenkins: âEConnected (5 jobs active)
Docker Registry: âEConnected (14 images)
Kubernetes: âEConnected (3 clusters)
Monitoring: âEConnected (8 dashboards)

ð¡ Optimization Recommendations
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
1. Implement build caching to reduce pipeline time by ~40%
2. Add parallel test execution to reduce QA stage time by ~50%
3. Configure auto-scaling for high-load periods
4. Implement blue-green deployments for zero-downtime updates
5. Add chaos engineering tests to improve resilience

ð¯ Next Steps
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
1. Review and approve production deployment
2. Monitor first production deployment
3. Configure automated rollbacks for failures
4. Set up canary deployments for gradual rollouts
5. Implement feature flags for safer deployments

ð Success Metrics
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
Deployment Frequency: 12/day (target: 10-15/day)
Change Failure Rate: 3.2% (target: <5%)
Mean Time to Recovery: 8.4 minutes (target: <10min)
Lead Time for Changes: 2.1 hours (target: <4 hours)

ð Quality Score: A+ (Excellent CI/CD Implementation)
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââE
Automation Level: 92%
Reliability Score: 94%
Performance Rating: A-
Security Compliance: A+
Monitoring Coverage: 98%
```

### Pipeline Configuration JSON
```json
{
  "cicd_integration_report": {
    "timestamp": "2026-01-04T16:30:00Z",
    "project": "zapabob/codex",
    "platforms": ["github-actions", "gitlab-ci", "jenkins"],
    "pipeline_summary": {
      "total_pipelines": 3,
      "active_stages": 5,
      "quality_gates": 4,
      "environments": ["development", "staging", "production"]
    },
    "generated_files": {
      "github_actions": [
        ".github/workflows/ci.yml",
        ".github/workflows/qa.yml",
        ".github/workflows/deploy.yml"
      ],
      "gitlab_ci": [
        ".gitlab-ci.yml",
        ".gitlab/deploy.yml"
      ],
      "jenkins": [
        "Jenkinsfile",
        "jenkins/pipeline.groovy"
      ],
      "docker": [
        "Dockerfile",
        "docker-compose.yml"
      ],
      "kubernetes": [
        "k8s/deployment.yml",
        "k8s/service.yml"
      ],
      "monitoring": [
        "monitoring/prometheus.yml",
        "monitoring/grafana-dashboard.json"
      ]
    },
    "performance_metrics": {
      "total_pipeline_time_minutes": 28.7,
      "average_stage_time_minutes": 5.7,
      "resource_utilization": {
        "cpu_percent": 67,
        "memory_gb": 2.3
      },
      "cost_per_build_usd": 0.23,
      "success_rate_percent": 94.2
    },
    "quality_gates": [
      {
        "name": "code_review",
        "status": "passed",
        "platforms": ["all"],
        "duration_seconds": 3.2,
        "confidence_percent": 98
      },
      {
        "name": "qa_analysis",
        "status": "passed",
        "platforms": ["all"],
        "duration_seconds": 127.3,
        "confidence_percent": 92
      }
    ],
    "recommendations": [
      "Implement build caching to reduce pipeline time by ~40%",
      "Add parallel test execution to reduce QA stage time by ~50%",
      "Configure auto-scaling for high-load periods"
    ]
  }
}
```

## Pipeline Architecture

### Multi-Platform Orchestration
```
âââââââââââââââââââE   ââââââââââââââââââââE
âE  CI/CD Agent   ââââââE  Platform APIs  âE
âE  Orchestrator  âE   âE                 âE
âE                âE   ââââââââââââââââââââE
âââââââââââââââââââE            âE
         âE                     âE
         ââââââââââââââââââââââââ¤
         âE                     âE
    ââââââ¼âââââE   âââââââââââââââE   âââââââââââââââE
    âEGitHub   âE   âE  GitLab    âE   âE  Jenkins   âE
    âEActions  âE   âE    CI     âE   âE            âE
    âââââââââââE   âââââââââââââââE   âââââââââââââââE
         âE             âE             âE
         ââââââââââââââââ¼âââââââââââââââE
                        âE
               ââââââââââ¼âââââââââE
               âE Unified Status âE
               âE  & Reporting   âE
               âââââââââââââââââââE
```

### Quality Gate Pipeline
```
Code Push/PR âELint & Format âESecurity Scan âEUnit Tests
       âE                                              âE
Build & Package âEQA Analysis âEIntegration Tests âââââE
       âE
Deploy to Dev âEDeploy to Staging âEManual Review âEDeploy to Prod
       âE             âE                     âE             âE
Health Checks   Performance Tests   Security Tests   Monitoring
```

## Configuration

### Main CI/CD Configuration
```yaml
cicd:
  platforms:
    - github_actions
    - gitlab_ci
    - jenkins

  environments:
    development:
      auto_deploy: true
      tests_required: ["unit"]
      approval_required: false

    staging:
      auto_deploy: true
      tests_required: ["unit", "integration"]
      approval_required: false

    production:
      auto_deploy: false
      tests_required: ["unit", "integration", "e2e", "performance"]
      approval_required: true

  quality_gates:
    - name: code_review
      required: true
      blocking: true

    - name: security_scan
      required: true
      blocking: true

    - name: qa_analysis
      required: true
      blocking: true

    - name: performance_test
      required: true
      blocking: false

  notifications:
    slack:
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channels:
        - "#deployments"
        - "#qa-alerts"

    email:
      smtp_server: "smtp.company.com"
      recipients:
        - "devops@company.com"
        - "qa@company.com"
```

### Platform-Specific Configurations
```yaml
# GitHub Actions specific
github_actions:
  workflows:
    - name: "CI Pipeline"
      path: ".github/workflows/ci.yml"
      triggers:
        - push:
            branches: [main, develop]
        - pull_request:
            branches: [main, develop]

  runners:
    - ubuntu-latest
    - windows-latest
    - macos-latest

# GitLab CI specific
gitlab_ci:
  image: "node:18"
  stages:
    - test
    - build
    - deploy

  cache:
    key: "${CI_COMMIT_REF_SLUG}"
    paths:
      - node_modules/
      - .cache/

# Jenkins specific
jenkins:
  agent: "docker"
  tools:
    nodejs: "NodeJS 18.0.0"

  options:
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
```

## Integration Points

### Development Workflow Integration
```bash
# Generate complete CI/CD setup
the cicd-integration skill "Setup multi-platform CI/CD with QA gates"

# Update existing pipelines
the cicd-integration skill "Update CI/CD pipelines with new QA requirements"

# Optimize pipeline performance
the cicd-integration skill "Analyze and optimize pipeline performance"
```

### Repository Integration
```bash
# Initialize CI/CD for new repository
the cicd-integration skill "Initialize CI/CD for new project"

# Migrate from single platform to multi-platform
the cicd-integration skill "Migrate Jenkins to multi-platform CI/CD"

# Setup monorepo CI/CD
the cicd-integration skill "Setup CI/CD for monorepo with multiple services"
```

### Deployment Integration
```bash
# Setup blue-green deployments
the cicd-integration skill "Configure blue-green deployment strategy"

# Setup canary deployments
the cicd-integration skill "Configure canary deployment with traffic splitting"

# Setup rollback automation
the cicd-integration skill "Configure automated rollback on failures"
```

## Performance Optimization

### Pipeline Caching Strategies
- **Dependency Caching**: Cache node_modules, target/, .cache/ directories