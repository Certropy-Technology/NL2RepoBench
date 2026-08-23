#!/usr/bin/env python3
"""Audit catalog task lifecycle reasons without mutating task sources.

The catalog is the source of truth.  This command intentionally produces a
report and fails closed for repairable blockers; changing a task to
``excluded`` or ``published`` still requires the task-local evidence and the
integrator's single-writer handoff.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

REPAIRABLE_TERMS = (
    "python",
    "node",
    "npm",
    "dependency",
    "dependenc",
    "install",
    "build",
    "docker",
    "image",
    "verifier",
    "environment",
    "offline",
    "timeout",
    "collection",
    "fixture",
    "package",
    "lock",
    "version",
    "revision",
    "drift",
    "mismatch",
    "does not match",
    "source/test",
)
EXCLUSION_TERMS = (
    "license is unclear",
    "license is unknown",
    "license is unresolved",
    "license cannot be verified",
    "licence is unclear",
    "licence is unknown",
    "licence is unresolved",
    "paid",
    "subscription",
    "external service",
    "cannot freeze",
    "unavailable revision",
    "resource budget",
    "hardware",
)
NO_TEST_PATTERNS = (
    re.compile(r"\bno (?:usable |executable |official )?tests?\b", re.I),
    re.compile(r"\btests? (?:are )?(?:missing|absent|unavailable)\b", re.I),
    re.compile(r"\btest suite (?:is )?(?:missing|absent|unavailable)\b", re.I),
)


def _load_source(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if path.is_symlink():
        return None, "task.toml must not be a symlink"
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return None, f"invalid TOML: {exc}"
    return payload, None


def _reason_kind(reason: str) -> str:
    folded = reason.casefold()
    for marker in (
        "publication is blocked because",
        "publication remains blocked because",
        "blocked because",
        "blockers before",
    ):
        if marker in folded:
            folded = folded.split(marker, 1)[1]
            break
    if any(pattern.search(reason) for pattern in NO_TEST_PATTERNS):
        return "no-tests"
    if any(term in folded for term in EXCLUSION_TERMS):
        return "eligibility-exclusion"
    if any(term in folded for term in REPAIRABLE_TERMS):
        return "repairable"
    return "unclassified"


def _document_blocker(task_dir: Path) -> tuple[list[str], str] | None:
    documents: list[str] = []
    reasons: list[str] = []
    for path in sorted(task_dir.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(task_dir).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not re.search(
            r"(?im)^\s*(?:\*\*)?status(?:\*\*)?\s*[:=]\s*[`\"]?blocked\b",
            text,
        ):
            continue
        documents.append(path.relative_to(task_dir).as_posix())
        folded = text.casefold()
        for marker in (
            "publication is blocked because",
            "publication remains blocked because",
            "blocked because",
            "blockers before",
        ):
            index = folded.find(marker)
            if index >= 0:
                reasons.append(text[index : index + 600].replace("\n", " ").strip())
                break
        if not reasons:
            first_line = text.splitlines()[0].strip() if text.splitlines() else "blocked document"
            reasons.append(first_line)
    if not documents:
        return None
    return documents, " ".join(reasons)


def _lifecycle_errors(status: str, lifecycle: dict[str, Any], reason_kind: str) -> list[str]:
    errors: list[str] = []
    if status in {"blocked", "excluded", "published"}:
        for field in ("owner", "evidence", "approval_refs"):
            value = lifecycle.get(field)
            if not value:
                errors.append(f"missing lifecycle.{field}")
    if status == "blocked" and reason_kind != "no-tests":
        errors.append("blocked status is reserved for no-test tasks")
    if status == "excluded" and reason_kind != "eligibility-exclusion":
        errors.append("excluded status requires an eligibility-exclusion reason")
    return errors


def reconcile(catalog_root: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    if catalog_root.is_symlink() or not catalog_root.is_dir():
        raise ValueError(f"catalog root does not exist: {catalog_root}")

    for task_dir in sorted(path for path in catalog_root.iterdir() if path.is_dir()):
        if task_dir.name.startswith("."):
            continue
        if task_dir.is_symlink():
            raise ValueError(f"catalog task directory must not be a symlink: {task_dir}")
        source_path = task_dir / "task.toml"
        blocker_document = _document_blocker(task_dir)
        blocked_docs = blocker_document[0] if blocker_document else []
        if not source_path.is_file():
            if not blocked_docs:
                record = {
                    "task_id": task_dir.name,
                    "status": "untracked-source",
                    "reason_kind": "unclassified",
                    "reason": "catalog task directory has no task.toml",
                    "blocked_docs": [],
                    "integrity_errors": ["missing authoritative task.toml"],
                }
                records.append(record)
                counts[record["reason_kind"]] = counts.get(record["reason_kind"], 0) + 1
                continue
            if blocked_docs:
                reason = blocker_document[1]
                reason_kind = _reason_kind(reason)
                record = {
                    "task_id": task_dir.name,
                    "status": "untracked-blocked",
                    "reason_kind": reason_kind,
                    "reason": reason,
                    "blocked_docs": blocked_docs,
                    "integrity_errors": [
                        "blocked document has no authoritative task.toml",
                        "missing lifecycle.owner",
                        "missing lifecycle.evidence",
                        "missing lifecycle.approval_refs",
                    ],
                }
                records.append(record)
                counts[record["reason_kind"]] = counts.get(record["reason_kind"], 0) + 1
            continue
        source, parse_error = _load_source(source_path)
        if parse_error:
            record = {
                "task_id": task_dir.name,
                "status": "invalid-source",
                "reason_kind": "unclassified",
                "reason": parse_error,
                "source": str(source_path),
            }
            records.append(record)
            counts[record["reason_kind"]] = counts.get(record["reason_kind"], 0) + 1
            continue
        lifecycle = source.get("lifecycle")
        lifecycle_is_table = isinstance(lifecycle, dict)
        lifecycle = lifecycle if lifecycle_is_table else {}
        status = str(lifecycle.get("status") or "")
        reason = str(lifecycle.get("reason") or "")
        if blocker_document and not reason:
            reason = blocker_document[1]
        reason_kind = _reason_kind(reason)
        valid_statuses = {
            "discovered",
            "frozen",
            "inventoried",
            "specified",
            "packaged",
            "oracle-passed",
            "controls-passed",
            "reviewed",
            "piloted",
            "published",
            "blocked",
            "excluded",
        }
        lifecycle_errors: list[str] = []
        if not lifecycle_is_table:
            lifecycle_errors.append("missing lifecycle table")
        elif status not in valid_statuses:
            lifecycle_errors.append(f"invalid lifecycle.status: {status or '<missing>'}")
        if blocker_document and status != "blocked":
            lifecycle_errors.append("blocked evidence document disagrees with lifecycle.status")
        if status in {"blocked", "excluded", "published"}:
            lifecycle_errors.extend(_lifecycle_errors(status, lifecycle, reason_kind))
        if not lifecycle_errors and status not in {"blocked", "excluded"} and not blocker_document:
            continue
        reason_kind = _reason_kind(reason)
        record = {
            "task_id": task_dir.name,
            "status": status,
            "reason_kind": reason_kind,
            "reason": reason,
            "blocked_docs": blocked_docs,
            "integrity_errors": lifecycle_errors,
            "source": str(source_path),
        }
        records.append(record)
        counts[reason_kind] = counts.get(reason_kind, 0) + 1

    return {
        "schema_version": "1.0",
        "catalog_root": str(catalog_root),
        "task_count": sum(1 for path in catalog_root.glob("*/task.toml") if path.is_file()),
        "record_count": len(records),
        "counts": dict(sorted(counts.items())),
        "records": records,
    }


def invalid_blockers(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in report["records"]
        if record.get("integrity_errors")
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/tasks"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        report = reconcile(args.catalog_root)
    except ValueError as exc:
        print(f"status reconciliation failed: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    invalid = invalid_blockers(report)
    if args.check and invalid:
        print(
            f"status check rejected {len(invalid)} non-test blockers; "
            "repair or explicitly exclude them",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
