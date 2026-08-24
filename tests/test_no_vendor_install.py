from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
TASKS = ROOT / "catalog/tasks"
FORBIDDEN_DOCKER_SNIPPETS = ("COPY dependencies", "--no-index", "--find-links")


def _is_node_task(task: Path) -> bool:
    data = tomllib.loads((task / "task.toml").read_text(encoding="utf-8"))
    return (data.get("metadata") or {}).get("language") == "node"


def test_python_harbor_tasks_do_not_vendor_dependencies() -> None:
    violations: list[str] = []

    for task in sorted(path for path in TASKS.iterdir() if path.is_dir()):
        if _is_node_task(task):
            continue

        if (task / "tests/dependencies").exists():
            violations.append(f"{task.name}: tests/dependencies")
        for path in task.rglob("*"):
            if path.is_dir() and path.name == "wheelhouse":
                violations.append(f"{task.name}: {path.relative_to(task)}")
            elif path.is_file() and path.suffix == ".whl":
                violations.append(f"{task.name}: {path.relative_to(task)}")
        for dockerfile in task.rglob("Dockerfile"):
            text = dockerfile.read_text(encoding="utf-8", errors="ignore")
            for snippet in FORBIDDEN_DOCKER_SNIPPETS:
                if snippet in text:
                    violations.append(
                        f"{task.name}: {dockerfile.relative_to(task)} contains {snippet!r}"
                    )

    assert violations == []
