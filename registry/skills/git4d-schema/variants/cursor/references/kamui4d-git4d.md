# KAMUI4D to Git4D schema note

KAMUI4D-style graph tooling benefits from predictable config and export paths.
Git4D uses `.git4drc` plus `.git4d/configs/*.json` as the strict local baseline.
YAML can be audited when PyYAML is installed, but JSON is the canonical format so
the skill remains dependency-free on fresh Windows machines.

Recommended local contract:

- `.git4drc` declares `version`, `profiles`, `integrations`, and `exports`
- `.git4d/configs/pipeline.json` declares stages such as `runtime` and `schema`
- `.git4d/configs/runtime.json` declares CPU/GPU expectations
- `git4d-results/kamui4d-graph.json` stores the graph export for viewers

Primary references checked on 2026-05-26:

- https://4d.kamui.ai/
- https://www.kamui.ai/ja
- https://github.com/dai-motoki/kamui4d-editor-releases/releases
- https://news.toremaga.com/release/others/3808256.html

Latest release observed during research: `KAMUI OS - AMATERAS - v1.8.45`
on 2026-05-26, including a Windows setup asset and Mac assets.
