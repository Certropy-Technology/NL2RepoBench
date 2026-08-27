from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
TASKS = ROOT / "catalog/tasks"
FORBIDDEN_DOCKER_SNIPPETS = ("COPY dependencies", "--no-index", "--find-links")


def _runtime_language(task: Path) -> str:
    task_toml = task / "task.toml"
    if not task_toml.is_file():
        return "unknown"
    data = tomllib.loads(task_toml.read_text(encoding="utf-8"))
    return str((data.get("metadata") or {}).get("language") or "python")


def test_python_harbor_tasks_do_not_vendor_dependencies() -> None:
    violations: list[str] = []

    for task in sorted(path for path in TASKS.iterdir() if path.is_dir()):
        if not (task / "task.toml").is_file():
            violations.append(f"{task.name}: task.toml missing")
            continue
        if _runtime_language(task) != "python":
            continue

        if (task / "tests/dependencies").exists():
            violations.append(f"{task.name}: tests/dependencies")
        for path in task.rglob("*"):
            if path.is_dir() and path.name == "wheelhouse":
                violations.append(f"{task.name}: {path.relative_to(task)}")
            elif path.is_file() and path.suffix == ".whl":
                violations.append(f"{task.name}: {path.relative_to(task)}")
        for install_surface in task.rglob("Dockerfile"):
            text = install_surface.read_text(encoding="utf-8", errors="ignore")
            for snippet in FORBIDDEN_DOCKER_SNIPPETS:
                if snippet in text:
                    violations.append(
                        f"{task.name}: {install_surface.relative_to(task)} "
                        f"contains {snippet!r}"
                    )

    assert violations == []
