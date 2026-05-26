#!/usr/bin/env python3
"""Git4D runtime checker and graph exporter.

The script is dependency-free on purpose. It validates local Git/DevOps
capabilities, detects GPU/CPU runtime hints, and exports a compact Git4D graph
that KAMUI4D-style viewers, Hermes, or Codex can consume.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 20) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except FileNotFoundError as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc), "elapsed_ms": 0}
    except OSError as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": f"timed out after {timeout}s",
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        }


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def tool_version(tool: str) -> list[str]:
    if tool in {"git", "uv", "node", "npm", "python", "nvidia-smi", "nvcc"}:
        return [tool, "--version"]
    if tool in {"gh", "codex", "hermes"}:
        return [tool, "--version"]
    return [tool, "--version"]


def detect_tools() -> dict[str, Any]:
    tools: dict[str, Any] = {}
    for name in ["git", "gh", "codex", "hermes", "uv", "python", "node", "npm", "nvidia-smi", "nvcc"]:
        path = shutil.which(name)
        info: dict[str, Any] = {"available": bool(path), "path": path}
        if path:
            version = run(tool_version(name), timeout=10)
            info["version"] = first_line(version["stdout"] or version["stderr"])
            info["version_ok"] = version["ok"]
        tools[name] = info
    info = tools.setdefault("python_current", {})
    info.update({"available": True, "path": sys.executable, "version": sys.version.split()[0]})
    return tools


def detect_cpu_features() -> dict[str, Any]:
    result: dict[str, Any] = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "features": {},
    }

    if sys.platform.startswith("win"):
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            checks = {
                "mmx": 3,
                "sse": 6,
                "sse2": 10,
                "sse3": 13,
                "xsave": 17,
                "rdrand": 28,
                "rdtscp": 32,
            }
            result["features"] = {
                name: bool(kernel32.IsProcessorFeaturePresent(code)) for name, code in checks.items()
            }
        except Exception as exc:  # pragma: no cover - host dependent
            result["warning"] = f"Windows CPU feature detection failed: {exc}"
    elif Path("/proc/cpuinfo").exists():
        text = Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").lower()
        flags = set()
        for line in text.splitlines():
            if line.startswith(("flags", "features")) and ":" in line:
                flags.update(line.split(":", 1)[1].split())
        result["features"] = {
            "sse": "sse" in flags,
            "sse2": "sse2" in flags,
            "sse3": "sse3" in flags or "pni" in flags,
            "sse4_1": "sse4_1" in flags,
            "sse4_2": "sse4_2" in flags,
            "avx": "avx" in flags,
            "avx2": "avx2" in flags,
            "avx512f": "avx512f" in flags,
            "neon": "neon" in flags or "asimd" in flags,
        }
    elif sys.platform == "darwin":
        sysctl = run(["sysctl", "-a"], timeout=10)
        text = (sysctl["stdout"] + "\n" + sysctl["stderr"]).lower()
        result["features"] = {
            "sse4_2": "sse4.2" in text,
            "avx": " avx" in text or ".avx" in text,
            "avx2": "avx2" in text,
            "neon": "neon" in text,
        }
    return result


def detect_gpu() -> dict[str, Any]:
    gpu: dict[str, Any] = {"nvidia_smi": shutil.which("nvidia-smi"), "nvcc": shutil.which("nvcc"), "gpus": []}

    if gpu["nvidia_smi"]:
        query = [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version,cuda_version",
            "--format=csv,noheader,nounits",
        ]
        smi = run(query, timeout=15)
        gpu["nvidia_smi_ok"] = smi["ok"]
        if smi["ok"]:
            for row in csv.reader(smi["stdout"].splitlines()):
                if len(row) >= 4:
                    gpu["gpus"].append(
                        {
                            "name": row[0].strip(),
                            "memory_total_mb": row[1].strip(),
                            "driver_version": row[2].strip(),
                            "cuda_version": row[3].strip(),
                        }
                    )
        else:
            gpu["nvidia_smi_error"] = smi["stderr"] or smi["stdout"]

    if gpu["nvcc"]:
        nvcc = run(["nvcc", "--version"], timeout=15)
        gpu["nvcc_ok"] = nvcc["ok"]
        gpu["nvcc_version"] = first_line(nvcc["stdout"] or nvcc["stderr"])
        match = re.search(r"release\s+([0-9.]+)", nvcc["stdout"] + "\n" + nvcc["stderr"])
        if match:
            gpu["cuda_toolkit_version"] = match.group(1)
    return gpu


def git_cmd(repo: Path, args: list[str], timeout: int = 20) -> dict[str, Any]:
    return run(["git", *args], cwd=repo, timeout=timeout)


def parse_worktrees(text: str) -> list[dict[str, Any]]:
    worktrees: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current.setdefault(key, value)
    if current:
        worktrees.append(current)
    return worktrees


def detect_git_repo(repo: Path) -> dict[str, Any]:
    info: dict[str, Any] = {"input_path": str(repo)}
    if not shutil.which("git"):
        info.update({"is_repo": False, "error": "git is not available on PATH"})
        return info

    root_result = git_cmd(repo, ["rev-parse", "--show-toplevel"])
    if not root_result["ok"]:
        info.update({"is_repo": False, "error": root_result["stderr"] or root_result["stdout"]})
        return info

    root = Path(root_result["stdout"]).resolve()
    info.update({"is_repo": True, "root": str(root)})
    info["branch"] = git_cmd(root, ["branch", "--show-current"])["stdout"]
    info["head"] = git_cmd(root, ["rev-parse", "HEAD"])["stdout"]
    info["head_short"] = git_cmd(root, ["rev-parse", "--short", "HEAD"])["stdout"]

    status = git_cmd(root, ["status", "--porcelain=v1"])
    status_lines = [line for line in status["stdout"].splitlines() if line.strip()]
    info["dirty_files"] = len(status_lines)
    info["status_sample"] = status_lines[:25]

    remotes = git_cmd(root, ["remote", "-v"])
    info["remotes"] = sorted(set(line.strip() for line in remotes["stdout"].splitlines() if line.strip()))

    worktrees = git_cmd(root, ["worktree", "list", "--porcelain"])
    if worktrees["ok"]:
        info["worktrees"] = parse_worktrees(worktrees["stdout"])

    git_dir_result = git_cmd(root, ["rev-parse", "--git-dir"])
    if git_dir_result["ok"]:
        git_dir = Path(git_dir_result["stdout"])
        if not git_dir.is_absolute():
            git_dir = root / git_dir
        hooks_dir = git_dir / "hooks"
        if hooks_dir.exists():
            info["hooks"] = sorted(p.name for p in hooks_dir.iterdir() if p.is_file() and not p.name.endswith(".sample"))

    return info


def benchmark_git(root: str | None) -> dict[str, Any]:
    if not root:
        return {}
    repo = Path(root)
    checks = {
        "status_porcelain": ["status", "--porcelain=v1"],
        "log_100": ["log", "--all", "--max-count=100", "--format=%H"],
    }
    return {name: git_cmd(repo, args, timeout=30)["elapsed_ms"] for name, args in checks.items()}


def parse_git_log_for_graph(root: Path, max_commits: int, max_files_per_commit: int) -> dict[str, Any]:
    fmt = "%x1e%H%x1f%P%x1f%an%x1f%ad%x1f%s"
    res = git_cmd(
        root,
        ["log", "--all", f"--max-count={max_commits}", "--date=iso-strict", f"--pretty=format:{fmt}", "--name-only"],
        timeout=60,
    )
    if not res["ok"]:
        return {"ok": False, "error": res["stderr"] or res["stdout"], "nodes": [], "edges": []}

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    file_node_ids: set[str] = set()
    commit_ids: set[str] = set()
    chunks = [chunk for chunk in res["stdout"].split("\x1e") if chunk.strip()]

    for index, chunk in enumerate(chunks):
        lines = [line.rstrip() for line in chunk.splitlines()]
        if not lines:
            continue
        header = lines[0].split("\x1f")
        if len(header) < 5:
            continue
        sha, parents, author, authored_at, subject = header[:5]
        files = [line.strip() for line in lines[1:] if line.strip()]
        commit_ids.add(sha)
        nodes.append(
            {
                "id": f"commit:{sha}",
                "kind": "commit",
                "label": f"{sha[:7]} {subject}",
                "sha": sha,
                "author": author,
                "time": authored_at,
                "coords": {
                    "x": index,
                    "y": len([p for p in parents.split() if p]),
                    "z": min(len(files), 100),
                    "t": authored_at,
                },
                "metrics": {"changed_files": len(files)},
            }
        )
        for parent in [p for p in parents.split() if p]:
            edges.append({"source": f"commit:{parent}", "target": f"commit:{sha}", "kind": "parent"})
        for path in files[:max_files_per_commit]:
            node_id = f"file:{path}"
            if node_id not in file_node_ids:
                file_node_ids.add(node_id)
                nodes.append({"id": node_id, "kind": "file", "label": path, "path": path})
            edges.append({"source": f"commit:{sha}", "target": node_id, "kind": "touches"})

    present_node_ids = {node["id"] for node in nodes}
    edges = [edge for edge in edges if edge["source"] in present_node_ids and edge["target"] in present_node_ids]
    return {
        "ok": True,
        "schema": "git4d.graph.v1",
        "generated_at": now_iso(),
        "repo": str(root),
        "limits": {"max_commits": max_commits, "max_files_per_commit": max_files_per_commit},
        "nodes": nodes,
        "edges": edges,
        "summary": {"commits": len(commit_ids), "files": len(file_node_ids), "edges": len(edges)},
    }


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    tools = report["tools"]
    repo = report["repo"]
    if not tools["git"]["available"]:
        issues.append({"severity": "error", "message": "Git is not available on PATH."})
    if not repo.get("is_repo"):
        issues.append({"severity": "warning", "message": "Target path is not a Git repository."})
    if repo.get("dirty_files", 0):
        issues.append({"severity": "warning", "message": f"Worktree has {repo['dirty_files']} changed files."})
    if repo.get("is_repo") and not repo.get("remotes"):
        issues.append({"severity": "info", "message": "No Git remotes configured."})
    if not tools["uv"]["available"]:
        issues.append({"severity": "info", "message": "uv is not on PATH; Python dependency control may be weaker."})
    if not tools["codex"]["available"]:
        issues.append({"severity": "info", "message": "codex CLI is not on PATH for this shell."})

    status = "pass"
    if any(item["severity"] == "error" for item in issues):
        status = "fail"
    elif any(item["severity"] == "warning" for item in issues):
        status = "warn"
    return {"status": status, "issues": issues}


def build_report(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any] | None]:
    repo_path = Path(args.repo).resolve()
    report: dict[str, Any] = {
        "schema": "git4d.runtime.v1",
        "generated_at": now_iso(),
        "host": {"os": platform.system(), "release": platform.release(), "node": platform.node()},
        "tools": detect_tools(),
        "cpu": detect_cpu_features(),
        "gpu": detect_gpu(),
        "repo": detect_git_repo(repo_path),
    }
    report["benchmarks_ms"] = benchmark_git(report["repo"].get("root"))
    report["summary"] = summarize(report)

    graph = None
    if args.graph_out and report["repo"].get("is_repo"):
        graph = parse_git_log_for_graph(
            Path(report["repo"]["root"]),
            max_commits=args.max_commits,
            max_files_per_commit=args.max_files_per_commit,
        )
    return report, graph


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def print_text(report: dict[str, Any], graph: dict[str, Any] | None, out: Path | None, graph_out: Path | None) -> None:
    summary = report["summary"]
    print(f"Git4D runtime: {summary['status']}")
    if out:
        print(f"runtime_report: {out}")
    if graph and graph_out:
        print(f"graph_export: {graph_out} ({graph.get('summary', {})})")
    for issue in summary["issues"]:
        print(f"- {issue['severity']}: {issue['message']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Git4D runtime capabilities and export Git4D graph JSON.")
    parser.add_argument("--repo", default=os.getcwd(), help="Repository or working directory to inspect.")
    parser.add_argument("--out", default="git4d-results/runtime-report.json", help="Runtime report JSON output path.")
    parser.add_argument("--graph-out", default="git4d-results/kamui4d-graph.json", help="Git4D graph JSON output path.")
    parser.add_argument("--max-commits", type=int, default=200, help="Maximum commits to include in graph export.")
    parser.add_argument("--max-files-per-commit", type=int, default=50, help="Maximum touched files per commit in graph.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Console output format.")
    parser.add_argument("--no-write", action="store_true", help="Do not write JSON files.")
    args = parser.parse_args()

    report, graph = build_report(args)
    out = Path(args.out).resolve() if args.out else None
    graph_out = Path(args.graph_out).resolve() if args.graph_out else None

    if not args.no_write:
        if out:
            write_json(out, report)
        if graph and graph_out:
            write_json(graph_out, graph)

    if args.format == "json":
        print(json.dumps({"report": report, "graph": graph}, indent=2, ensure_ascii=True))
    else:
        print_text(report, graph, out if not args.no_write else None, graph_out if not args.no_write else None)
    return 1 if report["summary"]["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
