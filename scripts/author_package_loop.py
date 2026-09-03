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
from datetime import UTC, datetime
from pathlib import Path
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
    "storage": {
        "large_artifacts": "project-disk-only",
        "preferred_root": ".nl2repo/authoring-work/",
        "tmpfs_policy": "small bounded process scratch only; clean after each stage",
        "max_tmpfs_bytes": 256 * 1024 * 1024,
    },
}


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


def _candidate_records(path: Path, language: str) -> list[dict[str, Any]]:
    payload = _json(path)
    records = payload.get("queue") or payload.get("candidates")
    if not isinstance(records, list):
        raise ValueError("candidate input requires queue or candidates")
    result = [
        record
        for record in records
        if isinstance(record, dict)
        and record.get("language") == language
        and record.get("status") in {"candidate", "needs-evidence"}
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
    if record.get("status") != "candidate":
        reasons.append("candidate-evidence-incomplete")
    risk_flags = record.get("risk_flags") or []
    if risk_flags:
        reasons.append("risk-adaptation-required:" + ",".join(risk_flags))
    return reasons


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
    for record in _candidate_records(candidate_path, language):
        package = str(record.get("package", ""))
        if packages is not None and package not in packages:
            continue
        if package in existing_catalog:
            skipped.append({"package": package, "reason": "catalog-task-exists"})
            continue
        if package in existing_oss:
            skipped.append({"package": package, "reason": "oss-run-exists"})
            continue
        selected.append(record)
        if len(selected) >= limit:
            break
    batch_id = batch_id or f"{language}-author-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    tasks = []
    for record in selected:
        candidate_id = str(record.get("candidate_id") or record.get("package"))
        remediation_reasons = _remediation_reasons(record)
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
                    else (
                        "Go locked toolchain, API/test inventory, offline module closure, "
                        "typed bridge, Harbor compile, verifier build, Oracle once, "
                        "controls, review"
                        if language == "go"
                        else (
                            "Java JDK 21/Maven 3.9 locked toolchain, POM/API/test inventory, "
                            "offline Maven closure, verifier-owned JUnit report, Harbor compile, "
                            "verifier build, Oracle once, controls, review"
                            if language == "java"
                            else (
                                "Python locked toolchain, AST/test inventory, active remediation, "
                                "Harbor gates, review"
                            )
                        )
                    )
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
        "remediation_policy": REMEDIATION_POLICY,
        "worker_guidance": "docs/authoring-agent-remediation-guide.zh-CN.md",
        "agent_run_loop": "separate downstream consumer; not executed by this plan",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--language", choices=("python", "node", "go", "java"), required=True)
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/sources"))
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
