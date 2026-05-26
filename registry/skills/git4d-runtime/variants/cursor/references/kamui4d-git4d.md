# KAMUI4D to Git4D implementation note

KAMUI4D public material describes a graph-based spatial development tool for
project structure, Git history, and AI task visibility. Release material also
shows KAMUI CODE and MCP-oriented updates.

Local Git4D therefore implements the durable, offline part first:

- runtime diagnostics for Git, Codex, Hermes, uv, Python, Node, CUDA, NVIDIA GPU,
  and CPU feature hints
- Git history export as `git4d.graph.v1` JSON with commit, file, parent, and
  touches edges
- portable reports under `git4d-results/` for KAMUI4D, Hermes, Codex, or Cursor
  consumers

Primary references checked on 2026-05-26:

- https://4d.kamui.ai/
- https://www.kamui.ai/ja
- https://github.com/dai-motoki/kamui4d-editor-releases/releases
- https://news.toremaga.com/release/others/3808256.html

Latest release observed during research: `KAMUI OS - AMATERAS - v1.8.45`
on 2026-05-26, including a Windows setup asset and Mac assets.
