---
name: hypura-workflow
description: Complete workflow for setting up LLM inference servers with hypura, including model downloads, server startup, and troubleshooting with GGUF models
metadata: {
  "openclaw": {
    "category": "hypura",
    "tags": ["hypura", "model-setup", "server", "deployment"],
    "required_commands": ["hypura"],
    "requires": {"bins": ["hypura"]}
  }
}
---

# Hypura Workflow

This skill covers the complete workflow for setting up LLM inference servers with hypura, from model preparation through server startup to troubleshooting. It includes patterns for running downloaded models and handling hypura validation errors.

## When to Use

- Downloading GGUF models from Hugging Face
- Setting up hypura servers with large models that need high context lengths
- Troubleshooting hypura metadata validation errors ("No TurboQuant research sidecar...")
- Configuring hypura for models larger than available RAM using NVMe streaming
- Setting up LLM inference as a service (background server)

## Prerequisites

- `hypura` binary installed (see `hermes skills install hypura`)
- Downloaded model file with supported extension (.gguf, etc.)
- Sufficient disk space for model + hypura cache

## Quick Start

```bash
# Download model (replace with your desired model)
hf download MODEL_ID --include "*.gguf"

# Start hypura server with high context length
hypura serve ./model.gguf --host 0.0.0.0 --port 8080 --context 65536 --turboquant-mode exact

# Check server status
curl http://127.0.0.1:8080/api/tags
```

## Model Validation Issues

**Common errors and fixes:**

### 1. "No TurboQuant research sidecar or GGUF metadata found"
```bash
# This happens with downloaded models that lack embedded metadata
hypura serve ./model.gguf --turboquant-mode exact --context 65536
```

### 2. "Fail-closed is active"
```bash
# Exact mode bypasses metadata validation for downloaded models
hypura serve ./model.gguf --turboquant-mode exact
```

### 3. High memory requirements
```bash
# Enable NVMe streaming for large models
hypura serve ./model.gguf --turboquant-mode exact --context 65536
```

## Configuration Templates

### For downloaded models

```bash
# Full command with optimal settings for downloaded models
hypura serve \
  ./model.gguf \
  --host 0.0.0.0 \
  --port 18900 \
  --context 65536 \
  --turboquant-mode exact \
  # Optional: custom config if you have one
  # --turboquant-config ./tq_config.json
```

### For baseline benchmarking

```bash
# Testing with small tokens first
hypura bench --max-tokens 10 ./model.gguf

# Then full benchmarking (add --force if model > RAM-4GB)
hypura bench --baseline --force --max-tokens 100 ./model.gguf
```

### For hardware profiling

```bash
# Check what hypura detects
hypura profile

# Show cached configuration
hypura profile --show
```

## Model Sources

### Hugging Face downloads

```bash
# Download with tokenization for the local directory
hf download MODEL_ID --include "*.gguf" --local-dir ./models
```

### Local file paths

```bash
# Use already downloaded models
hypura serve ./local/path/to/model.gguf --context 65536
```

## Troubleshooting

### Server won't start

1. **Check disk space:**
   ```bash
   df -h
   du -sh ./model.gguf
   ```

2. **Verify model file:**
   ```bash
   hypura serve ./model.gguf --turboquant-mode exact
   ```

3. **Check model compatibility:**
   ```bash
   # Test with small context first
   hypura serve ./model.gguf --context 1024
   ```

### High memory model error

```bash
# Force baseline if you have enough disk space
hypura bench --baseline --force --max-tokens 10 ./model.gguf
```

### Connection issues

```bash
# Check if server is bound to correct host
curl http://127.0.0.1:8080/api/tags
curl http://0.0.0.0:8080/api/tags
```

## Automation

### Systemd service example

Create `/etc/systemd/system/hypura.service`:

```ini
[Unit]
Description=Hypura LLM Inference Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/model
ExecStart=/usr/local/bin/hypura serve ./model.gguf --host 0.0.0.0 --port 8080 --context 65536 --turboquant-mode exact
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hypura
sudo systemctl start hypura
```

## Monitoring

### Process status

```bash
# Check hypura process
ps aux | grep hypura

# Check port usage
netstat -tlnp | grep :8080
```

### Logs

Hypura logs to stdout/stderr. Consider redirecting:

```bash
# Background with logs
hypura serve ./model.gguf --host 0.0.0.0 --port 8080 --context 65536 --turboquant-mode exact > hypura.log 2>&1 &
```

## Common Workflows

### 1. Development setup

```bash
# Download and test a small model
hf download tiny-model --include "*.gguf"
hypura serve ./tiny-model.gguf --context 1024
# Use for testing, then upgrade to production
```

### 2. Production deployment

```bash
# Download large model
hf download large-model --include "*.gguf"

# Start with highest context length
hypura serve ./large-model.gguf --host 0.0.0.0 --port 18900 --context 65536 --turboquant-mode exact
```

### 3. Benchmarking new hardware

```bash
# Run hardware profile first
hypura profile

# Then benchmark the model
hypura bench --max-tokens 10 ./model.gguf
```

## Cleanup

```bash
# Stop server
hypura stop --port 8080

# Clear hypura cache (if needed)
rm -rf ~/.hypura
```

## Notes

- Hypura uses a fail-closed validation by default. For downloaded models that lack embedded metadata, always use `--turboquant-mode exact`.
- The first time you run hypura with a new model, it may take longer while initializing.
- Hypura automatically selects the best streaming mode based on model size and hardware capabilities.
- For the best NVMe performance, ensure your model file is on a fast storage device.
