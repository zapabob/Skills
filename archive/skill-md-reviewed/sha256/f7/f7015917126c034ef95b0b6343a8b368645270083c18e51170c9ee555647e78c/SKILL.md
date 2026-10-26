---
name: hermes-repository-organization
description: Procedures for organizing Hermes repository structure according to project conventions, including moving scripts to appropriate directories and ensuring proper documentation exists.
version: 1.0.0
category: devops
---

# Hermes Repository Organization Skill

This skill provides procedures for organizing Hermes repository structure according to project conventions, including moving scripts to appropriate directories and ensuring proper documentation exists.

## Procedures

### 1. Identify Misplaced Root-Level Scripts

First, identify scripts in the repository root that should be moved to appropriate directories:

```bash
# List Python scripts in root that might belong elsewhere
ls *.py

# Look for extension-specific patterns
ls *_simulation.py *_simulator.py *_tool.py *_agent.py 2>/dev/null || true

# Check for Blender-related scripts
ls *blender* *blender* 2>/dev/null || true
```

Common patterns that indicate scripts belong in specialized directories:
- Blender directories:
- Blender scripts → scripts/blender/
- Web scraping/maintenance scripts → scripts/maintenance/
- Platform-specific tools → scripts/platforms/
- Utility scripts → scripts/utils/

### 2. Determine Correct Destination Directory

Based on file content and naming conventions:

#### Blender/Scripts
If the script:
- Uses bpy or bmesh modules
- References Blender-specific functionality
- Contains terms like "blender", "render", "mesh", "material" in comments or docstrings
→ Destination: `scripts/blender/`

#### Maintenance/Operations
If the script:
- Performs repository maintenance tasks
- Handles synchronization between repositories
- Cleans up temporary files
- Manages dependencies
→ Destination: `scripts/maintenance/`

#### Platform-Specific Tools
If the script:
- Interacts with a specific platform (Twitter/X, Discord, etc.)
- Contains platform-specific API calls
- Is designed to run as a standalone utility for a platform
→ Destination: `scripts/platforms/[platform-name]/`

#### Cron/Scheduled Jobs
If the script:
- Is designed to run as a scheduled/cron job
- Performs periodic maintenance or monitoring tasks
- Outputs safe summaries (JSON) for delivery
→ Destination: `cron/scripts/`

#### General Utilities
If the script:
- Provides general helper functions
- Is used by multiple other scripts
- Doesn't fit a specific category above
→ Destination: `scripts/utils/`

### 3. Move Files Preserving History

Use git move to preserve file history:

```bash
# Move single file
git mv old_path.py new_directory/new_path.py

# Move multiple files
git mv script1.py script2.py script3.py target_directory/

# Verify the move was recorded correctly
git log --follow --stat -- path/to/file.py
```

### 4. Create Required Documentation

For any directory containing functional code, ensure these files exist:

#### AGENTS.md (AI Agent Documentation)
This file should contain:
- Purpose of the scripts in this directory
- How AI agents should use these scripts
- Any important conventions or constraints
- References to related documentation
- Example usage patterns for agents

Template:
```markdown
# [Directory Name] Scripts

## Purpose
[Brief description of what these scripts do]

## Usage for AI Agents
- How to invoke these scripts
- Expected inputs/outputs
- Error handling patterns

## Conventions
- Any specific naming or structural conventions
- Dependencies or setup requirements

## Related Documentation
- Links to other relevant AGENTS.md files
- References to external documentation
```

#### README.md (Human Documentation)
This file should contain:
- Clear title and description
- Setup instructions if needed
- Usage examples
- Expected outputs
- Troubleshooting tips

### 5. Verify Documentation Completeness

Check that both AGENTS.md and README.md exist and contain appropriate content:

```bash
# Check for missing documentation
find scripts/ -type d -not -path '*/\\.*' | while read dir; do
  if [ -d "$dir" ] && [ "$(ls -A "$dir")" ]; then
    [ ! -f "$dir/AGENTS.md" ] && echo "Missing AGENTS.md: $dir"
    [ ! -f "$dir/README.md" ] && echo "Missing README.md: $dir"
  fi
done
```

### 6. Commit Changes with Clear Message

Use conventional commit format:

