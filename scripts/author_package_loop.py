#!/usr/bin/env python3
"""Plan deterministic Raw Package -> Harbor authoring work for Pi agents.

This controller only creates a bounded batch manifest and source-freeze stage
artifacts. A worker owns one Package task directory; the integrator owns
shared datasets, toolchain locks, private artifacts, Oracle/control results,
and publication. Agent model runs are a separate downstream loop and are never
started by this authoring controller.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

STAGES = (
    "source-freeze",
    "ast-inventory",
    "test-inventory",
    "dependency-probe",
    "environment-remediation",
    "dependency-closure",
    "harbor-package",
    "verifier-build",
    "oracle-once",
    "controls",
    "review-handoff",
)

REMEDIATION_POLICY = {
    "missing_immutable_image_or_digest": "must-remediate",
    "missing_runtime_or_dev_pin": "must-remediate",
    "missing_hash_locked_offline_closure": "must-remediate",
    "missing_build_backend_or_dockerfile": "must-remediate",
    "risk_flags": "adapt-and-probe-before-decision",
    "automatic_block_only": [
        "no-executable-tests-after-remediation",
        "license-unclear-or-undistributable",
        "revision-cannot-be-frozen-after-fetch-attempts",
        "paid-or-unreproducible-external-service",
        "resource-budget-exceeded-after-bounded-probes",
    ],
    "blocked_requires": [
        "attempted_commands",
        "tool_versions",
        "exit_codes",
        "failure_logs",
        "failure_class",
        "next_unblock_action",
    ],
    "existing_source_repair": {
        "missing_harbor_task": "repair-source-and-regenerate",
        "incomplete_harbor_task": "repair-source-and-regenerate",
        "repairable_blocked_source": "reopen-with-structured-evidence",
        "manual_or_terminal_blocker": "keep-blocked",
    },
    "storage": {
        "large_artifacts": "project-disk-only",
        "preferred_root": ".nl2repo/authoring-work/",
        "tmpfs_policy": "small bounded process scratch only; clean after each stage",
        "max_tmpfs_bytes": 256 * 1024 * 1024,
    },
}

REQUIRED_HARBOR_FILES = frozenset(
    {
        "bundle.manifest.json",
        "environment/Dockerfile",
        "instruction.md",
        "solution/solve.sh",
        "task.toml",
        "tests/test.sh",
    }
)
REPAIRABLE_FAILURE_CLASSES = frozenset({"environment", "verifier", "infrastructure"})
REPAIRABLE_BLOCKED_TERMS = (
    "dependency closure",
    "dependency lock",
    "hash-locked",
    "offline closure",
    "offline install",
    "private artifact",
    "oracle bundle",
    "verifier bundle",
    "verifier entrypoint",
    "separate verifier",
    "production compile",
    "dockerfile",
    "image digest",
    "network policy",
    "oracle plus",
    "oracle and controls",
    "tool budget",
)
TERMINAL_BLOCKED_TERMS = (
    "license is unclear",
    "license is unknown",
    "license is unresolved",
    "license cannot be verified",
    "no executable tests",
    "no usable tests",
    "paid service",
    "paid external service",
    "subscription required",
    "cannot freeze",
    "cannot be frozen",
    "unavailable revision",
    "resource budget exceeded",
)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _oss_tasks(path: Path | None) -> set[str]:
    if path is None:
        return set()
    payload = _json(path)
    runs = payload.get("runs")
    if not isinstance(runs, list):
        raise ValueError("OSS inventory requires runs")
    return {
        str(run["task_id"])
        for run in runs
        if isinstance(run, dict) and run.get("source") == "oss" and run.get("task_id")
    }


def _candidate_records(
    path: Path,
    language: str,
    *,
    remediation: bool = False,
) -> list[dict[str, Any]]:
    payload = _json(path)
    records = payload.get("queue") or payload.get("candidates")
    if not isinstance(records, list):
        raise ValueError("candidate input requires queue or candidates")
    result = [
        record
        for record in records
        if isinstance(record, dict)
        and record.get("language") == language
        and record.get("status")
        in (
            {
                "candidate",
                "needs-evidence",
                "existing",
                "blocked",
                "needs-remediation",
            }
            if remediation
            else {"candidate", "needs-evidence"}
        )
    ]
    return sorted(
        result,
        key=lambda record: (
            str(record.get("package", "")).casefold(),
            str(record.get("candidate_id", "")),
        ),
    )


def _remediation_reasons(record: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if record.get("status") == "needs-evidence":
        reasons.append("candidate-evidence-incomplete")
    risk_flags = record.get("risk_flags") or []
    if risk_flags:
        reasons.append("risk-adaptation-required:" + ",".join(risk_flags))
    return reasons


def _source_lifecycle(source_root: Path) -> tuple[str, str]:
    descriptor = source_root / "task.toml"
    if not descriptor.is_file() or descriptor.is_symlink():
        return "missing", "task.toml is missing"
    try:
        source = tomllib.loads(descriptor.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return "invalid", f"invalid task.toml: {exc}"
    lifecycle = source.get("lifecycle")
    if not isinstance(lifecycle, dict):
        return "unknown", "lifecycle table is missing"
    return str(lifecycle.get("status") or "unknown"), str(lifecycle.get("reason") or "")


def _blocked_evidence(
    source_root: Path,
    record: dict[str, Any],
    lifecycle_reason: str,
) -> tuple[str, str, str]:
    failure_class = str(record.get("failure_class") or "")
    next_step = ""
    evidence_path = source_root / "production-evidence.json"
    if evidence_path.is_file() and not evidence_path.is_symlink():
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            evidence = None
        if isinstance(evidence, dict):
            blocked = evidence.get("blocked")
            if isinstance(blocked, dict):
                failure_class = str(blocked.get("failure_class") or failure_class)
                next_step = str(
                    blocked.get("next_step") or blocked.get("next_unblock_action") or ""
                )
    reason = str(record.get("reason") or lifecycle_reason)
    return failure_class.casefold(), next_step, reason


def _blocked_reason_kind(
    source_root: Path,
    record: dict[str, Any],
    lifecycle_reason: str,
) -> str:
    failure_class, next_step, reason = _blocked_evidence(source_root, record, lifecycle_reason)
    combined = f"{reason}\n{next_step}".casefold()
    if any(term in combined for term in TERMINAL_BLOCKED_TERMS):
        return "terminal"
    if failure_class in REPAIRABLE_FAILURE_CLASSES and next_step.strip():
        return "repairable"
    if not failure_class and any(term in combined for term in REPAIRABLE_BLOCKED_TERMS):
        return "repairable"
    return "manual"


def _harbor_bundle_state(task_root: Path) -> str:
    if not task_root.is_dir():
        return "missing"
    entries = list(task_root.rglob("*"))
    if any(path.is_symlink() for path in entries):
        return "incomplete"
    files = {path.relative_to(task_root).as_posix(): path for path in entries if path.is_file()}
    if not REQUIRED_HARBOR_FILES.issubset(files):
        return "incomplete"
    try:
        task = tomllib.loads(files["task.toml"].read_text(encoding="utf-8"))
        manifest = json.loads(files["bundle.manifest.json"].read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, json.JSONDecodeError):
        return "incomplete"
    if task.get("schema_version") != "1.4" or not isinstance(manifest, dict):
        return "incomplete"
    if manifest.get("mode") != "production" or manifest.get("schema_version") not in {
        "1.0",
        "2.0",
    }:
        return "incomplete"
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        return "incomplete"
    declared: dict[str, tuple[str, int]] = {}
    for row in rows:
        if not isinstance(row, dict):
            return "incomplete"
        relative = row.get("path")
        digest = row.get("sha256")
        size = row.get("size_bytes")
        if not isinstance(relative, str):
            return "incomplete"
        safe = PurePosixPath(relative)
        if safe.is_absolute() or ".." in safe.parts or relative in declared:
            return "incomplete"
        if not isinstance(digest, str) or len(digest) != 64:
            return "incomplete"
        try:
            int(digest, 16)
        except ValueError:
            return "incomplete"
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            return "incomplete"
        declared[relative] = (digest, size)
    actual = {
        relative: (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size)
        for relative, path in files.items()
        if relative != "bundle.manifest.json"
    }
    return "complete" if declared == actual else "incomplete"


def classify_existing_remediation(
    record: dict[str, Any],
    *,
    source_root: Path,
    task_root: Path,
) -> tuple[dict[str, Any] | None, str]:
    if not source_root.is_dir():
        return None, "source-missing"
    lifecycle_status, lifecycle_reason = _source_lifecycle(source_root)
    bundle_state = _harbor_bundle_state(task_root)
    reasons: list[str] = []
    blocker_kind: str | None = None
    if lifecycle_status == "excluded":
        return None, "source-excluded"
    if lifecycle_status == "blocked":
        blocker_kind = _blocked_reason_kind(source_root, record, lifecycle_reason)
        if blocker_kind != "repairable":
            return None, f"blocked-{blocker_kind}"
        reasons.append("blocked-source-repairable")
    elif lifecycle_status in {"missing", "invalid", "unknown"}:
        reasons.append("source-declaration-incomplete")
    if bundle_state == "missing":
        reasons.append("harbor-task-missing")
    elif bundle_state == "incomplete":
        reasons.append("harbor-task-incomplete")
    elif not reasons:
        return None, "harbor-task-complete"
    selected = dict(record)
    selected.update(
        {
            "source_present": True,
            "existing_source_status": lifecycle_status,
            "existing_source_reason": lifecycle_reason,
            "existing_harbor_task_state": bundle_state,
            "blocked_reason_kind": blocker_kind,
            "existing_task_remediation_reasons": sorted(set(reasons)),
            "queue_reclaim_statuses": ["blocked", "complete"],
        }
    )
    return selected, "selected"


def build_plan(
    candidate_path: Path,
    *,
    language: str,
    catalog_root: Path,
    oss_inventory: Path | None,
    limit: int,
    batch_id: str | None = None,
    allow_risk: bool = False,
    packages: set[str] | None = None,
    tasks_root: Path = Path("catalog/tasks"),
    remediation: bool = False,
) -> dict[str, Any]:
    if limit < 1:
        raise ValueError("limit must be positive")
    existing_catalog = (
        {
            path.name
            for path in catalog_root.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
        if catalog_root.is_dir()
        else set()
    )
    existing_oss = _oss_tasks(oss_inventory)
    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for record in _candidate_records(
        candidate_path,
        language,
        remediation=remediation,
    ):
        package = str(record.get("package", ""))
        if packages is not None and package not in packages:
            continue
        if not remediation and package in existing_catalog:
            skipped.append({"package": package, "reason": "catalog-task-exists"})
            continue
        if not remediation and package in existing_oss:
            skipped.append({"package": package, "reason": "oss-run-exists"})
            continue
        selected_record: dict[str, Any] | None = record
        if remediation:
            selected_record, skip_reason = classify_existing_remediation(
                record,
                source_root=catalog_root / package,
                task_root=tasks_root / package,
            )
            if selected_record is None:
                skipped.append({"package": package, "reason": skip_reason})
                continue
            selected_record["oss_run_exists"] = package in existing_oss
        assert selected_record is not None
        selected.append(selected_record)
        if len(selected) >= limit:
            break
    batch_id = batch_id or f"{language}-author-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    tasks = []
    for record in selected:
        candidate_id = str(record.get("candidate_id") or record.get("package"))
        remediation_reasons = _remediation_reasons(record)
        remediation_reasons.extend(record.get("existing_task_remediation_reasons", []))
        remediation_reasons = sorted(set(remediation_reasons))
        tasks.append(
            {
                "candidate_id": candidate_id,
                "package": record["package"],
                "language": language,
                "upstream_url": record.get("upstream_url"),
                "revision": record.get("revision"),
                "source_digest": record.get("source_digest"),
                "stages": list(STAGES),
                "remediation_policy": REMEDIATION_POLICY,
                "worker_guidance": "docs/authoring-agent-remediation-guide.zh-CN.md",
                "worker_boundary": f"catalog/sources/{record['package']}/** only",
                "remediation_required": bool(remediation_reasons),
                "remediation_reasons": remediation_reasons,
                "remediation_mode": remediation,
                "source_present": bool(record.get("source_present")),
                "source_root": record.get("source_root", f"catalog/sources/{record['package']}"),
                "harbor_task_root": record.get(
                    "harbor_task_root", f"catalog/tasks/{record['package']}"
                ),
                "existing_source_status": record.get("existing_source_status"),
                "existing_source_reason": record.get("existing_source_reason"),
                "existing_harbor_task_state": record.get("existing_harbor_task_state"),
                "blocked_reason_kind": record.get("blocked_reason_kind"),
                "queue_reclaim_statuses": record.get("queue_reclaim_statuses", []),
                "agent_run_boundary": (
                    "Authoring ends after Oracle/controls/review; downstream Agent Run Loop "
                    "consumes this catalog task and is not started here."
                ),
                "production_gate": (
                    (
                        "Node 24 locked toolchain, AST/test inventory, offline closure, "
                        "active remediation, Harbor compile, verifier build, Oracle once, "
                        "controls, review"
                    )
                    if language == "node"
                    else "Python locked toolchain, AST/test inventory, active remediation, "
                    "Harbor gates, review"
                ),
                "handoff_status": "authoring-in-progress",
            }
        )
    return {
        "schema_version": "1.0",
        "batch_id": batch_id,
        "language": language,
        "candidate_input": str(candidate_path),
        "candidate_input_sha256": "sha256:"
        + hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
        "oss_inventory": str(oss_inventory) if oss_inventory else None,
        "parallelism": {"workers": min(limit, 3), "shared_integrator_writers": 1},
        "stages": list(STAGES),
        "tasks": tasks,
        "skipped": skipped,
        "status": "planned",
        "risk_policy": "allow-risk" if allow_risk else "remediate-before-gate",
        "remediation_mode": remediation,
        "remediation_policy": REMEDIATION_POLICY,
        "worker_guidance": "docs/authoring-agent-remediation-guide.zh-CN.md",
        "agent_run_loop": "separate downstream consumer; not executed by this plan",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--language", choices=("python", "node"), required=True)
    parser.add_argument(
        "--source-root",
        "--catalog-root",
        dest="catalog_root",
        type=Path,
        default=Path("catalog/sources"),
    )
    parser.add_argument("--tasks-root", type=Path, default=Path("catalog/tasks"))
    parser.add_argument("--oss-inventory", type=Path)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--batch-id")
    parser.add_argument(
        "--package",
        action="append",
        dest="packages",
        help="Restrict authoring to one or more package names; repeatable.",
    )
    parser.add_argument("--allow-risk", action="store_true")
    parser.add_argument(
        "--remediation",
        action="store_true",
        help=(
            "Select existing sources whose production Harbor task is missing or "
            "incomplete, plus blocked sources with structured repairable evidence."
        ),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        plan = build_plan(
            args.candidates,
            language=args.language,
            catalog_root=args.catalog_root,
            oss_inventory=args.oss_inventory,
            limit=args.limit,
            batch_id=args.batch_id,
            allow_risk=args.allow_risk,
            packages=set(args.packages) if args.packages else None,
            tasks_root=args.tasks_root,
            remediation=args.remediation,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"authoring loop planning failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "selected": len(plan["tasks"]),
                "skipped": len(plan["skipped"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
