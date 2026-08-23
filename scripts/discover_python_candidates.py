#!/usr/bin/env python3
"""Fetch auditable PyPI/GitHub evidence for a bounded Python candidate batch."""

from __future__ import annotations

import argparse
import json
import subprocess
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RISKY_PACKAGES = {
    "requests": ["network"],
    "boto3": ["cloud", "network", "credentials"],
    "botocore": ["cloud", "network", "credentials"],
    "google-auth": ["cloud", "credentials", "network"],
    "google-cloud-storage": ["cloud", "network", "credentials"],
    "pymongo": ["database", "network"],
    "lxml": ["native"],
    "msgspec": ["native"],
    "numpy": ["native", "large"],
    "pandas": ["native", "large"],
    "scipy": ["native", "large"],
    "scikit-learn": ["native", "large"],
    "matplotlib": ["native", "gui"],
    "textual": ["terminal", "interactive"],
    "aiohttp": ["network", "native-optional"],
    "httpcore": ["network"],
    "urllib3": ["network"],
    "websockets": ["network"],
    "anyio": ["async", "timing"],
    "trio": ["async", "timing"],
}


def _get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "NL2RepoBench-authoring/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        value = json.loads(response.read())
    if not isinstance(value, dict):
        raise ValueError(f"JSON response is not an object: {url}")
    return value


def _repo_url(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("url")
    if not isinstance(value, str) or not value:
        return None
    value = value.removeprefix("git+").removesuffix(".git")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    return value.rstrip("/")


def _revision(repository: str) -> str | None:
    parsed = urllib.parse.urlparse(repository)
    if parsed.netloc.casefold() != "github.com":
        return None
    completed = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{parsed.path.strip('/')}.git", "HEAD"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    sha = (
        completed.stdout.split()[0]
        if completed.returncode == 0 and completed.stdout.split()
        else ""
    )
    return sha if len(sha) == 40 else None


def discover(package: str, observed_at: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(package, safe="")
    metadata = _get_json(f"https://pypi.org/pypi/{encoded}/json")
    info = metadata.get("info")
    if not isinstance(info, dict):
        raise ValueError(f"PyPI info missing: {package}")
    repository = _repo_url(
        info.get("project_urls", {}).get("Source")
        or info.get("project_urls", {}).get("Repository")
        or info.get("home_page")
    )
    if repository is None:
        raise ValueError(f"PyPI package has no upstream repository: {package}")
    releases = metadata.get("releases", {})
    latest = str(info.get("version") or "")
    files = releases.get(latest, []) if isinstance(releases, dict) else []
    upload_times = [item.get("upload_time_iso_8601") for item in files if isinstance(item, dict)]
    last_activity = max((value for value in upload_times if isinstance(value, str)), default=None)
    stats = _get_json(f"https://pypistats.org/api/packages/{encoded}/recent")
    data = stats.get("data") if isinstance(stats.get("data"), dict) else stats
    return {
        "package": package,
        "language": "python",
        "source_kind": "pypi",
        "upstream_url": repository,
        "revision": _revision(repository),
        "license_spdx": info.get("license"),
        "license_evidence": f"https://pypi.org/project/{encoded}/",
        "last_activity": last_activity,
        "monthly_downloads": data.get("last_month") if isinstance(data, dict) else None,
        "latest_version": latest,
        "observed_at": observed_at,
        "test_evidence": "requires source-freeze AST/test inventory",
        "risk_flags": RISKY_PACKAGES.get(package, []),
        "status": "needs-evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--observed-at", default=datetime.now(UTC).isoformat())
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(discover, package, args.observed_at): package
            for package in args.package
        }
        for future in as_completed(futures):
            package = futures[future]
            try:
                records.append(future.result())
            except Exception as exc:  # noqa: BLE001 - preserve candidate-specific evidence gap
                errors.append({"package": package, "error": f"{type(exc).__name__}: {exc}"})
    records.sort(key=lambda item: item["package"].casefold())
    report = {
        "schema_version": "1.0",
        "report_id": "python-production-discovery-" + args.observed_at[:10],
        "observed_at": args.observed_at,
        "language": "python",
        "threshold": {"max_activity_months": 36, "min_monthly_downloads": 1000},
        "candidates": records,
        "errors": sorted(errors, key=lambda item: item["package"].casefold()),
        "next_stage": "source-freeze-and-ast-test-inventory",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"output": str(args.output), "candidates": len(records), "errors": len(errors)},
            sort_keys=True,
        )
    )
    return 0 if records else 1


if __name__ == "__main__":
    raise SystemExit(main())
