---
name: hermes-skill-sourcing
description: Use when installing a third-party skill into Hermes.
version: 1.0.0
author: Hermes Agent
license: MIT
category: devops
metadata:
  hermes:
    tags: [hermes, skills, plugins, install, provenance, security-scan]
    category: devops
    related_skills: [hermes-agent, hermes-plugin-troubleshooting, hermes-runtime-operations]
---

# Hermes Skill Sourcing

Class-level workflow for adopting an external skill/plugin (agent-skills repo,
plugin marketplace, single SKILL.md) into Hermes with evidence. Covers sourcing,
install, security-scan interpretation, provenance verification, and activation.

Does NOT cover writing new skills or debugging a plugin that is already loaded
and failing at runtime (that's `hermes-plugin-troubleshooting`).

## When to Use

- "Install the X skill/plugin from `<github url>`"
- "Add this repo as a skill source" / tap questions
- Auditing an installed skill: is it still upstream-faithful?
- Interpreting a `hermes skills install` security verdict

## Prerequisites

- `hermes` on PATH (or the repo checkout: `python -m hermes_cli.main ...`).
- `git` for provenance checks.
- Network access to github.com for the clone-back verification.

## Procedure

### 1. Read upstream instructions BEFORE installing

Agent-skills repos almost always ship `AGENTS.md` + `INSTALL.md`. Find the
section for the **current harness** (Hermes / Claude Code / Codex / Cursor /
OpenCode / Pi / Qwen / Gemini / Zed) and use its exact command. Do not invent a
command when the repo documents one.

`AGENTS.md`'s repo map also names which file is canonical for the skill's
behavior — that is the file you hash later, not whatever the installer produced.

### 2. Preview, then install

```bash
hermes skills inspect ayghri/i-have-adhd/skills/i-have-adhd   # preview
hermes skills install ayghri/i-have-adhd/skills/i-have-adhd --yes
```

- `--yes` is **required** in non-interactive / TUI contexts; without it the
  command blocks on a confirmation prompt.
- Lands in `~/.hermes/skills/<name>/`. Resolve via `get_hermes_home()` if you
  script the path; the default profile is `~/.hermes`.
- `hermes skills install <direct SKILL.md https URL>` also works.
- A bare `owner/repo` is a **tap**, not a skill. If it does not resolve:
  `hermes skills tap add owner/repo` → `hermes skills search <query>` →
  install the full `owner/repo/<path/to/skill-dir>`.

### 3. Report the security scan honestly

The installer runs quarantine → scan → verdict automatically. Surface to the
user: **verdict**, **scanner id**, **scan hash**, **upstream commit SHA**.

- Community source + SAFE verdict → auto-ALLOWED. Fine.
- A MEDIUM/LOW finding on *prose inside SKILL.md* (e.g. an unpinned
  `npm install foo` appearing as a "good example") is not executable code.
  Name it once as a non-blocking flag; do not treat it as a failure and do not
  pass `--force` to silence it.

### 4. Verify provenance — three independent reads

Exit code 0 proves nothing about fidelity. All three:

```bash
hermes skills list                       # row present and 'enabled'
# file exists at ~/.hermes/skills/<name>/SKILL.md
git clone --depth 1 <repo> <scratch>
# sha256 of installed SKILL.md == sha256 of upstream canonical SKILL.md
```

**Only the hash equality proves the install was not rewritten, truncated, or
frontmatter-mangled.** Byte-equality against the canonical path from step 1 is
the check to report.

### 5. State what was NOT installed

Multi-runtime repos ship hooks, plugin manifests, marketplace metadata, and
extension files that the Hermes skill route ignores. Say explicitly which parts
came in as `SKILL.md` only, so the user does not expect a slash command or an
always-on hook that does not exist in this harness.

### 6. Activation

Prompt caching means a freshly installed skill is **not invocable in the session
that installed it**. `/reset` does not reliably fix this either. Tell the user to
open a **new session** and invoke it there.

**Prefer Hermes-native always-on over the repo's prose snippet.** Upstream
multi-runtime repos document an always-on block to paste into `AGENTS.md` /
`SOUL.md` / `~/.gemini/GEMINI.md` per runtime. Hermes needs none of that — it
injects a skill straight into the system prompt via config:

```bash
hermes config set skills.auto_load '["<skill-name>"]'
```

Quote the value. The CLI's structured-value parser (`hermes_cli/config.py`,
`_looks_structured_value` branch) only tries YAML when the string starts with a
list/mapping marker, so a bare `skill-name` stores a **string** and every
`isinstance(..., list)` reader silently ignores it — the setting looks saved
and does nothing.

