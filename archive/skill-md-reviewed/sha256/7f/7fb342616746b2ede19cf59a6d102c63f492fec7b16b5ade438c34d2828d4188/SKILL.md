---
name: moonshot-pipeline-plan-mode
description: Creates and manages execution plans for the integrated Moonshot Pipeline 2025-2026, including data collection (Arxiv top 50K, defense/JAXA whitepapers), SFT training, advanced technique integration (DeepseekGLPO, mHC, SO8T, imatrix), ABC testing, and HF upload. Use when planning complex multi-phase ML pipeline executions or when breaking down the Moonshot Pipeline into manageable steps.
---

# Moonshot Pipeline Plan Mode

## Overview

This skill helps create and manage execution plans for the integrated Moonshot Pipeline 2025-2026, which includes:

1. **Data Collection**: Arxiv top 50K papers, Japanese defense/JAXA whitepapers
2. **Dataset Verification**: NSFW, sexual, drug detection datasets (already collected)
3. **SFT Training**: Supervised Fine-Tuning with collected data
4. **Advanced Techniques Integration**: DeepseekGLPO, mHC manifold, SO8T quadrality, imatrix protection
5. **ABC Testing**: Industry-standard benchmark evaluation (A: baseline, B: Borea-phi3.5, C: Moonshot result)
6. **HF Upload**: Upload HF standard files and BF16 GGUF if performance improved

## Plan Structure

### Phase 1: Data Collection
- **Arxiv Top 50K**: Collect top 50,000 cited papers from Arxiv (2024-2026)
- **Defense/JAXA Whitepapers**: Collect Japanese defense and JAXA whitepapers using web-search-deepresearch
- **Checkpoint**: Save progress every 5 minutes with rolling backups

### Phase 2: Dataset Verification
- **NSFW Datasets**: Verify existing NSFW detection datasets
- **Drug Datasets**: Verify existing drug detection datasets
- **Purpose**: Detection training (not content generation)

### Phase 3: SFT Training
- **Input**: Collected Arxiv papers, whitepapers, NSFW/drug detection datasets
- **Model**: Borea-Phi-3.5-mini-Instruct-Jp
- **Output**: SFT-trained model

### Phase 4: Advanced Techniques Integration
- **DeepseekGLPO**: Group Relative Policy Optimization for emergent reasoning
- **mHC Manifold**: Manifold-constrained hyper-connections for stable scaling
- **SO8T Quadrality**: Four-perspective reasoning (triality + identity + duality)
- **imatrix Protection**: Importance-aware quantization for mathematical/scientific reasoning preservation
- **Geometric Scaling**: Manifold-preserving parameter optimization

### Phase 5: ABC Testing
- **Model A**: Baseline model
- **Model B**: Borea-phi3.5-instinct-jp
- **Model C**: Moonshot Pipeline result
- **Benchmarks**: GSM8K, MATH, ARC-Challenge, ELYZA Tasks 100
- **Statistical Analysis**: 5-seed testing with confidence intervals

### Phase 6: HF Upload (Conditional)
- **Condition**: Only if performance improved compared to previous results
- **Formats**: HF standard files (SafeTensors) + BF16 GGUF
- **Method**: HFCLI upload

## Usage

### Creating a Plan

```python
from scripts.pipeline.integrated_moonshot_pipeline_2025_2026 import IntegratedMoonshotPipeline2025_2026

pipeline = IntegratedMoonshotPipeline2025_2026()
plan = pipeline.create_execution_plan()
```

### Executing a Plan

```python
pipeline.execute_full_pipeline()
```

### Resuming from Checkpoint

```python
checkpoint = pipeline.load_checkpoint()
if checkpoint:
    pipeline.resume_from_checkpoint(checkpoint)
```

## Checkpoint System

- **Automatic Checkpoints**: Saved every 5 minutes
- **Rolling Backups**: Maximum 3 backups maintained
- **Resume Capability**: Can resume from any checkpoint
- **Power Failure Recovery**: Automatic recovery from power interruptions

## Error Handling

- **Retry Logic**: Automatic retry for transient failures
- **Graceful Degradation**: Continue with available data if some sources fail
- **Detailed Logging**: All operations logged with timestamps

## Performance Monitoring

- **Progress Bars**: tqdm-based progress visualization
- **Resource Usage**: CPU, GPU, memory monitoring
- **Time Estimates**: Remaining time calculations

## Integration Points

- **web-search-deepresearch**: Used for whitepaper collection
- **abctest subagent**: Used for ABC testing execution
- **HFCLI**: Used for HuggingFace uploads
- **Enhanced Moonshot Pipeline**: Core training and integration logic
