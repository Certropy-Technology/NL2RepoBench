#!/usr/bin/env python3
"""Normalize discovery reports into independent Package queue records.

This stage never creates a Harbor task and never upgrades a candidate to
publishable.  It only merges heterogeneous PyPI/npm/GitHub discovery reports,
deduplicates them against the catalog, and marks missing evidence so workers
can claim one Package at a time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SHA_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid discovery report {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"discovery report root must be an object: {path}")
    return value


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _months_old(observed: datetime, activity: datetime) -> int:
    months = (observed.year - activity.year) * 12 + observed.month - activity.month
    if observed.day < activity.day:
        months -= 1
    return months


def _repo_url(raw: Any) -> str | None:
    if not isinstance(raw, str) or not raw:
        return None
    if raw.startswith("https://"):
        return raw.rstrip("/")
    repository = raw.strip("/")
    return f"https://github.com/{repository}"


def _source_kind(report: Path, raw: dict[str, Any]) -> str:
    explicit = raw.get("source_kind") or raw.get("ecosystem") or raw.get("language")
    if isinstance(explicit, str):
        folded = explicit.casefold()
        if folded in {"npm", "node", "javascript", "typescript"}:
            return "npm"
        if folded in {"pypi", "python"}:
            return "pypi"
        if folded == "github":
            return "github"
    name = report.name.casefold()
    if "npm" in name or "node" in name:
        return "npm"
    if "github" in name:
        return "github"
    return "pypi"


def _merge_records(report: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    source_kind = _source_kind(report, payload)
    report_language = payload.get("language")
    if report_language not in {"python", "node"}:
        report_language = (
            "python"
            if "python" in str(payload.get("dataset_target", "")).casefold()
            else None
        )
    merged: dict[str, dict[str, Any]] = {}

    def absorb(raw: Any, *, shape: str) -> None:
        if not isinstance(raw, dict):
            return
        package = raw.get("package") or raw.get("task_id") or raw.get("name")
        repository = _repo_url(raw.get("repository") or raw.get("upstream_url"))
        if not isinstance(package, str) or not package.strip():
            return
        identity = repository or f"{source_kind}:{package.casefold()}"
        record = merged.setdefault(
            identity,
            {
                "candidate_id": (
                    f"{_slug(identity)}-"
                    f"{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:12]}"
                ),
                "package": package,
                "language": (
                    str(raw.get("language"))
                    if raw.get("language") in {"python", "node"}
                    else (
                        "node"
                        if source_kind == "npm"
                        else "python"
                        if source_kind == "pypi"
                        else report_language
                        if report_language is not None
                        else "unknown"
                    )
                ),
                "source_kind": source_kind,
                "upstream_url": repository,
                "identity": identity,
                "selection_sources": [],
                "risk_flags": [],
                "conflicts": [],
                "status": "needs-evidence",
            },
        )
        record["selection_sources"].append(
            {
                "report": str(report),
                "shape": shape,
                "report_sha256": "sha256:" + hashlib.sha256(report.read_bytes()).hexdigest(),
            }
        )
        field_aliases = {
            "revision": ("revision", "commit", "sha"),
            "license_spdx": ("license_spdx", "license"),
            "license_evidence": ("license_evidence", "license_url"),
            "last_activity": (
                "last_activity",
                "last_update_at_discovery",
                "last_push",
                "commit_date",
            ),
            "stars": ("stars", "stars_observed", "stars_at_discovery"),
            "monthly_downloads": ("monthly_downloads", "downloads", "monthly_download"),
            "category": ("category",),
            "difficulty": ("difficulty",),
            "source_sloc": ("source_sloc",),
            "test_files": ("test_files",),
            "test_count": ("static_test_defs", "test_count", "tests"),
        }
        for target, aliases in field_aliases.items():
            for alias in aliases:
                value = raw.get(alias)
                if value is None:
                    continue
                if target not in record:
                    record[target] = value
                    break
                if record[target] != value:
                    record["conflicts"].append(target)
                    values = (record[target], value)
                    record[target] = min(
                        values,
                        key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True),
                    )
                    break
        risks = raw.get("risks") or raw.get("offline_risk") or raw.get("risk_flags")
        if isinstance(risks, list):
            record["risk_flags"].extend(str(value) for value in risks)
        elif isinstance(risks, str):
            record["risk_flags"].append(risks)
        reason = raw.get("reason")
        if isinstance(reason, str) and reason:
            record.setdefault("notes", []).append(reason)

    for raw in payload.get("candidates", []):
        absorb(raw, shape="candidates")
    for raw in payload.get("shortlist", []):
        absorb(raw, shape="shortlist")
    for raw in payload.get("deep_validation", []):
        absorb(raw, shape="deep_validation")
    return list(merged.values())


def _status(record: dict[str, Any], existing_ids: set[str], observed_at: str) -> str:
    package = str(record["package"])
    repository = record.get("upstream_url")
    normalized = {_slug(package), _slug(str(repository or ""))}
    if package in existing_ids or normalized.intersection({_slug(item) for item in existing_ids}):
        return "existing"
    if record.get("language") not in {"python", "node"}:
        return "needs-evidence"
    revision = record.get("revision")
    license_spdx = record.get("license_spdx")
    last_activity = record.get("last_activity")
    stars = record.get("stars")
    downloads = record.get("monthly_downloads")
    if not isinstance(repository, str) or not repository.startswith("https://"):
        return "needs-evidence"
    if not isinstance(revision, str) or SHA_PATTERN.fullmatch(revision) is None:
        return "needs-evidence"
    if not isinstance(license_spdx, str) or not license_spdx.strip() or license_spdx.casefold() in {
        "unknown",
        "unresolved",
        "noassertion",
    }:
        return "needs-evidence"
    if not isinstance(last_activity, str):
        return "needs-evidence"
    try:
        activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
    except ValueError:
        return "needs-evidence"
    observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    activity = activity.replace(tzinfo=activity.tzinfo or UTC)
    observed = observed.replace(tzinfo=observed.tzinfo or UTC)
    if _months_old(observed, activity) > 36:
        return "rejected"
    if stars is None and downloads is None:
        return "needs-evidence"
    if stars is not None and not isinstance(stars, int):
        return "needs-evidence"
    if downloads is not None and not isinstance(downloads, int):
        return "needs-evidence"
    if (stars or 0) < 100 and (downloads or 0) < 1_000:
        return "rejected"
    return "candidate"


def build_queue(
    reports: list[Path],
    *,
    catalog_root: Path,
    observed_at: str,
) -> dict[str, Any]:
    existing_ids = {
        path.name
        for path in catalog_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    } if catalog_root.is_dir() else set()
    records: dict[str, dict[str, Any]] = {}
    for report in sorted(reports):
        for record in _merge_records(report, _load(report)):
            identity = str(record["candidate_id"])
            if identity not in records:
                records[identity] = record
            else:
                current = records[identity]
                current["selection_sources"].extend(record["selection_sources"])
                current["risk_flags"] = sorted(
                    set(current.get("risk_flags", [])) | set(record.get("risk_flags", []))
                )
                current["conflicts"] = sorted(
                    set(current.get("conflicts", [])) | set(record.get("conflicts", []))
                )
                for key, value in record.items():
                    if key in {"selection_sources", "risk_flags", "conflicts"}:
                        continue
                    if key not in current and value not in (None, [], ""):
                        current[key] = value
                    elif key in current and current[key] != value and value not in (None, [], ""):
                        current["conflicts"].append(key)
                        current[key] = min(
                            (current[key], value),
                            key=lambda item: json.dumps(
                                item, ensure_ascii=False, sort_keys=True
                            ),
                        )
                current["conflicts"] = sorted(set(current["conflicts"]))
    queue = []
    for record in sorted(
        records.values(),
        key=lambda item: (item["language"], item["package"].casefold(), item["candidate_id"]),
    ):
        record["selection_sources"] = sorted(
            record["selection_sources"], key=lambda item: (item["report"], item["shape"])
        )
        record["risk_flags"] = sorted(set(record.get("risk_flags", [])))
        record["observed_at"] = observed_at
        record["status"] = (
            "needs-evidence"
            if record.get("conflicts")
            else _status(record, existing_ids, observed_at)
        )
        queue.append(record)
    counts: dict[str, int] = {}
    for record in queue:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    return {
        "schema_version": "1.0",
        "queue_id": "package-discovery-" + observed_at[:10],
        "observed_at": observed_at,
        "threshold": {
            "max_activity_age_months": 36,
            "min_stars_or_monthly_downloads": {"stars": 100, "monthly_downloads": 1000},
        },
        "source_reports": [
            {
                "path": str(path),
                "sha256": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted(reports)
        ],
        "counts": dict(sorted(counts.items())),
        "queue": queue,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/sources"))
    parser.add_argument("--observed-at", default=datetime.now(UTC).isoformat())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        queue = build_queue(
            args.input,
            catalog_root=args.catalog_root,
            observed_at=args.observed_at,
        )
    except (OSError, ValueError) as exc:
        print(f"candidate queue failed: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(queue, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "candidate_count": len(queue["queue"]),
                "counts": queue["counts"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
