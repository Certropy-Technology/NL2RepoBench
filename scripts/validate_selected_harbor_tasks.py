#!/usr/bin/env python3
"""Run the deterministic source-to-Harbor gate for one selected task set."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tomllib
from pathlib import Path

from nl2repobench.harbor.private_artifacts import compile_resolver_for_source
from nl2repobench.harbor.registry import HarborCompilerRegistry
from nl2repobench.storage.artifacts import FileArtifactStore


class SelectedGateError(ValueError):
    """Raised when a selected source does not reproduce its checked-in bundle."""


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _inventory(root: Path) -> dict[str, tuple[str, int]]:
    return {
        path.relative_to(root).as_posix(): (_sha256(path), path.stat().st_size)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _compare_bundle(task_id: str, expected: Path, actual: Path) -> None:
    if _inventory(expected) != _inventory(actual):
        raise SelectedGateError(f"{task_id}: generated bundle is not byte-identical")


def _selection_ids(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("tasks")
    if not isinstance(rows, list):
        raise SelectedGateError("selection report tasks must be a list")
    ids = sorted(
        str(row["task"])
        for row in rows
        if isinstance(row, dict) and row.get("eligible") is True
    )
    if len(ids) != len(set(ids)):
        raise SelectedGateError("selection report contains duplicate eligible tasks")
    return ids


def _toolchain_name(source_data: dict[str, object]) -> str:
    metadata = source_data.get("metadata")
    if not isinstance(metadata, dict):
        raise SelectedGateError("source metadata is missing")
    language = metadata.get("language")
    if language == "python":
        return "toolchain.lock.toml"
    if language == "node":
        return "toolchain.node.lock.toml"
    if language == "go":
        return "toolchain.go.lock.toml"
    raise SelectedGateError(f"unsupported selected language: {language!r}")


def _assert_agent_context(
    task_id: str,
    source_data: dict[str, object],
    task_root: Path,
    expected_runtime_image: str,
    expected_runtime_image_id: str,
) -> None:
    environment = task_root / "environment"
    dockerfile = (environment / "Dockerfile").read_text(encoding="utf-8")
    task_data = tomllib.loads((task_root / "task.toml").read_text(encoding="utf-8"))
    runtime_environment = task_data.get("environment")
    verifier = task_data.get("verifier")
    if not isinstance(runtime_environment, dict) or runtime_environment.get(
        "network_mode"
    ) != "no-network":
        raise SelectedGateError(f"{task_id}: Agent network mode is not no-network")
    if not isinstance(verifier, dict) or verifier.get("network_mode") != "no-network":
        raise SelectedGateError(f"{task_id}: verifier network mode is not no-network")
    if verifier.get("allowed_hosts", []) or runtime_environment.get("allowed_hosts", []):
        raise SelectedGateError(f"{task_id}: generated network allowlist is not empty")

    metadata = source_data.get("metadata")
    assert isinstance(metadata, dict)
    language = metadata["language"]
    if language == "python":
        required = {
            "candidate-requirements.lock.txt",
            "--require-hashes",
            "--index-url https://pypi.org/simple",
            "pip-index-hash-locked-v1",
            "/opt/openhands-sdk-venv/bin/python",
        }
    elif language == "node":
        required = {
            "npm-bundle",
            "npm_config_offline=true",
            "/opt/openhands-sdk-venv/bin/python",
        }
    else:
        required = {
            "go-module-bundle",
            "GOPROXY=off",
            "/opt/openhands-sdk-venv/bin/python",
        }
    missing = sorted(value for value in required if value not in dockerfile)
    if missing:
        raise SelectedGateError(f"{task_id}: Agent Dockerfile is missing {missing}")
    if expected_runtime_image not in dockerfile:
        raise SelectedGateError(f"{task_id}: Agent Dockerfile has the wrong runtime image")
    if f'agent-runtime-image-id="{expected_runtime_image_id}"' not in dockerfile:
        raise SelectedGateError(f"{task_id}: Agent Dockerfile has no runtime image identity label")

    forbidden = {"private", "verifier", "solution", "command-plan.json"}
    leaks = [
        path.relative_to(environment).as_posix()
        for path in environment.rglob("*")
        if path.is_file()
        and (set(path.relative_to(environment).parts) & forbidden)
    ]
    if leaks:
        raise SelectedGateError(f"{task_id}: private Agent assets found: {sorted(leaks)}")


def validate(
    *,
    selection: Path,
    sources: Path,
    tasks: Path,
    artifact_root: Path,
    repository_root: Path,
    output_root: Path,
) -> dict[str, object]:
    task_ids = _selection_ids(selection)
    if len(task_ids) != 51:
        raise SelectedGateError(f"expected 51 eligible tasks, got {len(task_ids)}")
    output_root.mkdir(parents=True, exist_ok=True)
    first_root = output_root / "compile-a"
    second_root = output_root / "compile-b"
    for root in (first_root, second_root):
        if root.exists():
            shutil.rmtree(root)
    artifact_store = FileArtifactStore(artifact_root)
    registry = HarborCompilerRegistry.default()
    rows: list[dict[str, object]] = []
    for task_id in task_ids:
        source_root = sources / task_id
        checked_in = tasks / task_id
        if not source_root.is_dir() or not checked_in.is_dir():
            raise SelectedGateError(f"{task_id}: source or generated task directory is missing")
        source_data = tomllib.loads((source_root / "task.toml").read_text(encoding="utf-8"))
        evidence = source_root / "production-evidence.json"
        if not evidence.is_file():
            raise SelectedGateError(f"{task_id}: production-evidence.json is missing")
        if json.loads(evidence.read_text(encoding="utf-8")).get("task_id") != task_id:
            raise SelectedGateError(f"{task_id}: production evidence task_id mismatch")
        toolchain = repository_root / _toolchain_name(source_data)
        toolchain_data = tomllib.loads(toolchain.read_text(encoding="utf-8"))
        runtime = toolchain_data["agent_runtime"]
        _assert_agent_context(
            task_id,
            source_data,
            checked_in,
            str(runtime["image"]),
            str(runtime["image_id"]),
        )
        resolver = compile_resolver_for_source(
            source_root,
            artifact_store=artifact_store,
            compiled_root=(repository_root / ".nl2repo/compiled").resolve(),
        )
        first = registry.compile_task(
            source_root,
            first_root,
            toolchain,
            artifact_resolver=resolver,
        )
        second = registry.compile_task(
            source_root,
            second_root,
            toolchain,
            artifact_resolver=resolver,
        )
        _compare_bundle(task_id, checked_in, first)
        _compare_bundle(task_id, first, second)
        rows.append(
            {
                "task_id": task_id,
                "language": source_data["metadata"]["language"],
                "source_evidence_sha256": _sha256(evidence),
                "bundle_manifest_sha256": _sha256(checked_in / "bundle.manifest.json"),
                "deterministic": True,
            }
        )
    return {
        "schema_version": "1.0",
        "report_kind": "selected-harbor-source-to-projection-gate",
        "selection": str(selection.relative_to(repository_root)),
        "task_count": len(rows),
        "error_count": 0,
        "tasks": rows,
        "ok": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--sources", type=Path, default=Path("catalog/sources"))
    parser.add_argument("--tasks", type=Path, default=Path("catalog/tasks"))
    parser.add_argument("--artifact-root", type=Path, default=Path(".nl2repo/artifacts"))
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(".nl2repo/validation/selected-harbor"),
    )
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    repository_root = Path.cwd().resolve()
    try:
        report = validate(
            selection=args.selection.resolve(),
            sources=args.sources.resolve(),
            tasks=args.tasks.resolve(),
            artifact_root=args.artifact_root.resolve(),
            repository_root=repository_root,
            output_root=args.output_root.resolve(),
        )
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"selected Harbor gate failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"report": str(args.report), "task_count": report["task_count"], "ok": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
