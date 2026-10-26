---
name: memory-redundant-backup
description: Create redundant backups of Hermes memory in both machine-readable and human-readable formats.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [memory, backup, redundant]
    related_skills: [memory-maintenance, memory-composite-system]
---

# Memory Redundant Backup

This skill provides a tool to create backups of the built-in Hermes memory (MEMORY.md and USER.md) in a timestamped directory under `~/.hermes/memory_backups/`. The backup is both machine-readable (exact copies of the original files) and human-readable (markdown files that can be viewed in any text editor).

## When to Use

- Before making significant changes to memory
- As a periodic backup strategy
- When you want to preserve a snapshot of memory for audit or recovery

## Prerequisites

- Hermes Agent installed and running
- Write access to `~/.hermes/memory_backups/`

## How to Run

Use the `memory_redundant_backup` tool via the agent interface or terminal:

```bash
hermes tools memory_redundant_backup
```

Or invoke it directly in a conversation:

```
hermes memory_redundant_backup
```

## Quick Reference

- `memory_redundant_backup()` — Performs a backup of MEMORY.md and USER.md to a timestamped directory.

## Procedure

1. The tool locates the current Hermes home directory.
2. It reads MEMORY.md and USER.md from the Hermes home.
3. It creates a timestamped directory under `~/.hermes/memory_backups/` (format: YYYY-MM-DD_HH-MM-SS).
4. It writes copies of MEMORY.md and USER.md to this directory.
5. It also creates a `README.md` in the backup directory explaining the backup.
6. The tool returns the path to the backup directory.

## Pitfalls

- Ensure the `~/.hermes/memory_backups/` directory exists and is writable.
- The tool does not overwrite existing backup directories; each backup gets a unique timestamp.
- If MEMORY.md or USER.md does not exist, the tool will skip that file and log a warning.

## Verification

- After running, check the `~/.hermes/memory_backups/` directory for a new timestamped folder.
- Verify that the folder contains MEMORY.md, USER.md, and README.md.
- The contents of MEMORY.md and USER.md should match the originals at the time of backup.
