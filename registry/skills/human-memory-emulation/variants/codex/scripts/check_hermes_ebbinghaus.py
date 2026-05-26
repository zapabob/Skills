#!/usr/bin/env python3
"""Check a Hermes Ebbinghaus memory provider install.

This script avoids secrets and defaults to a temporary probe database.
Run it with the Hermes repo's Python environment when possible.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path


def _find_repo(start: Path) -> Path | None:
    candidates = [start, *start.parents, start / "hermes-agent"]
    for candidate in candidates:
        if (
            (candidate / "pyproject.toml").exists()
            and (candidate / "plugins" / "memory").is_dir()
        ):
            return candidate
    return None


def _read_provider_from_config(config_path: Path) -> str:
    if not config_path.exists():
        return ""
    in_memory = False
    for raw in config_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            in_memory = stripped == "memory:"
            continue
        if in_memory and stripped.startswith("provider:"):
            return stripped.split(":", 1)[1].strip().strip("'\"")
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Path to hermes-agent repo")
    parser.add_argument("--hermes-home", default=os.environ.get("HERMES_HOME"))
    parser.add_argument("--live", action="store_true", help="Probe live configured DB")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser() if args.repo else _find_repo(Path.cwd())
    if repo is None:
        print(json.dumps({"ok": False, "error": "hermes-agent repo not found"}))
        return 2
    repo = repo.resolve()
    sys.path.insert(0, str(repo))

    hermes_home = Path(args.hermes_home or Path.home() / ".hermes").expanduser()
    config_path = hermes_home / "config.yaml"
    result: dict = {
        "repo": str(repo),
        "hermes_home": str(hermes_home),
        "config_path": str(config_path),
        "configured_provider": _read_provider_from_config(config_path),
        "files": {
            "provider": (repo / "plugins" / "memory" / "ebbinghaus" / "__init__.py").exists(),
            "plugin_yaml": (repo / "plugins" / "memory" / "ebbinghaus" / "plugin.yaml").exists(),
            "tests": (repo / "tests" / "plugins" / "test_ebbinghaus_plugin.py").exists(),
        },
    }

    try:
        from plugins.memory import discover_memory_providers, load_memory_provider

        providers = discover_memory_providers()
        ebbinghaus = [item for item in providers if item[0] == "ebbinghaus"]
        result["discovered"] = ebbinghaus
        provider = load_memory_provider("ebbinghaus")
        result["loadable"] = provider is not None
        result["available"] = bool(provider and provider.is_available())
        if provider is None:
            print(json.dumps({"ok": False, **result}, ensure_ascii=False, indent=2))
            return 1

        if args.live:
            db_path = str(hermes_home / "ebbinghaus_memory.db")
        else:
            tmp_dir = tempfile.TemporaryDirectory()
            db_path = str(Path(tmp_dir.name) / "probe.db")

        provider._config = {  # type: ignore[attr-defined]
            "db_path": db_path,
            "max_prefetch": 3,
            "min_prefetch_score": 0.01,
        }
        provider.initialize("skill-probe", hermes_home=str(hermes_home), platform="cli")
        add = json.loads(provider.handle_tool_call(
            "ebbinghaus_memory",
            {
                "action": "remember",
                "content": "Skill probe memory for Ebbinghaus encoding and recall.",
                "tags": "skill,probe,ebbinghaus",
                "salience": 0.7,
            },
        ))
        recall = json.loads(provider.handle_tool_call(
            "ebbinghaus_memory",
            {"action": "recall", "query": "ebbinghaus probe recall", "limit": 1},
        ))
        stats = json.loads(provider.handle_tool_call("ebbinghaus_memory", {"action": "stats"}))
        provider.shutdown()

        result["probe"] = {
            "db_path": db_path,
            "remember_status": add.get("status"),
            "recall_count": len(recall.get("results", [])),
            "stats": stats,
        }
        result["ok"] = all(result["files"].values()) and result["available"] and result["probe"]["recall_count"] > 0
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 1
    except Exception as exc:
        result["ok"] = False
        result["error"] = str(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
