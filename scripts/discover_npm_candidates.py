#!/usr/bin/env python3
"""Fetch auditable npm/GitHub evidence for a bounded candidate batch."""

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
    "better-sqlite3": ["native", "database"],
    "esbuild": ["native", "build-tool"],
    "sharp": ["native", "platform-binary"],
    "axios": ["network"],
    "express": ["network", "server"],
    "fastify": ["network", "server"],
    "koa": ["network", "server"],
    "socket.io": ["network", "server"],
    "ws": ["network"],
    "undici": ["network"],
    "node-fetch": ["network"],
    "jsdom": ["browser-emulation", "network"],
    "execa": ["process"],
    "vite": ["build-tool", "native-optional"],
    "rollup": ["build-tool"],
    "typescript": ["build-tool", "large-suite"],
    "eslint": ["dynamic-loader", "build-tool"],
    "prettier": ["build-tool", "large-suite"],
}


def _get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "NL2RepoBench-authoring/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        value = json.loads(response.read())
    if not isinstance(value, dict):
        raise ValueError(f"JSON response is not an object: {url}")
    return value


def _repository_url(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("url")
    if not isinstance(value, str) or not value:
        return None
    value = value.removeprefix("git+").removesuffix(".git")
    if value.startswith("git://"):
        value = "https://" + value.removeprefix("git://")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    return value.rstrip("/")


def _github_revision(repository: str) -> str | None:
    parsed = urllib.parse.urlparse(repository)
    if parsed.netloc.casefold() != "github.com":
        return None
    owner_repo = parsed.path.strip("/")
    completed = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{owner_repo}.git", "HEAD"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        return None
    sha = completed.stdout.split()[0] if completed.stdout.split() else ""
    return sha if len(sha) == 40 else None


def discover(package: str, observed_at: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(package, safe="@/")
    metadata = _get_json(f"https://registry.npmjs.org/{encoded}")
    latest = metadata.get("dist-tags", {}).get("latest")
    info = metadata.get("versions", {}).get(latest, {}) if isinstance(latest, str) else {}
    if not isinstance(info, dict):
        info = {}
    repository = _repository_url(info.get("repository") or metadata.get("repository"))
    if repository is None:
        raise ValueError(f"npm metadata has no GitHub repository: {package}")
    time_map = metadata.get("time", {})
    published = time_map.get(latest) if isinstance(time_map, dict) else None
    downloads = _get_json(
        f"https://api.npmjs.org/downloads/point/last-month/{encoded}"
    )
    return {
        "package": package,
        "language": "node",
        "source_kind": "npm",
        "upstream_url": repository,
        "revision": _github_revision(repository),
        "license_spdx": info.get("license") or metadata.get("license"),
        "license_evidence": f"https://www.npmjs.com/package/{encoded}",
        "last_activity": published,
        "monthly_downloads": downloads.get("downloads"),
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
            except Exception as exc:  # noqa: BLE001 - record candidate-specific evidence gap
                errors.append({"package": package, "error": f"{type(exc).__name__}: {exc}"})
    records.sort(key=lambda item: item["package"].casefold())
    report = {
        "schema_version": "1.0",
        "report_id": "npm-production-discovery-" + args.observed_at[:10],
        "observed_at": args.observed_at,
        "language": "node",
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
