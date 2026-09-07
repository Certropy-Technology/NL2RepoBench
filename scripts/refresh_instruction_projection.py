#!/usr/bin/env python3
"""Refresh instruction.md projections after source instruction migrations.

For every task whose ``catalog/sources/<id>/instruction.md`` differs from the
compiled runtime ``catalog/tasks/<id>/instruction.md``, this tool re-derives the
canonical manifest digest with the same ``CatalogCompiler`` the CLI uses and
rewrites exactly the projection bytes a full Harbor recompile would refresh for
an instruction-only change:

- ``catalog/tasks/<id>/instruction.md`` (byte copy of the source instruction),
- the ``instruction.md`` entry inside ``bundle.manifest.json``,
- ``canonical_manifest_digest`` in both ``bundle.manifest.json`` and
  ``task.toml``.

The tool refuses to touch a task when the existing projection is inconsistent
(recorded instruction digest does not match the on-disk projection bytes) or
when the canonical compile fails, so partially-authored or blocked tasks are
left untouched and reported instead.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nl2repobench.authoring.catalog import CatalogCompiler, CatalogError  # noqa: E402
from nl2repobench.storage.artifacts import FileArtifactStore  # noqa: E402
from nl2repobench.storage.state import StateStore  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stale_tasks(root: Path) -> list[str]:
    tasks = []
    for task_toml in sorted((root / "catalog/tasks").glob("*/task.toml")):
        task_id = task_toml.parent.name
        source = root / "catalog/sources" / task_id / "instruction.md"
        projected = task_toml.parent / "instruction.md"
        if source.is_file() and projected.is_file():
            if source.read_bytes() != projected.read_bytes():
                tasks.append(task_id)
    return tasks


def refresh_task(root: Path, task_id: str, compiler: CatalogCompiler, out_root: Path) -> str:
    source_dir = root / "catalog/sources" / task_id
    task_root = root / "catalog/tasks" / task_id
    manifest_path = task_root / "bundle.manifest.json"
    task_toml_path = task_root / "task.toml"
    projected_instruction = task_root / "instruction.md"

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = [item for item in payload["files"] if item["path"] == "instruction.md"]
    if len(entries) != 1:
        raise RuntimeError("bundle manifest must list instruction.md exactly once")
    entry = entries[0]

    current = projected_instruction.read_bytes()
    if sha256_bytes(current) != entry["sha256"] or len(current) != entry["size_bytes"]:
        raise RuntimeError("existing projection is inconsistent with bundle manifest")

    old_digest = payload.get("canonical_manifest_digest")
    if not isinstance(old_digest, str) or not old_digest.startswith("sha256:"):
        raise RuntimeError("bundle manifest lacks canonical_manifest_digest")
    task_toml_text = task_toml_path.read_text(encoding="utf-8")
    if task_toml_text.count(old_digest) != 1:
        raise RuntimeError("task.toml must reference the previous canonical digest once")

    compiled = compiler.compile_task(source_dir, out_root)
    new_digest = compiled.manifest.content_digest()
    if compiled.reference.manifest_digest != new_digest:
        raise RuntimeError(
            "canonical digest mismatch between manifest and artifact reference"
        )
    if not new_digest.startswith("sha256:"):
        raise RuntimeError(f"unexpected canonical digest: {new_digest}")

    new_instruction = (source_dir / "instruction.md").read_bytes()
    entry["sha256"] = sha256_bytes(new_instruction)
    entry["size_bytes"] = len(new_instruction)
    payload["canonical_manifest_digest"] = new_digest

    projected_instruction.write_bytes(new_instruction)
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    task_toml_path.write_text(
        task_toml_text.replace(old_digest, new_digest), encoding="utf-8"
    )
    return new_digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--task", action="append", help="Limit to specific task ids.")
    args = parser.parse_args()
    root = args.root.resolve()

    targets = args.task or stale_tasks(root)
    refreshed: list[str] = []
    failed: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="instruction-refresh-") as scratch:
        scratch_path = Path(scratch)
        with StateStore(scratch_path / "state.db") as state:
            compiler = CatalogCompiler(
                FileArtifactStore(root / ".nl2repo/artifacts"), state_store=state
            )
            for task_id in targets:
                try:
                    refresh_task(root, task_id, compiler, scratch_path / "canonical")
                except (CatalogError, RuntimeError, OSError, ValueError, KeyError) as exc:
                    failed[task_id] = str(exc)
                else:
                    refreshed.append(task_id)
    print(json.dumps({"refreshed": len(refreshed), "failed": failed}, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