Then verify the injection for real (see `scripts/verify_auto_load.py`):

1. `resolve_auto_load_skills()` returns your identifier.
2. `build_auto_load_prompt()` returns it in `loaded`, empty `missing`, and a
   non-zero prompt length containing the activation note
   `auto-loaded via config (skills.auto_load)`.
3. `agent/system_prompt.py::_auto_load_parts` includes it in the prompt body.
4. `HERMES_IGNORE_RULES=1` suppresses it — the documented escape hatch.

Run the regression suite for the mechanism:
`tests/agent/test_skills_auto_load_native.py`,
`tests/agent/test_skills_auto_load_boundaries_native.py`,
`tests/agent/test_skills_auto_load_new_session_native.py` (50 tests, ~4 min).

If the user's need is per-project rather than global, prefer the workdir
`AGENTS.md` over `skills.auto_load`, which applies to every session.

### 7. Clean up the probe clone

Delete the shallow clone used for hashing. Use `cmd /c rmdir /s /q <dir>` on
Windows rather than a POSIX `rm -rf` from the bash tool.

## Pitfalls

1. **Inventing an install command instead of reading `INSTALL.md`.** Upstream
   manifests route differently per runtime; the wrong one silently installs a
   subset (skill without hooks, or nothing).
2. **Trusting exit code 0 as verification.** The scan/install pipeline can
   succeed while the delivered file differs from upstream.
3. **Forgetting `--yes` in TUI mode.** Blocks on a prompt nothing will answer.
4. **Passing `owner/repo` expecting a skill install.** That is the tap form.
5. **Claiming the plugin's entry points were installed** when only `SKILL.md`
   landed. Misleads the user into hunting a missing slash command.
6. **Telling the user to `/reset`.** Newly installed skills need a new session;
   `/reset` alone is not the documented path.
7. **Treating a prose-scanner MEDIUM as a blocker.** It creates false alarm;
   report it and move on.
8. **`--force` reflexively.** Bypasses a verdict that was worth reading.
9. **Hand-copying an always-on snippet when Hermes has `skills.auto_load`.** The
   upstream per-runtime snippet is for harnesses without a native mechanism.
   Pasting it into `SOUL.md` works but is unmaintainable and leaves the skill
   invisible to `hermes skills list`.
10. **`hermes config set skills.auto_load skill-name` without JSON quotes.**
    Stores a string; every list-gated reader drops it. Looks saved, does nothing.
11. **Trusting `hermes config set`'s "not a recognized config key" warning.**
    That notice comes from the DEFAULT_CONFIG known-key list, which does not
    enumerate `skills.auto_load`. The real reader is
    `agent/skill_commands.py::resolve_auto_load_skills`, and the key works.
    Verify by reading it back through the module instead of re-writing with
    `--force` — a warning here is not a failure signal.
12. **Probing config with the wrong interpreter.** `load_config_readonly`
    imports `yaml`; the bare `python` on PATH may lack it while the repo venv
    (`.venv/Scripts/python.exe`) has it. An empty `resolve_auto_load_skills()`
    result from the wrong interpreter is a false negative that looks exactly
    like a broken setting. Re-probe with the venv interpreter before concluding.

## Verification

Before declaring done, confirm you can show all of:

- [ ] Upstream `AGENTS.md`/`INSTALL.md` read and the harness-matched command used
- [ ] Security verdict + scanner + hash + upstream SHA reported
- [ ] `hermes skills list` shows the skill enabled
- [ ] Installed file exists AND its sha256 equals the upstream canonical file
- [ ] Explicit statement of what the Hermes route did NOT install
- [ ] User told to invoke it in a **new** session
- [ ] If always-on was requested: `skills.auto_load` written as a JSON list AND
      read back through `build_auto_load_prompt()` (non-zero length, entry in
      `loaded`, empty `missing`) using the repo venv interpreter

## References

- `references/verified-installations.md` — per-repo install receipts (command,
  verdict, hash, activation notes) for sources verified on this workstation.
