#!/usr/bin/env python3
"""Test-only Pi replacement for the Java authoring loop E2E."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    package = os.environ.get("JAVA_AUTHORING_PACKAGE", "java-ministats")
    source = root / "catalog/sources" / package
    fixture = Path(os.environ["JAVA_AUTHORING_TEMPLATE"])
    source.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(fixture, source)
    task_toml = source / "task.toml"
    task_id = task_toml.read_text(encoding="utf-8")
    task_id = task_id.replace('task_id = "java-ministats"', f'task_id = "{package}"')
    task_toml.write_text(
        task_id,
        encoding="utf-8",
    )
    private_artifacts = Path(os.environ["JAVA_AUTHORING_ARTIFACTS"])
    if private_artifacts.is_dir():
        shutil.copytree(private_artifacts, root / ".nl2repo/artifacts")
    handoff = root / ".nl2repo/authoring-handoff.json"
    handoff.parent.mkdir(parents=True, exist_ok=True)
    handoff.write_text(
        json.dumps(
            {
                "status": "authoring-complete",
                "language": "java",
                "package": package,
                "note": "test-only deterministic authoring agent",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    shutil.rmtree(root / ".pi", ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
