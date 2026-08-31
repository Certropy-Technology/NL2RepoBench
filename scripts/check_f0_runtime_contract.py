#!/usr/bin/env python3
"""Fail closed until the F0 canonical migration has no active runtime bypasses."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

from pydantic import ValidationError

from nl2repobench.domain.canonical_contract import TaskSource

CONTRACT_SCHEMA_VERSION = "1.0"
CONTRACT_PATH = "harbor-runner/private-staging-contract.json"
LANES = frozenset({"python+pip", "python+uv", "node+npm", "node+pnpm", "go+go-modules"})
ARTIFACT_KINDS = frozenset(
    {"dependency-lock", "offline-store", "test-bundle", "verifier-bundle", "oracle-bundle"}
)
ROOT_KEYS = frozenset({"dependency", "oracle", "test", "verifier"})
ROOT_OWNER_UID = 0
ROOT_OWNER_GID = 0
ARTIFACT_ROOTS = {
    "dependency-lock": "dependency",
    "offline-store": "dependency",
    "oracle-bundle": "oracle",
    "test-bundle": "test",
    "verifier-bundle": "verifier",
}
RELATIVE_PATH = re.compile(r"^(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+$")
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "contract_id",
        "purpose",
        "staging_roots",
        "allowed_artifact_kinds",
        "artifact_kind_roots",
        "authorization",
        "limits",
        "lanes",
        "lifetime",
        "audit_receipt",
    }
)
ROOT_FIELDS = frozenset({"ephemeral", "mode", "uid", "gid", "path"})
LIMIT_FIELDS = frozenset(
    {"max_member_bytes", "max_members", "max_path_bytes", "max_total_bytes"}
)
LANE_FIELDS = frozenset(
    {
        "allowed_artifact_kinds",
        "artifact_kind_roots",
        "offline_smoke_command_id",
        "toolchain_binding",
    }
)
AUTHORIZATION = {
    "digest_algorithm": "sha256",
    "requires_private_visibility": True,
    "resolver_scope": "task-and-manifest",
    "scope_fields": [
        "task_id",
        "manifest_digest",
        "purpose",
        "staging_root",
        "allowed_digests",
    ],
}
TOOLCHAIN_BINDING = {
    "digest_format": "sha256:<64 lowercase hex>",
    "required": True,
    "source": "expected_toolchain_digest",
}
LIFETIME = {
    "cleanup_deadline_seconds": 60,
    "delete_on_failure": True,
    "max_seconds": 7200,
    "retain_audit_receipt": True,
}
AUDIT_RECEIPT = {
    "path_policy": "source-local-hash-bound",
    "required_fields": [
        "operation_id",
        "task_id",
        "manifest_digest",
        "artifact_digest",
        "staging_root",
        "started_at",
        "finished_at",
        "cleanup_complete",
    ],
    "requires_sha256": True,
    "schema_version": "1.0",
}
SMOKE_IDS = {
    "python+pip": "python-pip-offline-install-v1",
    "python+uv": "python-uv-offline-install-v1",
    "node+npm": "node-npm-offline-install-v1",
    "node+pnpm": "node-pnpm-offline-install-v1",
    "go+go-modules": "go-modules-offline-build-v1",
}
LIMITS = {
    "dependency-lock": (64, 4 * 1024 * 1024, 16 * 1024 * 1024),
    "offline-store": (100_000, 512 * 1024 * 1024, 2 * 1024**3),
    "test-bundle": (10_000, 512 * 1024 * 1024, 2 * 1024**3),
    "verifier-bundle": (10_000, 512 * 1024 * 1024, 2 * 1024**3),
    "oracle-bundle": (10_000, 512 * 1024 * 1024, 2 * 1024**3),
}


@dataclass(frozen=True, slots=True)
class Violation:
    path: str
    line: int
    token: str


FORBIDDEN = {
    "legacy-domain-model": re.compile(r"\bdomain\.models\b"),
    "models_v2": re.compile(r"(?:domain|harbor|verification)\.models_v2|models_v2\.py"),
    "v2-model": re.compile(r"\b(?:TaskManifestV2|DeclarativeTaskSourceV2|V2RecordModel)\b"),
    "legacy-lock": re.compile(r"\b(?:lock_artifact|module_bundle)\b"),
    "schema-dispatch": re.compile(r"schema_version\s*(?:==|!=)\s*[\"']2\.0[\"']"),
    "broad-private": re.compile(r"allow_private|--allow-private"),
}


def scan_runtime(repository_root: Path) -> tuple[Violation, ...]:
    source_root = repository_root / "src/nl2repobench"
    violations: list[Violation] = []
    for path in sorted(source_root.rglob("*.py")):
        relative = path.relative_to(repository_root)
        if "analysis" in relative.parts and "archive" in relative.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for token, pattern in FORBIDDEN.items():
                if pattern.search(line):
                    violations.append(Violation(relative.as_posix(), line_number, token))
    return tuple(violations)


def canonical_source_errors(repository_root: Path) -> dict[str, tuple[str, ...]]:
    root = repository_root / "catalog/sources"
    errors: dict[str, tuple[str, ...]] = {}
    task_files = sorted(root.rglob("task.toml"))
    for path in task_files:
        if any(
            (parent / "task.toml").is_file()
            for parent in path.parent.parents
            if parent != root and parent.is_relative_to(root)
        ):
            continue
        relative = path.relative_to(repository_root).as_posix()
        try:
            payload = tomllib.loads(path.read_text(encoding="utf-8"))
            TaskSource.model_validate(payload)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            errors[relative] = (str(exc),)
        except ValidationError as exc:
            errors[relative] = tuple(
                ".".join(str(part) for part in item["loc"]) + ": " + str(item["msg"])
                for item in exc.errors(include_url=False)
            )
    return errors


def canonical_source_gaps(repository_root: Path) -> tuple[str, ...]:
    return tuple(canonical_source_errors(repository_root))


def validate_private_staging_contract(path: Path) -> tuple[str, ...]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return (f"private staging contract is not valid JSON: {exc}",)
    errors: list[str] = []
    if not isinstance(payload, dict) or set(payload) != TOP_LEVEL_KEYS:
        return ("private staging contract has unexpected top-level fields",)
    if (
        not isinstance(payload["schema_version"], str)
        or payload["schema_version"] != CONTRACT_SCHEMA_VERSION
    ):
        errors.append("schema_version must be exactly 1.0")
    if not isinstance(payload["contract_id"], str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9._-]{1,127}", payload["contract_id"]
    ):
        errors.append("contract_id is invalid")
    if payload["purpose"] != "ephemeral-private-artifact-staging":
        errors.append("purpose is invalid")
    roots = payload["staging_roots"]
    if not isinstance(roots, dict) or set(roots) != ROOT_KEYS:
        errors.append("staging_roots must contain exactly dependency, oracle, test, verifier")
    else:
        for name, root in roots.items():
            if not isinstance(root, dict) or set(root) != ROOT_FIELDS:
                errors.append(f"staging_roots.{name} has unexpected fields")
                continue
            if (
                root["ephemeral"] is not True
                or root["mode"] != "0700"
                or type(root["uid"]) is not int
                or root["uid"] != ROOT_OWNER_UID
                or type(root["gid"]) is not int
                or root["gid"] != ROOT_OWNER_GID
            ):
                errors.append(
                    f"staging_roots.{name} must be ephemeral mode 0700 owned by "
                    f"uid/gid {ROOT_OWNER_UID}/{ROOT_OWNER_GID}"
                )
            path = root["path"]
            safe_path = (
                isinstance(path, str)
                and RELATIVE_PATH.fullmatch(path) is not None
                and path.startswith(".nl2repo/")
                and all(part not in {"", ".", ".."} for part in path.split("/"))
            )
            if not safe_path:
                errors.append(
                    f"staging_roots.{name}.path must be a safe repository-relative .nl2repo path"
                )
        paths = [
            root["path"]
            for root in roots.values()
            if isinstance(root, dict) and isinstance(root.get("path"), str)
        ]
        if len(paths) != len(set(paths)):
            errors.append("staging_roots paths must be unique")
    if (
        not isinstance(payload["allowed_artifact_kinds"], list)
        or payload["allowed_artifact_kinds"] != sorted(ARTIFACT_KINDS)
    ):
        errors.append("allowed_artifact_kinds must list each supported kind exactly once")
    artifact_kind_roots = payload["artifact_kind_roots"]
    if (
        not isinstance(artifact_kind_roots, dict)
        or artifact_kind_roots != ARTIFACT_ROOTS
    ):
        errors.append(
            "artifact_kind_roots must exactly bind each artifact kind to its staging root"
        )
    authorization = payload["authorization"]
    if not isinstance(authorization, dict) or set(authorization) != set(AUTHORIZATION):
        errors.append("authorization fields are invalid")
    elif authorization != AUTHORIZATION:
        errors.append("authorization binding is invalid")
    limits = payload["limits"]
    if not isinstance(limits, dict) or set(limits) != ARTIFACT_KINDS:
        errors.append("limits must cover exactly the supported artifact kinds")
    else:
        for kind, value in limits.items():
            if not isinstance(value, dict) or set(value) != LIMIT_FIELDS:
                errors.append(f"limits.{kind} fields are invalid")
                continue
            max_members, max_member_bytes, max_total_bytes = LIMITS[kind]
            if (
                value["max_members"],
                value["max_member_bytes"],
                value["max_total_bytes"],
                value["max_path_bytes"],
            ) != (max_members, max_member_bytes, max_total_bytes, 255):
                errors.append(f"limits.{kind} exceeds or changes the hard ceiling")
    lanes = payload["lanes"]
    if not isinstance(lanes, dict) or set(lanes) != LANES:
        errors.append("lanes must contain exactly the supported runtime/package-manager identities")
    else:
        for lane, value in lanes.items():
            if not isinstance(value, dict) or set(value) != LANE_FIELDS:
                errors.append(f"lanes.{lane} fields are invalid")
                continue
            if (
                not isinstance(value["allowed_artifact_kinds"], list)
                or value["allowed_artifact_kinds"] != sorted(ARTIFACT_KINDS)
                or value["artifact_kind_roots"] != ARTIFACT_ROOTS
                or value["offline_smoke_command_id"] != SMOKE_IDS[lane]
            ):
                errors.append(f"lanes.{lane} artifact, root, or offline smoke binding is invalid")
            binding = value["toolchain_binding"]
            if binding != TOOLCHAIN_BINDING:
                errors.append(f"lanes.{lane}.toolchain_binding is invalid")
    lifetime = payload["lifetime"]
    if lifetime != LIFETIME:
        errors.append("lifetime policy is invalid")
    receipt = payload["audit_receipt"]
    if receipt != AUDIT_RECEIPT:
        errors.append("audit_receipt policy is invalid")
    return tuple(errors)


def check(repository_root: Path) -> dict[str, object]:
    violations = scan_runtime(repository_root)
    source_errors = canonical_source_errors(repository_root)
    source_gaps = tuple(source_errors)
    staging_contract = repository_root / CONTRACT_PATH
    if not staging_contract.is_file():
        blockers = ["private-staging-contract-missing"]
        contract_errors: tuple[str, ...] = ()
    else:
        contract_errors = validate_private_staging_contract(staging_contract)
        blockers = ["private-staging-contract-invalid"] if contract_errors else []
    return {
        "schema_version": "1.0",
        "passed": not violations and not source_gaps and not blockers,
        "blockers": blockers,
        "runtime_violations": [asdict(item) for item in violations],
        "source_migration_gaps": list(source_gaps),
        "source_migration_errors": {
            path: list(messages) for path, messages in source_errors.items()
        },
        "private_staging_contract": str(staging_contract.relative_to(repository_root)),
        "private_staging_contract_errors": list(contract_errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    report = check(args.repository_root.resolve())
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
