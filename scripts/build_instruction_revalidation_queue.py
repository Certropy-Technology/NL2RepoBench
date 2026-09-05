#!/usr/bin/env python3
"""Build a deterministic queue after public instruction changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from nl2repobench.authoring.catalog import CatalogCompiler


REVALIDATION_STATUSES = {"packaged", "oracle-passed", "controls-passed"}


def git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()


def changed_instruction_paths(root: Path, baseline: str, head: str) -> list[Path]:
    output = git_output(
        root,
        "diff",
        "--name-only",
        f"{baseline}..{head}",
        "--",
        "catalog/sources/*/instruction.md",
    )
    return sorted(root / item for item in output.splitlines() if item)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build_queue(root: Path, baseline: str, head: str) -> dict[str, object]:
    changed = changed_instruction_paths(root, baseline, head)
    tasks: list[dict[str, object]] = []
    status_counts: Counter[str] = Counter()

    for instruction_path in changed:
        source_root = instruction_path.parent
        source = CatalogCompiler.load_task(source_root)
        status = source.lifecycle.status.value
        status_counts[status] += 1
        if status not in REVALIDATION_STATUSES:
            continue
        evidence_path = source_root / "production-evidence.json"
        tasks.append(
            {
                "task_id": source.task_id,
                "version": source.version,
                "lifecycle_status": status,
                "source_digest": source.content_digest(),
                "instruction_sha256": sha256(instruction_path),
                "prior_evidence_path": (
                    str(evidence_path.relative_to(root))
                    if evidence_path.is_file()
                    else None
                ),
                "prior_receipts_current": False,
                "required_gates": [
                    "compile-final-manifest",
                    "oracle-no-network",
                    "empty-control",
                    "stub-control",
                    "forgery-control",
                    "offline-control",
                    "source-and-projection-validation",
                ],
            }
        )

    return {
        "schema_version": 1,
        "baseline_commit": baseline,
        "instruction_migration_commit": head,
        "network_policy": "no-network",
        "invalidation_reason": (
            "Public instruction bytes changed, so compiled manifests and prior "
            "Oracle/control receipts are not current for the new source digest."
        ),
        "changed_instruction_count": len(changed),
        "changed_status_counts": dict(sorted(status_counts.items())),
        "revalidation_task_count": len(tasks),
        "tasks": tasks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    baseline = git_output(root, "rev-parse", args.baseline)
    head = git_output(root, "rev-parse", args.head)
    queue = build_queue(root, baseline, head)
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    display_output = (
        str(output.relative_to(root)) if output.is_relative_to(root) else str(output)
    )
    print(
        json.dumps(
            {
                "output": display_output,
                "changed_instruction_count": queue["changed_instruction_count"],
                "revalidation_task_count": queue["revalidation_task_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
