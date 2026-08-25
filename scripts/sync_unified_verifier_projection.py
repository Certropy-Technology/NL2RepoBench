"""Regenerate verifier-only parts of the flat Harbor projection.

Catalog source TOML remains authoritative. This integrator updates generated
Node grader copies and the current metric ID, then refreshes each affected
bundle manifest from the generated tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path


def _refresh_manifest(task: Path) -> None:
    manifest_path = task / "bundle.manifest.json"
    if not manifest_path.is_file():
        return
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = []
    for path in sorted(p for p in task.rglob("*") if p.is_file() and p != manifest_path):
        data = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(task).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )
    payload["files"] = files
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def sync(root: Path) -> list[str]:
    canonical_grader = root / "src/nl2repobench/verification/node/grade-report.mjs"
    changed: list[str] = []
    for task in sorted(path for path in (root / "catalog/tasks").iterdir() if path.is_dir()):
        task_toml = task / "task.toml"
        if not task_toml.is_file():
            continue
        data = tomllib.loads(task_toml.read_text(encoding="utf-8"))
        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict) or metadata.get("language") != "node":
            continue
        text = task_toml.read_text(encoding="utf-8")
        updated = text.replace(
            'metric_contract = "node-test-leaf-pass-rate-v1"',
            'metric_contract = "fixed-test-pass-rate-v1"',
        )
        grader = task / "tests/runtime/node/grade-report.mjs"
        if grader.is_file() and canonical_grader.is_file():
            grader.write_bytes(canonical_grader.read_bytes())
            updated_task = True
        else:
            updated_task = False
        if updated != text:
            task_toml.write_text(updated, encoding="utf-8")
            updated_task = True
        if updated_task:
            _refresh_manifest(task)
            changed.append(task.name)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    changed = sync(args.root.resolve())
    print(json.dumps({"changed_tasks": changed, "count": len(changed)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
