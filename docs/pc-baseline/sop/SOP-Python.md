# SOP Python

## Standard Toolchain

- Environment and command runner: `uv`
- Tests: `pytest`
- Format: `black`
- Lint: `flake8`
- Type discipline: mandatory type hints
- Boundary validation: `pydantic` where schema enforcement matters

## UV-First Environment Policy

1. Use `uv` as the default Python environment manager, dependency resolver, and command runner for all Python work.
2. Before running Python commands, inspect project metadata in this order when present:
   - `pyproject.toml`
   - `uv.lock`
   - `.python-version`
   - `requires-python`
   - project README, task runner config, or local scripts that define the supported Python version
3. Select the Python version from project metadata. If the required interpreter is missing, install it with `uv python install <version>` unless the project explicitly forbids that path.
4. Run project commands through `uv` by default:
   - Dependency setup: `uv sync`
   - Python execution: `uv run python ...`
   - Tests: `uv run pytest ...`
   - Format and lint: `uv run black ...`, `uv run flake8 ...`
   - Type checks: `uv run mypy ...` or the project-defined checker
   - Nested projects: `uv run --project <path> ...`
5. For ad hoc Python tools that should not modify the project dependency graph, prefer `uvx <tool>` or `uv run --with <package> ...`.
6. For dependency changes in `pyproject.toml` projects, prefer `uv add`, `uv remove`, and `uv lock` instead of editing dependency state by hand.
7. Do not use bare `python`, `pip`, `pytest`, `black`, `flake8`, or `mypy` for project work unless an exception below applies.
8. Do not install packages into the global Python environment or create ad hoc virtual environments when a `uv` path is available.

## Allowed Exceptions

Use a non-`uv` Python path only when at least one condition is true:

1. The project explicitly requires Conda, Poetry, a checked-in virtual environment, or a custom wrapper that must be used for correctness.
2. `uv` is blocked by a documented local failure, such as a Windows file lock on the managed environment, and an existing project interpreter is the safest fallback.
3. The command is intentionally inspecting files or metadata without using the project runtime.
4. A third-party build, installer, or vendor script rejects `uv` and the fallback is required to complete the requested task.

When an exception is used, record the reason, the exact fallback command, and the remaining risk in the implementation log or final report.

## Rules

1. Keep imports ordered as standard library, third-party, then local modules.
2. Favor readable code and simple control flow over clever metaprogramming.
3. Add docstrings to public modules, classes, functions, and non-obvious behavior.
4. Use `logging`, not `print`.
5. Do not swallow exceptions.
6. Add `tqdm` when long-running scripts need visible progress.

## Completion Gate

- Fresh evidence shows the selected interpreter, usually `uv run python --version` or an equivalent project command
- Python commands were run through `uv`, or any fallback is documented under Allowed Exceptions
- `pytest` evidence exists when behavior changes
- `black` and `flake8` expectations are satisfied
- Type hints and boundary validation are present where needed
