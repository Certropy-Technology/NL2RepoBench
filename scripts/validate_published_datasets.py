#!/usr/bin/env python3
"""Validate published dataset sources, compiled manifests, and Harbor hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _toml(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"invalid TOML {path}: {exc}") from exc


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve(base: Path, value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty relative path")
    path = (base / value).resolve()
    try:
        path.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(f"{field} escapes campaign root") from exc
    return path


def validate_published_datasets(
    campaign_path: Path,
    *,
    catalog_root: Path,
) -> dict[str, Any]:
    campaign = _json(campaign_path)
    datasets = campaign.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise ValueError("campaign.datasets must be a non-empty list")
    campaign_tasks = {
        raw["task_id"]: raw
        for raw in campaign.get("tasks", [])
        if isinstance(raw, dict) and isinstance(raw.get("task_id"), str)
    }
    dataset_reports: list[dict[str, Any]] = []
    all_task_ids: set[str] = set()
    for raw_dataset in datasets:
        if not isinstance(raw_dataset, dict):
            raise ValueError("campaign dataset entries must be objects")
        dataset_id = raw_dataset.get("dataset_id")
        language = raw_dataset.get("language")
        source_path = _resolve(campaign_path.parent, raw_dataset.get("source"), "dataset.source")
        compiled_root = _resolve(
            campaign_path.parent, raw_dataset.get("compiled"), "dataset.compiled"
        )
        source = _toml(source_path)
        compiled = _json(compiled_root / "dataset.manifest.json")
        if compiled.get("dataset_id") != dataset_id:
            raise ValueError(f"dataset {dataset_id}: compiled dataset_id mismatch")
        if compiled.get("version") != source.get("version"):
            raise ValueError(f"dataset {dataset_id}: compiled version mismatch")
        declared_tasks = source.get("tasks")
        compiled_tasks = compiled.get("tasks")
        if not isinstance(declared_tasks, list) or not isinstance(compiled_tasks, list):
            raise ValueError(f"dataset {dataset_id}: tasks must be lists")
        compiled_ids = [item.get("task_id") for item in compiled_tasks if isinstance(item, dict)]
        if sorted(declared_tasks) != sorted(compiled_ids):
            raise ValueError(f"dataset {dataset_id}: source and compiled task entries differ")
        if all_task_ids.intersection(compiled_ids):
            raise ValueError(f"dataset {dataset_id}: task appears in multiple datasets")
        all_task_ids.update(compiled_ids)

        task_reports: list[dict[str, Any]] = []
        for task_id in compiled_ids:
            if not isinstance(task_id, str):
                raise ValueError(f"dataset {dataset_id}: invalid task reference")
            source_task = catalog_root / task_id / "task.toml"
            harbor_task = catalog_root / task_id / "harbor/task.toml"
            canonical_task = compiled_root / task_id / "manifest.json"
            source_data = _toml(source_task)
            lifecycle = source_data.get("lifecycle")
            lifecycle = lifecycle if isinstance(lifecycle, dict) else {}
            if lifecycle.get("status") != "published":
                raise ValueError(f"{task_id}: catalog lifecycle is not published")
            metadata = source_data.get("metadata")
            metadata = metadata if isinstance(metadata, dict) else {}
            if metadata.get("language") != language:
                raise ValueError(f"{task_id}: catalog language does not match dataset")
            if not harbor_task.is_file() or not canonical_task.is_file():
                raise ValueError(f"{task_id}: Harbor or canonical manifest is missing")
            canonical_data = _json(canonical_task)
            canonical_lifecycle = canonical_data.get("lifecycle")
            canonical_lifecycle = (
                canonical_lifecycle if isinstance(canonical_lifecycle, dict) else {}
            )
            if canonical_lifecycle.get("status") != "published":
                raise ValueError(f"{task_id}: compiled lifecycle is not published")
            campaign_task = campaign_tasks.get(task_id, {})
            source_digest = _sha256(source_task)
            harbor_digest = _sha256(harbor_task)
            if campaign_task.get("source_manifest_sha256") not in {None, source_digest}:
                raise ValueError(f"{task_id}: source hash differs from campaign")
            if campaign_task.get("harbor_task_sha256") not in {None, harbor_digest}:
                raise ValueError(f"{task_id}: Harbor task hash differs from campaign")
            task_reports.append(
                {
                    "task_id": task_id,
                    "source_sha256": source_digest,
                    "harbor_task_sha256": harbor_digest,
                    "canonical_manifest": str(canonical_task),
                }
            )
        dataset_reports.append(
            {
                "dataset_id": dataset_id,
                "version": source.get("version"),
                "language": language,
                "task_count": len(task_reports),
                "tasks": task_reports,
            }
        )
    return {
        "schema_version": "1.0",
        "dataset_count": len(dataset_reports),
        "task_count": len(all_task_ids),
        "datasets": dataset_reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/tasks"))
    args = parser.parse_args()
    try:
        report = validate_published_datasets(args.campaign, catalog_root=args.catalog_root)
    except (OSError, ValueError) as exc:
        print(f"published dataset validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
