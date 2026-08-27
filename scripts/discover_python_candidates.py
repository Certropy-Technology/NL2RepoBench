#!/usr/bin/env python3
"""Fetch auditable PyPI/GitHub evidence for a bounded Python candidate batch."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.error
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
    request = urllib.request.Request(
        url, headers={"User-Agent": "NL2RepoBench-authoring/1.0"}
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                value = json.loads(response.read())
            break
        except urllib.error.HTTPError as exc:
            if exc.code != 429 and not 500 <= exc.code < 600:
                raise
            if attempt == 4:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
            time.sleep(min(delay, 30))
    if not isinstance(value, dict):
        raise ValueError(f"JSON response is not an object: {url}")
    return value


def _repo_url(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("url")
    if not isinstance(value, str) or not value:
        return None
    value = value.removeprefix("git+")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    if value.startswith("http://github.com/"):
        value = "https://github.com/" + value.removeprefix("http://github.com/")
    parsed = urllib.parse.urlparse(value)
    if parsed.netloc.casefold() != "github.com":
        return None
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        return None
    return f"https://github.com/{parts[0]}/{parts[1].removesuffix('.git')}"


def _repository(info: dict[str, Any]) -> str | None:
    project_urls = info.get("project_urls")
    candidates: list[Any] = []
    if isinstance(project_urls, dict):
        preferred = sorted(
            project_urls,
            key=lambda key: (
                not any(
                    token in key.casefold()
                    for token in ("source", "repository", "repo", "code", "github")
                ),
                key.casefold(),
            ),
        )
        candidates.extend(project_urls[key] for key in preferred)
    candidates.append(info.get("home_page"))
    for value in candidates:
        repository = _repo_url(value)
        if repository is not None:
            return repository
    return None


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
    repository = _repository(info)
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
