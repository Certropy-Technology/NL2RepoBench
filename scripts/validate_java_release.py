#!/usr/bin/env python3
"""Validate the separate Java/Maven pilot release without publishing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

TASKS = ("java-commons-codec", "java-commons-csv", "java-semver4j")



def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate(root: Path) -> dict[str, Any]:
    dataset_path = root / "catalog/datasets/nl2repobench-java-pilot/dataset.toml"
    dataset = tomllib.loads(dataset_path.read_text(encoding="utf-8"))
    if dataset.get("dataset_id") != "nl2repobench-java-pilot":
        raise ValueError("Java dataset ID is invalid")
    if dataset.get("tasks") != list(TASKS):
        raise ValueError("Java pilot task list is not canonical")
    reviews_root = root / "catalog/datasets/nl2repobench-java-pilot/reviews"
    review_verdicts = []
    for review_name in ("spec-review.json", "security-review.json"):
        review = load_json(reviews_root / review_name)
        if review.get("verdict") != "approve":
            raise ValueError(f"review is not approved: {review_name}")
        review_verdicts.append(review_name)
    model_pilot = load_json(reviews_root / "model-pilot-status.json")
    if model_pilot.get("status") not in {
        "blocked",
        "partial",
        "complete-with-model-failure",
        "complete",
    }:
        raise ValueError("Java model pilot status is invalid")
    model_evidence_root = (
        root / "catalog/datasets/nl2repobench-java-pilot/model-pilot-evidence"
    )
    for model_name in ("sol-java-semver4j", "opus-java-semver4j"):
        receipt = load_json(model_evidence_root / model_name / "receipt.json")
        if receipt.get("task_id") != "java-semver4j":
            raise ValueError(f"model evidence task mismatch: {model_name}")
        if receipt.get("public_network_available") is not False:
            raise ValueError(f"model evidence is not offline: {model_name}")
        if not isinstance(receipt.get("workspace_tree_sha256"), str):
            raise ValueError(f"model workspace hash is missing: {model_name}")
    runtime_evidence = load_json(
        root
        / "catalog/datasets/nl2repobench-java-pilot/runtime-build-evidence.json"
    )
    if runtime_evidence.get("registry_required") is not False:
        raise ValueError("Java runtime build must not require an image registry")
    for name in ("java_runtime", "openhands_runtime"):
        runtime = runtime_evidence.get(name, {})
        if not isinstance(runtime, dict) or not runtime.get("offline_probe"):
            raise ValueError(f"{name}: Dockerfile build evidence is incomplete")
    rows: list[dict[str, Any]] = []
    for task_id in TASKS:
        source_root = root / "catalog/sources" / task_id
        task_root = root / "catalog/tasks" / task_id
        source = tomllib.loads((source_root / "task.toml").read_text(encoding="utf-8"))
        expected_versions = {
            "java-commons-codec": "1.1.0",
            "java-commons-csv": "1.2.0",
            "java-semver4j": "1.3.0",
        }
        expected_version = expected_versions[task_id]
        if source.get("version") != expected_version:
            raise ValueError(f"{task_id}: unexpected task version")
        if source.get("metadata", {}).get("language") != "java":
            raise ValueError(f"{task_id}: language is not java")
        runtime = source.get("environment", {}).get("runtime", {})
        if runtime.get("package_manager") != "maven":
            raise ValueError(f"{task_id}: package manager is not Maven")
        traceability = json.loads(
            (source_root / "evidence/traceability.json").read_text(encoding="utf-8")
        )
        selected = traceability.get("api_inventory", {}).get("selected_symbols", [])
        leaves = traceability.get("contract_leaf", {}).get("ids", [])
        if not isinstance(selected, list) or not isinstance(leaves, list):
            raise ValueError(f"{task_id}: traceability inventory is malformed")
        if task_id == "java-semver4j" and len(selected) != 9:
            raise ValueError("java-semver4j: selected API inventory must match its nine leaves")
        frozen_total = traceability.get("contract_leaf", {}).get("frozen_total")
        expected_total = source.get("tests", {}).get("expected_total")
        if frozen_total != expected_total:
            raise ValueError(f"{task_id}: traceability denominator mismatch")
        lifecycle = source.get("lifecycle", {})
        if lifecycle.get("status") not in {"controls-passed", "reviewed", "piloted"}:
            raise ValueError(f"{task_id}: invalid pilot lifecycle status")
        evidence = load_json(source_root / "production-evidence.json")
        if evidence.get("terminal_kind") != "valid":
            raise ValueError(f"{task_id}: evidence is not valid")
        oracle = evidence.get("oracle", {})
        if oracle.get("valid") is not True or oracle.get("reward") < 0.8:
            raise ValueError(f"{task_id}: Oracle evidence is insufficient")
        if set(evidence.get("controls", {})) != {
            "empty", "stub", "forgery", "install-failure", "hang", "offline"
        }:
            raise ValueError(f"{task_id}: controls evidence is incomplete")
        manifest = task_root / "bundle.manifest.json"
        if not manifest.is_file():
            raise ValueError(f"{task_id}: generated bundle is missing")
        rows.append(
            {
                "task_id": task_id,
                "version": source["version"],
                "source_sha256": sha256(source_root / "task.toml"),
                "bundle_manifest_sha256": sha256(manifest),
                "oracle_grading": oracle["grading"]["path"],
                "controls": sorted(evidence["controls"]),
                "lifecycle": lifecycle["status"],
            }
        )
    return {
        "schema_version": "1.0",
        "dataset_id": dataset["dataset_id"],
        "version": dataset["version"],
        "runtime": "java+maven",
        "status": "piloted" if model_pilot.get("status") == "complete" else "pilot-blocked",
        "publication_approval": False,
        "reviews": review_verdicts,
        "model_pilot": model_pilot,
        "runtime_build_evidence": "runtime-build-evidence.json",
        "tasks": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.root.resolve())
        payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
        print(payload, end="")
        return 0
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"Java release validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
