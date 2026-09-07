#!/usr/bin/env python3
"""Refresh Java instruction.md projections using the Java-aware catalog compiler.

main's ``CatalogCompiler`` only accepts the unified Python/Node schema, so the
34 Java sources (extended Maven/junit-platform schema) cannot be canonical-compiled
from main. Their projection digests are instead recomputed in the dedicated Java
Maven authoring worktree, whose ``src`` bundles the Java-aware source model, and
this script rewrites the three projection bytes in the integration checkout.

Run from the integration checkout root with ``PYTHONPATH`` pointing at the
Java worktree, so the extended schema compiler is imported while every path stays
under the integration checkout. Only tasks whose old projection digest matches the
recorded bundle manifest are touched; failures are reported, not overwritten.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path("/data/NL2RepoBench-integration-20260827")
# Do NOT insert ROOT/src: when this script is run from the Java Maven worktree
# with PYTHONPATH pointing at that worktree, its Java-aware source models must
# win over main's unified-schema models. The environment (from the launcher)
# is what places the worktree's src on sys.path first.

from nl2repobench.authoring.catalog import CatalogCompiler, CatalogError  # noqa: E402
from nl2repobench.storage.artifacts import FileArtifactStore  # noqa: E402
from nl2repobench.storage.state import StateStore  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


import hashlib  # noqa: E402


def main() -> int:
    java_ids = sorted(
        p.parent.name
        for p in (ROOT / "catalog/tasks").glob("*/task.toml")
        if p.parent.name.startswith("java-")
    )
    refreshed: list[str] = []
    failed: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="java-instruction-refresh-") as scratch:
        scratch_path = Path(scratch)
        with StateStore(scratch_path / "state.db") as state:
            compiler = CatalogCompiler(
                FileArtifactStore(ROOT / ".nl2repo/artifacts"), state_store=state
            )
            for task_id in java_ids:
                source_dir = ROOT / "catalog/sources" / task_id
                task_root = ROOT / "catalog/tasks" / task_id
                manifest_path = task_root / "bundle.manifest.json"
                task_toml_path = task_root / "task.toml"
                projected_instruction = task_root / "instruction.md"
                try:
                    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                    entries = [
                        item
                        for item in payload["files"]
                        if item["path"] == "instruction.md"
                    ]
                    if len(entries) != 1:
                        raise RuntimeError(
                            "bundle manifest must list instruction.md exactly once"
                        )
                    entry = entries[0]
                    current = projected_instruction.read_bytes()
                    if sha256_bytes(current) != entry["sha256"] or len(current) != entry[
                        "size_bytes"
                    ]:
                        raise RuntimeError(
                            "existing projection is inconsistent with bundle manifest"
                        )
                    old_digest = payload.get("canonical_manifest_digest")
                    if not isinstance(old_digest, str):
                        raise RuntimeError("missing canonical_manifest_digest")
                    task_toml_text = task_toml_path.read_text(encoding="utf-8")
                    if task_toml_text.count(old_digest) != 1:
                        raise RuntimeError(
                            "task.toml must reference the previous digest once"
                        )
                    compiled = compiler.compile_task(source_dir, scratch_path / "out")
                    new_digest = compiled.manifest.content_digest()
                    if compiled.reference.manifest_digest != new_digest:
                        raise RuntimeError("manifest digest and reference disagree")
                    new_instruction = (source_dir / "instruction.md").read_bytes()
                    entry["sha256"] = sha256_bytes(new_instruction)
                    entry["size_bytes"] = len(new_instruction)
                    payload["canonical_manifest_digest"] = new_digest
                    projected_instruction.write_bytes(new_instruction)
                    manifest_path.write_text(
                        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
                        + "\n",
                        encoding="utf-8",
                    )
                    task_toml_path.write_text(
                        task_toml_text.replace(old_digest, new_digest),
                        encoding="utf-8",
                    )
                except (CatalogError, RuntimeError, OSError, ValueError, KeyError) as exc:
                    failed[task_id] = str(exc)
                else:
                    refreshed.append(task_id)
    print(json.dumps({"refreshed": refreshed, "failed": failed}, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
