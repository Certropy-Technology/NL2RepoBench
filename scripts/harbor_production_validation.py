#!/usr/bin/env python3
"""Shared fail-closed validation for the Harbor production catalog.

The production gate intentionally separates canonical task metadata from run
evidence.  ``task.toml`` remains the compiler input; a sibling
``production-evidence.json`` records immutable paths and hashes for Oracle,
control, or blocked-remediation logs without creating a compile/evidence hash
cycle.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

from nl2repobench.authoring.catalog import CatalogCompiler
from nl2repobench.harbor.registry import HarborCompilerRegistry
from nl2repobench.storage.artifacts import FileArtifactStore, LocalArtifactResolver

JsonObject = dict[str, Any]

VALID_STATUSES = frozenset({"controls-passed", "reviewed", "piloted", "published"})
BLOCKED_STATUSES = frozenset({"blocked", "excluded"})
TERMINAL_STATUSES = VALID_STATUSES | BLOCKED_STATUSES
FAILURE_CLASSES = frozenset({"source", "spec", "environment", "verifier", "infrastructure"})
REQUIRED_RUNTIME_FILES = frozenset(
    {
        "bundle.manifest.json",
        "environment/Dockerfile",
        "instruction.md",
        "solution/solve.sh",
        "task.toml",
        "tests/test.sh",
    }
)
REQUIRED_CONTROLS = frozenset({"empty", "stub", "forgery", "offline"})


class ProductionGateError(ValueError):
    """Raised for a malformed production-gate input or evidence record."""


def read_json_object(path: Path) -> JsonObject:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProductionGateError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProductionGateError(f"JSON root must be an object: {path}")
    return value


def read_toml_object(path: Path) -> JsonObject:
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ProductionGateError(f"invalid TOML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProductionGateError(f"TOML root must be a table: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def canonical_sha256(value: JsonObject) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


def directory_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return "sha256:" + digest.hexdigest()


def _safe_relative(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProductionGateError(f"{field} must be a non-empty relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ProductionGateError(f"{field} must not escape the repository: {value}")
    return value


def _git_output(repository_root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=repository_root, text=True, stderr=subprocess.STDOUT
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ProductionGateError(
            f"git {' '.join(args)} failed with {exc.returncode}: {exc.output.strip()}"
        ) from exc


def validate_frozen_input(
    input_path: Path,
    *,
    repository_root: Path,
    expected_sources: int,
    verify_git: bool = True,
) -> tuple[JsonObject, list[JsonObject]]:
    payload = read_json_object(input_path)
    if payload.get("schema_version") != "1.0":
        raise ProductionGateError("production input schema_version must be 1.0")
    expected_digest = payload.get("content_sha256")
    digest_payload = dict(payload)
    digest_payload.pop("content_sha256", None)
    if expected_digest != canonical_sha256(digest_payload):
        raise ProductionGateError("production input content_sha256 does not match its payload")
    if payload.get("source_count") != expected_sources:
        raise ProductionGateError(
            f"expected {expected_sources} frozen sources, got {payload.get('source_count')}"
        )
    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list) or len(raw_sources) != expected_sources:
        raise ProductionGateError("production input sources do not match source_count")
    sources: list[JsonObject] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_sources):
        if not isinstance(raw, dict):
            raise ProductionGateError(f"production input source {index} must be an object")
        task_id = raw.get("task_id")
        tree = raw.get("source_tree_sha1")
        if not isinstance(task_id, str) or not task_id or task_id in seen:
            raise ProductionGateError(f"invalid or duplicate frozen task_id: {task_id!r}")
        if (
            not isinstance(tree, str)
            or len(tree) != 40
            or any(c not in "0123456789abcdef" for c in tree)
        ):
            raise ProductionGateError(f"{task_id}: source_tree_sha1 must be a full Git SHA-1")
        seen.add(task_id)
        sources.append({"task_id": task_id, "source_tree_sha1": tree})
    if sources != sorted(sources, key=lambda item: str(item["task_id"])):
        raise ProductionGateError("production input sources must be sorted by task_id")
    if verify_git:
        base = payload.get("base_commit")
        source_root = payload.get("source_root")
        if not isinstance(base, str) or not base:
            raise ProductionGateError("production input base_commit is missing")
        if not isinstance(source_root, str) or not source_root:
            raise ProductionGateError("production input source_root is missing")
        lines = _git_output(repository_root, "ls-tree", f"{base}:{source_root}").splitlines()
        actual: list[JsonObject] = []
        for line in lines:
            metadata, task_id = line.split("\t", 1)
            _mode, kind, object_id = metadata.split()
            if kind == "tree":
                actual.append({"task_id": task_id, "source_tree_sha1": object_id})
        actual.sort(key=lambda item: str(item["task_id"]))
        if actual != sources:
            raise ProductionGateError("frozen source list differs from the base commit tree")
    return payload, sources


def _visible_directories(root: Path) -> set[str]:
    if not root.is_dir():
        raise ProductionGateError(f"directory does not exist: {root}")
    return {path.name for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")}


def _file_inventory(root: Path, *, exclude_manifest: bool = False) -> dict[str, tuple[str, int]]:
    inventory: dict[str, tuple[str, int]] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if exclude_manifest and relative == "bundle.manifest.json":
            continue
        inventory[relative] = (sha256_file(path).removeprefix("sha256:"), path.stat().st_size)
    return inventory


def _validate_bundle_manifest(task_id: str, task_root: Path) -> JsonObject:
    manifest_path = task_root / "bundle.manifest.json"
    manifest = read_json_object(manifest_path)
    if manifest.get("schema_version") != "1.0":
        raise ProductionGateError(f"{task_id}: bundle manifest schema must be 1.0")
    if manifest.get("mode") != "production":
        raise ProductionGateError(f"{task_id}: bundle manifest is not production mode")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise ProductionGateError(f"{task_id}: bundle manifest files must be non-empty")
    declared: dict[str, tuple[str, int]] = {}
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            raise ProductionGateError(f"{task_id}: bundle file {index} is not an object")
        relative = _safe_relative(raw.get("path"), f"{task_id}.bundle.files[{index}].path")
        digest = raw.get("sha256")
        size = raw.get("size_bytes")
        if relative in declared:
            raise ProductionGateError(f"{task_id}: duplicate bundle path: {relative}")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ProductionGateError(f"{task_id}: invalid bundle hash for {relative}")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ProductionGateError(f"{task_id}: invalid bundle size for {relative}")
        declared[relative] = (digest, size)
    actual = _file_inventory(task_root, exclude_manifest=True)
    if declared != actual:
        missing = sorted(set(declared) - set(actual))
        extra = sorted(set(actual) - set(declared))
        mismatched = sorted(
            path for path in set(declared) & set(actual) if declared[path] != actual[path]
        )
        raise ProductionGateError(
            f"{task_id}: bundle manifest mismatch; missing={missing}, extra={extra}, "
            f"mismatched={mismatched}"
        )
    return manifest


def _validate_runtime_shape(task_id: str, source_data: JsonObject, task_root: Path) -> JsonObject:
    actual_files = {
        path.relative_to(task_root).as_posix()
        for path in task_root.rglob("*")
        if path.is_file()
    }
    missing = sorted(REQUIRED_RUNTIME_FILES - actual_files)
    if missing:
        raise ProductionGateError(f"{task_id}: missing Harbor runtime files: {missing}")
    task_data = read_toml_object(task_root / "task.toml")
    if task_data.get("schema_version") != "1.4":
        raise ProductionGateError(f"{task_id}: generated Harbor task schema must be 1.4")
    verifier = task_data.get("verifier")
    if not isinstance(verifier, dict) or verifier.get("environment_mode") != "separate":
        raise ProductionGateError(f"{task_id}: verifier.environment_mode must be separate")
    metadata = task_data.get("metadata")
    source_tests = source_data.get("tests")
    if not isinstance(metadata, dict) or not isinstance(source_tests, dict):
        raise ProductionGateError(f"{task_id}: test metadata is malformed")
    if metadata.get("expected_test_count") != source_tests.get("expected_total"):
        raise ProductionGateError(f"{task_id}: generated expected denominator differs from source")
    source_environment = source_data.get("environment")
    runtime_environment = task_data.get("environment")
    if not isinstance(source_environment, dict) or not isinstance(runtime_environment, dict):
        raise ProductionGateError(f"{task_id}: environment metadata is malformed")
    policy = source_environment.get("network_policy")
    if not isinstance(policy, dict):
        raise ProductionGateError(f"{task_id}: source lacks explicit environment.network_policy")
    mode = policy.get("mode")
    if mode not in {"no-network", "allowlist"}:
        raise ProductionGateError(f"{task_id}: production source network mode is invalid: {mode}")
    if runtime_environment.get("network_mode") != mode or verifier.get("network_mode") != mode:
        raise ProductionGateError(f"{task_id}: generated network mode differs from source policy")
    grader_paths = (
        task_root / "tests/verifier/run.py",
        task_root / "tests/runtime/nl2repobench/verification/grader.py",
        task_root / "tests/runtime/node/grade-report.mjs",
    )
    if not any(path.is_file() for path in grader_paths):
        raise ProductionGateError(f"{task_id}: structured grader entrypoint is missing")
    manifest = _validate_bundle_manifest(task_id, task_root)
    if manifest.get("canonical_manifest_digest") != metadata.get("canonical_manifest_digest"):
        raise ProductionGateError(
            f"{task_id}: canonical manifest digest differs across bundle files"
        )
    return task_data


def _compare_compiled_bundle(task_id: str, checked_in: Path, compiled: Path) -> None:
    expected = _file_inventory(checked_in)
    actual = _file_inventory(compiled)
    if expected != actual:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        mismatched = sorted(
            path for path in set(expected) & set(actual) if expected[path] != actual[path]
        )
        raise ProductionGateError(
            f"{task_id}: checked-in task differs from production recompile; "
            f"missing={missing}, extra={extra}, mismatched={mismatched}"
        )


def _task_issue(task_id: str, message: str) -> JsonObject:
    return {"task_id": task_id, "message": message}


def validate_catalog(
    *,
    sources_root: Path,
    tasks_root: Path,
    input_path: Path,
    expected_sources: int,
    repository_root: Path,
    artifact_root: Path,
    python_toolchain: Path,
    node_toolchain: Path,
    verify_git: bool = True,
    compile_tasks: bool = True,
    require_evidence: bool = True,
) -> JsonObject:
    frozen, frozen_rows = validate_frozen_input(
        input_path,
        repository_root=repository_root,
        expected_sources=expected_sources,
        verify_git=verify_git,
    )
    frozen_ids = {str(row["task_id"]) for row in frozen_rows}
    current_ids = _visible_directories(sources_root)
    errors: list[JsonObject] = []
    if current_ids != frozen_ids:
        errors.append(
            _task_issue(
                "<catalog>",
                "current source IDs differ from frozen input; "
                f"missing={sorted(frozen_ids-current_ids)}, extra={sorted(current_ids-frozen_ids)}",
            )
        )

    rows: list[JsonObject] = []
    valid_ids: set[str] = set()
    blocked_ids: set[str] = set()
    excluded_ids: set[str] = set()
    resolver = LocalArtifactResolver(FileArtifactStore(artifact_root), allow_private=True)
    registry = HarborCompilerRegistry.default()
    compile_parent = tempfile.TemporaryDirectory(prefix="nl2repo-production-gate-")
    try:
        for task_id in sorted(frozen_ids):
            source_root = sources_root / task_id
            row: JsonObject = {
                "task_id": task_id,
                "source_path": source_root.relative_to(repository_root).as_posix(),
            }
            task_errors: list[str] = []
            try:
                source_data = read_toml_object(source_root / "task.toml")
                source = CatalogCompiler.load_task(source_root)
                if source.task_id != task_id:
                    raise ProductionGateError(
                        f"descriptor task_id {source.task_id!r} differs from directory"
                    )
                environment = source_data.get("environment")
                if not isinstance(environment, dict) or not isinstance(
                    environment.get("network_policy"), dict
                ):
                    raise ProductionGateError("missing explicit [environment.network_policy]")
                status = source.lifecycle.status.value
                row["status"] = status
                row["source_content_sha256"] = directory_sha256(source_root)
                if status in VALID_STATUSES:
                    category = "valid"
                    valid_ids.add(task_id)
                elif status == "blocked":
                    category = "blocked"
                    blocked_ids.add(task_id)
                elif status == "excluded":
                    category = "excluded"
                    excluded_ids.add(task_id)
                else:
                    category = "incomplete"
                    raise ProductionGateError(f"lifecycle status is not terminal: {status}")
                row["category"] = category
                evidence_path = source_root / "production-evidence.json"
                if evidence_path.is_file():
                    evidence = read_json_object(evidence_path)
                    if evidence.get("task_id") != task_id:
                        raise ProductionGateError("production evidence task_id mismatch")
                    row["evidence_path"] = evidence_path.relative_to(repository_root).as_posix()
                    row["evidence_sha256"] = sha256_file(evidence_path)
                    row["evidence"] = evidence
                elif require_evidence:
                    raise ProductionGateError("production-evidence.json is missing")

                runtime_root = tasks_root / task_id
                if category == "valid":
                    if not runtime_root.is_dir():
                        raise ProductionGateError("valid source has no Harbor runtime directory")
                    runtime_data = _validate_runtime_shape(task_id, source_data, runtime_root)
                    row["runtime_path"] = runtime_root.relative_to(repository_root).as_posix()
                    row["runtime_schema_version"] = runtime_data.get("schema_version")
                    row["expected_total"] = source_data.get("tests", {}).get("expected_total")
                    row["bundle_manifest_sha256"] = sha256_file(
                        runtime_root / "bundle.manifest.json"
                    )
                    if compile_tasks:
                        output_root = Path(compile_parent.name) / task_id
                        toolchain = (
                            node_toolchain
                            if source_data.get("schema_version") == "2.0"
                            else python_toolchain
                        )
                        compiled = registry.compile_task(
                            source_root,
                            output_root,
                            toolchain,
                            artifact_resolver=resolver,
                            allow_incomplete=False,
                        )
                        _compare_compiled_bundle(task_id, runtime_root, compiled)
                        row["production_recompile"] = "matched"
                elif runtime_root.exists():
                    raise ProductionGateError(
                        f"{category} source retains forbidden runtime directory"
                    )
            except (OSError, ValueError) as exc:
                task_errors.append(str(exc))
            if task_errors:
                row["errors"] = task_errors
                errors.extend(_task_issue(task_id, message) for message in task_errors)
            rows.append(row)
    finally:
        compile_parent.cleanup()

    runtime_ids = _visible_directories(tasks_root)
    if runtime_ids != valid_ids:
        errors.append(
            _task_issue(
                "<catalog>",
                "catalog/tasks does not equal valid task IDs; "
                f"missing={sorted(valid_ids-runtime_ids)}, extra={sorted(runtime_ids-valid_ids)}",
            )
        )
    counts = {
        "sources": len(frozen_ids),
        "valid": len(valid_ids),
        "blocked": len(blocked_ids),
        "excluded": len(excluded_ids),
        "incomplete_or_invalid": len(frozen_ids) - len(valid_ids | blocked_ids | excluded_ids),
        "runtime_tasks": len(runtime_ids),
    }
    if counts["valid"] + counts["blocked"] + counts["excluded"] != expected_sources:
        errors.append(
            _task_issue("<catalog>", "terminal category counts do not equal source count")
        )
    report: JsonObject = {
        "schema_version": "1.0",
        "report_kind": "harbor-production-gate",
        "repository_root": ".",
        "input": {
            "path": input_path.relative_to(repository_root).as_posix(),
            "content_sha256": frozen["content_sha256"],
            "base_commit": frozen["base_commit"],
        },
        "counts": counts,
        "tasks": rows,
        "errors": errors,
        "ok": not errors,
    }
    digest_payload = dict(report)
    report["content_sha256"] = canonical_sha256(digest_payload)
    return report


def _report_repository_root(report_path: Path, report: JsonObject) -> Path:
    value = report.get("repository_root", ".")
    if value != ".":
        raise ProductionGateError("report repository_root must be '.'")
    return report_path.resolve().parent.parent


def _verify_report_digest(report: JsonObject) -> None:
    expected = report.get("content_sha256")
    payload = dict(report)
    payload.pop("content_sha256", None)
    if expected != canonical_sha256(payload):
        raise ProductionGateError("gate report content_sha256 does not match")


def _artifact_from_record(
    record: JsonObject, field: str, *, repository_root: Path, task_id: str
) -> JsonObject:
    raw = record.get(field)
    if not isinstance(raw, dict):
        raise ProductionGateError(f"{task_id}: evidence {field} must be an object")
    relative = _safe_relative(raw.get("path"), f"{task_id}.{field}.path")
    path = repository_root / relative
    if not path.is_file():
        raise ProductionGateError(f"{task_id}: evidence file is missing: {relative}")
    expected = raw.get("sha256")
    actual = sha256_file(path)
    if expected != actual:
        raise ProductionGateError(f"{task_id}: evidence hash mismatch: {relative}")
    return read_json_object(path)


def _file_from_record(
    record: JsonObject, field: str, *, repository_root: Path, task_id: str
) -> Path:
    raw = record.get(field)
    if not isinstance(raw, dict):
        raise ProductionGateError(f"{task_id}: evidence {field} must be an object")
    relative = _safe_relative(raw.get("path"), f"{task_id}.{field}.path")
    path = repository_root / relative
    if not path.is_file():
        raise ProductionGateError(f"{task_id}: evidence file is missing: {relative}")
    if raw.get("sha256") != sha256_file(path):
        raise ProductionGateError(f"{task_id}: evidence hash mismatch: {relative}")
    return path


def _validate_command(record: JsonObject, task_id: str, label: str) -> None:
    command = record.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ProductionGateError(f"{task_id}: {label} command is missing")
    exit_code = record.get("exit_code")
    if isinstance(exit_code, bool) or not isinstance(exit_code, int):
        raise ProductionGateError(f"{task_id}: {label} exit_code must be an integer")


def _validate_grading(
    task_id: str,
    grading: JsonObject,
    *,
    expected_total: int,
    minimum_reward: float,
    maximum_reward: float,
) -> None:
    reward = grading.get("reward")
    counts = grading.get("counts")
    collection = grading.get("collection")
    if grading.get("valid") is not True:
        raise ProductionGateError(f"{task_id}: grading valid is not true")
    if (
        isinstance(reward, bool)
        or not isinstance(reward, (int, float))
        or not math.isfinite(reward)
    ):
        raise ProductionGateError(f"{task_id}: grading reward is invalid")
    if not minimum_reward <= float(reward) <= maximum_reward:
        raise ProductionGateError(
            f"{task_id}: grading reward {reward} outside [{minimum_reward}, {maximum_reward}]"
        )
    if not isinstance(counts, dict) or counts.get("collected") != expected_total:
        raise ProductionGateError(f"{task_id}: grading collection differs from frozen total")
    if grading.get("expected_total") != expected_total:
        raise ProductionGateError(f"{task_id}: grading expected_total differs from source")
    if isinstance(collection, dict) and collection.get("collection_errors"):
        raise ProductionGateError(f"{task_id}: grading contains collection errors")
    if grading.get("failure_reason") not in {None, ""}:
        raise ProductionGateError(f"{task_id}: grading contains a verifier/setup failure")


def _validate_network(task_id: str, network: JsonObject) -> None:
    if network.get("public_network_available") is not False:
        raise ProductionGateError(f"{task_id}: verifier network was available")
    probes = network.get("probes")
    if (
        not isinstance(probes, dict)
        or not probes
        or any(value is not False for value in probes.values())
    ):
        raise ProductionGateError(f"{task_id}: offline network probes are incomplete or succeeded")


def _validate_oracle_row(row: JsonObject, repository_root: Path) -> None:
    task_id = str(row["task_id"])
    evidence = row.get("evidence")
    if not isinstance(evidence, dict):
        raise ProductionGateError(f"{task_id}: production evidence is missing")
    oracle = evidence.get("oracle")
    if not isinstance(oracle, dict):
        raise ProductionGateError(f"{task_id}: Oracle evidence is missing")
    _validate_command(oracle, task_id, "Oracle")
    if oracle.get("exit_code") != 0:
        raise ProductionGateError(f"{task_id}: Oracle command did not exit zero")
    if oracle.get("harbor_version") != "0.21.0":
        raise ProductionGateError(f"{task_id}: Oracle Harbor version must be 0.21.0")
    expected_total = row.get("expected_total")
    if (
        isinstance(expected_total, bool)
        or not isinstance(expected_total, int)
        or expected_total <= 0
    ):
        raise ProductionGateError(f"{task_id}: report expected_total is invalid")
    grading = _artifact_from_record(
        oracle, "grading", repository_root=repository_root, task_id=task_id
    )
    _validate_grading(
        task_id,
        grading,
        expected_total=expected_total,
        minimum_reward=0.80,
        maximum_reward=1.0,
    )
    network = _artifact_from_record(
        oracle, "network", repository_root=repository_root, task_id=task_id
    )
    _validate_network(task_id, network)


def _validate_controls_row(row: JsonObject, repository_root: Path) -> None:
    task_id = str(row["task_id"])
    evidence = row.get("evidence")
    if not isinstance(evidence, dict):
        raise ProductionGateError(f"{task_id}: production evidence is missing")
    controls = evidence.get("controls")
    if not isinstance(controls, dict) or not REQUIRED_CONTROLS.issubset(controls):
        raise ProductionGateError(f"{task_id}: controls must include {sorted(REQUIRED_CONTROLS)}")
    expected_total = row.get("expected_total")
    if (
        isinstance(expected_total, bool)
        or not isinstance(expected_total, int)
        or expected_total <= 0
    ):
        raise ProductionGateError(f"{task_id}: report expected_total is invalid")
    for name in sorted(REQUIRED_CONTROLS):
        control = controls.get(name)
        if not isinstance(control, dict):
            raise ProductionGateError(f"{task_id}: control {name} must be an object")
        _validate_command(control, task_id, f"control {name}")
        if control.get("exit_code") != 0:
            raise ProductionGateError(f"{task_id}: control {name} command did not exit zero")
        network = _artifact_from_record(
            control, "network", repository_root=repository_root, task_id=task_id
        )
        _validate_network(task_id, network)
        if name == "offline":
            if control.get("completed") is not True:
                raise ProductionGateError(f"{task_id}: offline verifier did not complete")
            continue
        grading = _artifact_from_record(
            control, "grading", repository_root=repository_root, task_id=task_id
        )
        if (
            name == "empty"
            and grading.get("failure_reason") == "candidate-installation-failed"
            and grading.get("failure_class") == "model"
            and grading.get("reward") == 0.0
            and isinstance(grading.get("counts"), dict)
            and grading["counts"].get("collected") == 0
        ):
            continue
        _validate_grading(
            task_id,
            grading,
            expected_total=expected_total,
            minimum_reward=0.0,
            maximum_reward=0.20,
        )
        if name == "forgery" and control.get("verifier_owned_reward") is not True:
            raise ProductionGateError(f"{task_id}: forgery control lacks verifier-owned proof")


def _validate_blocked_row(row: JsonObject, repository_root: Path) -> None:
    task_id = str(row["task_id"])
    evidence = row.get("evidence")
    if not isinstance(evidence, dict):
        raise ProductionGateError(f"{task_id}: blocked evidence is missing")
    blocked = evidence.get("blocked")
    if not isinstance(blocked, dict):
        raise ProductionGateError(f"{task_id}: blocked evidence record is missing")
    failure_class = blocked.get("failure_class")
    if failure_class not in FAILURE_CLASSES:
        raise ProductionGateError(f"{task_id}: blocked failure_class is invalid")
    next_step = blocked.get("next_step")
    if not isinstance(next_step, str) or not next_step.strip():
        raise ProductionGateError(f"{task_id}: blocked next_step is missing")
    commands = blocked.get("commands")
    if not isinstance(commands, list) or not commands:
        raise ProductionGateError(f"{task_id}: blocked remediation commands are missing")
    for index, raw in enumerate(commands):
        if not isinstance(raw, dict):
            raise ProductionGateError(f"{task_id}: blocked command {index} is malformed")
        _validate_command(raw, task_id, f"blocked command {index}")
        version = raw.get("tool_version")
        if not isinstance(version, str) or not version:
            raise ProductionGateError(f"{task_id}: blocked command {index} lacks tool_version")
        log = _file_from_record(
            raw, "log", repository_root=repository_root, task_id=task_id
        )
        if log.stat().st_size == 0:
            raise ProductionGateError(f"{task_id}: blocked command {index} log is empty")
    source = blocked.get("source_freeze")
    if not isinstance(source, dict):
        raise ProductionGateError(f"{task_id}: blocked source-freeze evidence is missing")
    known = source.get("status") == "known"
    failed = source.get("status") == "failed" and isinstance(source.get("reason"), str)
    if not (known or failed):
        raise ProductionGateError(f"{task_id}: blocked source authority is unresolved")


def validate_evidence(report_path: Path, kind: str) -> JsonObject:
    report = read_json_object(report_path)
    _verify_report_digest(report)
    if report.get("report_kind") != "harbor-production-gate":
        raise ProductionGateError("not a Harbor production gate report")
    if report.get("ok") is not True:
        raise ProductionGateError("catalog gate report is not successful")
    if kind not in {"oracle", "controls", "blocked"}:
        raise ProductionGateError("evidence kind must be oracle, controls, or blocked")
    repository_root = _report_repository_root(report_path, report)
    raw_rows = report.get("tasks")
    if not isinstance(raw_rows, list):
        raise ProductionGateError("gate report tasks must be a list")
    rows = [row for row in raw_rows if isinstance(row, dict)]
    selected = (
        [row for row in rows if row.get("category") == "valid"]
        if kind in {"oracle", "controls"}
        else [row for row in rows if row.get("category") in BLOCKED_STATUSES]
    )
    errors: list[JsonObject] = []
    for row in selected:
        task_id = str(row.get("task_id"))
        try:
            if kind == "oracle":
                _validate_oracle_row(row, repository_root)
            elif kind == "controls":
                _validate_controls_row(row, repository_root)
            else:
                _validate_blocked_row(row, repository_root)
        except (OSError, ValueError) as exc:
            errors.append(_task_issue(task_id, str(exc)))
    return {
        "schema_version": "1.0",
        "report_kind": f"harbor-production-{kind}-evidence",
        "tasks_checked": len(selected),
        "errors": errors,
        "ok": not errors,
    }


def write_report(path: Path, report: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
