#!/usr/bin/env python3
"""Git4D schema/configuration auditor.

Validates .git4d configuration files without external dependencies. JSON is the
canonical structured format; YAML is parsed with PyYAML when available and is
otherwise checked conservatively with a clear warning.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STAGE_TYPES = {"shell", "docker", "node", "python", "approval", "codex", "hermes", "kamui4d"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_issue(issues: list[dict[str, Any]], severity: str, path: Path | None, message: str, hint: str | None = None) -> None:
    payload: dict[str, Any] = {"severity": severity, "message": message}
    if path:
        payload["path"] = str(path)
    if hint:
        payload["hint"] = hint
    issues.append(payload)


def load_json(path: Path) -> tuple[Any | None, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    try:
        return json.loads(path.read_text(encoding="utf-8")), issues
    except json.JSONDecodeError as exc:
        add_issue(issues, "error", path, f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    except OSError as exc:
        add_issue(issues, "error", path, f"Cannot read file: {exc}")
    return None, issues


def load_yaml(path: Path) -> tuple[Any | None, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    try:
        import yaml  # type: ignore

        return yaml.safe_load(path.read_text(encoding="utf-8")), issues
    except ModuleNotFoundError:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "\t" in text:
            add_issue(issues, "warning", path, "YAML contains tab characters.", "Prefer spaces for indentation.")
        if not re.search(r"^\s*[A-Za-z0-9_-]+\s*:", text, flags=re.MULTILINE):
            add_issue(issues, "warning", path, "YAML parser unavailable and no top-level keys were detected.")
        else:
            add_issue(
                issues,
                "info",
                path,
                "PyYAML is not installed, so this YAML file received syntax-only checks.",
                "Use JSON for strict Git4D validation or install PyYAML.",
            )
    except Exception as exc:
        add_issue(issues, "error", path, f"Invalid YAML: {exc}")
    return None, issues


def load_document(path: Path) -> tuple[Any | None, list[dict[str, Any]]]:
    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonc"} or path.name == ".git4drc":
        return load_json(path)
    if suffix in {".yaml", ".yml"}:
        return load_yaml(path)
    return None, [{"severity": "info", "path": str(path), "message": "Skipped unsupported Git4D file type."}]


def discover_config_files(repo: Path) -> list[Path]:
    candidates: list[Path] = []
    direct = [repo / ".git4drc"]
    for path in direct:
        if path.exists():
            candidates.append(path)
    git4d_dir = repo / ".git4d"
    if git4d_dir.exists():
        for pattern in ["*.json", "*.jsonc", "*.yaml", "*.yml", "configs/*.json", "configs/*.yaml", "configs/*.yml", "schema/**/*.json"]:
            candidates.extend(sorted(git4d_dir.glob(pattern)))
    return sorted(set(p.resolve() for p in candidates if p.is_file()))


def require_object(doc: Any, path: Path, issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not isinstance(doc, dict):
        add_issue(issues, "error", path, "Git4D config must be a JSON/YAML object.")
        return None
    return doc


def validate_version(doc: dict[str, Any], path: Path, issues: list[dict[str, Any]]) -> None:
    version = doc.get("version")
    if version is None:
        add_issue(issues, "warning", path, "Missing version field.", "Add a semantic Git4D config version such as 1.0.0.")
        return
    if not isinstance(version, str) or not re.match(r"^\d+\.\d+(\.\d+)?", version):
        add_issue(issues, "warning", path, "Version should be a string like 1.0.0.")


def validate_pipeline(doc: dict[str, Any], path: Path, issues: list[dict[str, Any]]) -> None:
    pipeline = doc.get("pipeline")
    if pipeline is None:
        return
    if not isinstance(pipeline, dict):
        add_issue(issues, "error", path, "pipeline must be an object.")
        return
    stages = pipeline.get("stages")
    if not isinstance(stages, list) or not stages:
        add_issue(issues, "error", path, "pipeline.stages must be a non-empty list.")
        return
    seen: set[str] = set()
    for idx, stage in enumerate(stages):
        label = f"pipeline.stages[{idx}]"
        if not isinstance(stage, dict):
            add_issue(issues, "error", path, f"{label} must be an object.")
            continue
        name = stage.get("name")
        stage_type = stage.get("type")
        if not isinstance(name, str) or not name.strip():
            add_issue(issues, "error", path, f"{label}.name is required.")
        elif name in seen:
            add_issue(issues, "error", path, f"Duplicate stage name: {name}.")
        else:
            seen.add(name)
        if stage_type not in VALID_STAGE_TYPES:
            add_issue(issues, "error", path, f"{label}.type must be one of {sorted(VALID_STAGE_TYPES)}.")
        if stage_type in {"shell", "python", "node"} and not (stage.get("script") or stage.get("command")):
            add_issue(issues, "warning", path, f"{label} should define script or command.")
        if stage_type == "docker" and not stage.get("image"):
            add_issue(issues, "warning", path, f"{label} docker stage should define image.")


def validate_runtime(doc: dict[str, Any], path: Path, issues: list[dict[str, Any]]) -> None:
    runtime = doc.get("runtime")
    if runtime is None:
        return
    if not isinstance(runtime, dict):
        add_issue(issues, "error", path, "runtime must be an object.")
        return
    gpu = runtime.get("gpu")
    if gpu is not None:
        if not isinstance(gpu, dict):
            add_issue(issues, "error", path, "runtime.gpu must be an object.")
        else:
            if "required" in gpu and not isinstance(gpu["required"], bool):
                add_issue(issues, "error", path, "runtime.gpu.required must be boolean.")
            if "min_memory" in gpu and not isinstance(gpu["min_memory"], (str, int, float)):
                add_issue(issues, "warning", path, "runtime.gpu.min_memory should be a number or string such as 16GB.")
            if "cuda_version" in gpu and not isinstance(gpu["cuda_version"], str):
                add_issue(issues, "warning", path, "runtime.gpu.cuda_version should be a string.")
    cpu = runtime.get("cpu")
    if cpu is not None:
        if not isinstance(cpu, dict):
            add_issue(issues, "error", path, "runtime.cpu must be an object.")
        elif "cores" in cpu and (not isinstance(cpu["cores"], int) or cpu["cores"] < 1):
            add_issue(issues, "error", path, "runtime.cpu.cores must be a positive integer.")


def validate_integrations(doc: dict[str, Any], path: Path, issues: list[dict[str, Any]]) -> None:
    integrations = doc.get("integrations")
    if integrations is None:
        add_issue(
            issues,
            "info",
            path,
            "No integrations section found.",
            "Add integrations.codex, integrations.hermes, and integrations.kamui4d when this repo is agent-controlled.",
        )
        return
    if not isinstance(integrations, dict):
        add_issue(issues, "error", path, "integrations must be an object.")
        return
    for name in ["codex", "hermes", "kamui4d"]:
        value = integrations.get(name)
        if value is None:
            add_issue(issues, "info", path, f"integrations.{name} is not declared.")
        elif not isinstance(value, (bool, dict)):
            add_issue(issues, "warning", path, f"integrations.{name} should be boolean or object.")
        elif isinstance(value, dict) and "enabled" in value and not isinstance(value["enabled"], bool):
            add_issue(issues, "error", path, f"integrations.{name}.enabled must be boolean.")


def validate_schema_file(doc: dict[str, Any], path: Path, issues: list[dict[str, Any]]) -> None:
    if "schema" in path.parts or path.name.endswith(".schema.json"):
        if "$schema" not in doc:
            add_issue(issues, "warning", path, "Schema file should declare $schema.")
        if "type" not in doc:
            add_issue(issues, "warning", path, "Schema file should declare top-level type.")


def validate_document(doc: Any, path: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    obj = require_object(doc, path, issues)
    if obj is None:
        return issues
    validate_version(obj, path, issues)
    validate_pipeline(obj, path, issues)
    validate_runtime(obj, path, issues)
    validate_integrations(obj, path, issues)
    validate_schema_file(obj, path, issues)
    if "exports" not in obj and not ("schema" in path.parts or path.name.endswith(".schema.json")):
        add_issue(issues, "info", path, "No exports section found.", "Add exports.git4d_graph for KAMUI4D/Hermes/Codex consumers.")
    return issues


def init_git4d(repo: Path) -> list[Path]:
    config_dir = repo / ".git4d" / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    files: dict[Path, dict[str, Any]] = {
        repo / ".git4drc": {
            "version": "1.0.0",
            "profiles": {"default": ".git4d/configs/pipeline.json"},
            "integrations": {"codex": {"enabled": True}, "hermes": {"enabled": True}, "kamui4d": {"enabled": True}},
            "exports": {"git4d_graph": "git4d-results/kamui4d-graph.json"},
        },
        config_dir / "pipeline.json": {
            "version": "1.0.0",
            "pipeline": {
                "stages": [
                    {"name": "runtime", "type": "python", "script": "python scripts/git4d_runtime_check.py"},
                    {"name": "schema", "type": "python", "script": "python scripts/git4d_schema_audit.py"},
                ]
            },
            "integrations": {"codex": True, "hermes": True, "kamui4d": True},
            "exports": {"git4d_graph": "git4d-results/kamui4d-graph.json"},
        },
        config_dir / "runtime.json": {
            "version": "1.0.0",
            "runtime": {"gpu": {"required": False}, "cpu": {"cores": 2, "features": ["sse2"]}},
            "integrations": {"codex": True, "hermes": True, "kamui4d": True},
        },
    }
    for path, payload in files.items():
        if not path.exists():
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            created.append(path)
    return created


def audit(repo: Path, do_init: bool) -> dict[str, Any]:
    created: list[Path] = []
    if do_init:
        created = init_git4d(repo)

    files = discover_config_files(repo)
    issues: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []

    if not files:
        add_issue(issues, "warning", None, "No .git4d configuration files found.", "Run with --init to create a baseline.")

    for path in files:
        doc, load_issues = load_document(path)
        issues.extend(load_issues)
        if doc is not None:
            issues.extend(validate_document(doc, path))
            documents.append({"path": str(path), "keys": sorted(doc.keys()) if isinstance(doc, dict) else []})

    status = "pass"
    if any(item["severity"] == "error" for item in issues):
        status = "fail"
    elif any(item["severity"] == "warning" for item in issues):
        status = "warn"

    return {
        "schema": "git4d.schema_audit.v1",
        "generated_at": now_iso(),
        "repo": str(repo),
        "created": [str(path) for path in created],
        "documents": documents,
        "summary": {"status": status, "files": len(files), "errors": count(issues, "error"), "warnings": count(issues, "warning"), "info": count(issues, "info")},
        "issues": issues,
    }


def count(issues: list[dict[str, Any]], severity: str) -> int:
    return sum(1 for issue in issues if issue.get("severity") == severity)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def print_text(report: dict[str, Any], out: Path | None) -> None:
    summary = report["summary"]
    print(f"Git4D schema audit: {summary['status']}")
    if out:
        print(f"schema_report: {out}")
    if report["created"]:
        print("created:")
        for path in report["created"]:
            print(f"- {path}")
    for issue in report["issues"]:
        path = f"{issue.get('path')}: " if issue.get("path") else ""
        print(f"- {issue['severity']}: {path}{issue['message']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Git4D .git4d configuration files.")
    parser.add_argument("--repo", default=os.getcwd(), help="Repository or working directory to inspect.")
    parser.add_argument("--out", default="git4d-results/schema-report.json", help="Schema report JSON output path.")
    parser.add_argument("--init", action="store_true", help="Create baseline .git4d config if it is missing.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Console output format.")
    parser.add_argument("--no-write", action="store_true", help="Do not write JSON report.")
    args = parser.parse_args()

    report = audit(Path(args.repo).resolve(), args.init)
    out = Path(args.out).resolve() if args.out else None
    if out and not args.no_write:
        write_json(out, report)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print_text(report, out if not args.no_write else None)
    return 1 if report["summary"]["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