```bash
git add scripts/blender/AGENTS.md scripts/blender/README.md \
       scripts/blender/*.py

git commit -m "refactor: move [script-name] to appropriate directory

- Moved [script-name] from root to scripts/blender/
- Added AGENTS.md and README.md following project conventions
- Preserved git history through git move"
```

## Best Practices

### For AI Agents

1. **Preserve History**: Always use `git mv` instead of manual copy/delete to maintain file history
2. **Follow Existing Patterns**: Look at similar directories for structure and content guidance
3. **Document First**: Create or update documentation before or alongside moving files
4. **Validate Placement**: Ensure moved scripts still work in their new location
5. **Keep Atomic Changes**: Group related moves in a single commit when possible

### Directory Structure Guidelines

- Keep the repository root clean - only core Hermes files and essential configuration
- Group related functionality under `scripts/` with clear subdirectories
- Maintain parallel structure between `scripts/` and `~/.hermes/scripts/` for user-specific scripts
- Ensure every functional directory has both AGENTS.md

## Troubleshooting

### Scripts Not Working After Move

If a script fails after being moved:
1. Check for hardcoded paths that reference the old location
2. Verify relative paths in the script still resolve correctly
3. Ensure any required dependencies are still accessible
4. Update any import paths if the script imports from other moved files

### Missing Documentation Templates

If unsure what to include in AGENTS.md or README.md:
1. Look at existing examples in similar directories (e.g., `scripts/blender/` after this operation)
2. Check the repository root for examples of good documentation
3. Refer to the CONTRIBUTING.md for documentation standards

## References

- `scripts/blender/AGENTS.md` - Example of good agent documentation
- `scripts/blender/README.md` - Example of good user documentation
- `fork/extensions/AGENTS.md` - Example for fork-specific extensions
- `CONTRIBUTING.md` - General contribution guidelines

## Example Workflow

Here's how to reorganize a misplaced Blender rendering script:

```bash
# 1. Identify the misplaced script
ls *_render*.py  # Suppose this shows render_no_outputfile.py

# 2. Determine correct destination
# (Based on Blender usage in the script)
echo "Move to: scripts/blender/"

# 3. Move the file preserving history
git mv render_no_outputfile.py scripts/blender/render_no_outputfile.py

# 4. Check if directory needs documentation
ls scripts/blender/AGENTS.md 2>/dev/null || echo "Need to create AGENTS.md"
ls scripts/blender/README.md 2>/dev/null || echo "Need to create README.md"

# 5. Create missing documentation
# (Content would be added based on the script's purpose)

# 6. Verify everything works
python scripts/blender/render_no_outputfile.py --help  # or similar validation

# 7. Commit changes
git add scripts/blender/
git commit -m "refactor: move render_no_outputfile.py to scripts/blender/
- Moved render_no_outputfile.py from root to scripts/blender/
- Added AGENTS.md and README.md following project conventions
- Preserved git history through git move"
```

### 7. Verifying Repository State After Changes

After making changes (e.g., updating .gitignore, moving scripts), verify the repository state before creating a pull request.

Steps:

```bash
# Ensure you are on the correct branch
git status

# Check for untracked files that should be ignored
git status --untracked-files=no

# Verify that the changes you made are correctly staged
git diff --cached

# If ready, commit with a clear message
git commit -m "your commit message"

# Push to remote
git push origin <branch-name>

# Verify that the push is up-to-date
git status

# Create a pull request via GitHub interface or using gh CLI
# Example using gh CLI:
gh pr create --title "Your PR title" --body "Your PR description"
```

## Related Skills

After making changes (e.g., updating .gitignore, moving scripts), verify the repository state before creating a pull request.

Steps:

```bash
# Ensure you are on the correct branch
git status

# Check for untracked files that should be ignored
git status --untracked-files=no

# Verify that the changes you made are correctly staged
git diff --cached

# If ready, commit with a clear message
git commit -m "your commit message"

# Push to remote
git push origin <branch-name>

# Verify that the push is up-to-date
git status

# Create a pull request via GitHub interface or using gh CLI
# Example using gh CLI:
gh pr create --title "Your PR title" --body "Your PR description"
```

## Related Skills

- `hermes-agent`: For understanding Hermes core structure and extension patterns
- `blender-mcp`: For specific Blender integration patterns
- `cronjob-management`: For managing automated scripts that might be relocated

---
*This skill captures the pattern of organizing Hermes repository assets according to established project conventions.*