#!/usr/bin/env python3
"""Refresh the mutable authoring candidate pool from bounded public indexes."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PYPI_TOP_URL = (
    "https://hugovk.github.io/top-pypi-packages/"
    "top-pypi-packages-30-days.min.json"
)
NPM_SEARCH_URL = "https://registry.npmjs.org/-/v1/search"
GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
NPM_QUERIES = ("keywords:utility", "keywords:parser", "keywords:cli")
GITHUB_QUERIES = (
    "language:go stars:200..5000 archived:false fork:false "
    "pushed:>=2024-01-01 size:<10000",
    "language:go stars:50..199 archived:false fork:false "
    "pushed:>=2025-01-01 size:<5000",
)
PACKAGE_PATTERN = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*|"
    r"@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)$"
)
GO_PACKAGE_PATTERN = re.compile(r"^go-[a-z0-9][a-z0-9-]*$")
REPOSITORY_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
)


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _get_json(url: str, *, github: bool = False) -> dict[str, Any]:
    headers = {"User-Agent": "NL2RepoBench-candidate-pool/1.0"}
    if github:
        headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                value = json.loads(response.read())
            if not isinstance(value, dict):
                raise ValueError(f"JSON response is not an object: {url}")
            return value
        except urllib.error.HTTPError as exc:
            if exc.code != 429 and not 500 <= exc.code < 600:
                raise
            if attempt == 3:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
            time.sleep(min(delay, 30))
    raise AssertionError("unreachable")


def _python_candidates(limit: int) -> list[str]:
    payload = _get_json(PYPI_TOP_URL)
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("PyPI top-package index has no rows list")
    names: list[str] = []
    for row in rows:
        name = row.get("project") if isinstance(row, dict) else None
        if isinstance(name, str) and PACKAGE_PATTERN.fullmatch(name):
            names.append(name)
        if len(names) >= limit:
            break
    return names


def _node_candidates(limit: int) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    per_query = min(250, max(25, limit))
    for query in NPM_QUERIES:
        url = NPM_SEARCH_URL + "?" + urllib.parse.urlencode(
            {"text": query, "size": per_query, "quality": 0.8, "popularity": 0.9}
        )
        payload = _get_json(url)
        objects = payload.get("objects", [])
        if not isinstance(objects, list):
            continue
        for item in objects:
            package = item.get("package") if isinstance(item, dict) else None
            name = package.get("name") if isinstance(package, dict) else None
            links = package.get("links") if isinstance(package, dict) else None
            repository = links.get("repository") if isinstance(links, dict) else None
            if (
                isinstance(name, str)
                and PACKAGE_PATTERN.fullmatch(name)
                and isinstance(repository, str)
                and "github.com/" in repository.casefold()
                and name not in seen
            ):
                seen.add(name)
                names.append(name)
            if len(names) >= limit:
                return names
    return names


def _go_package(repository: str, used: set[str]) -> str | None:
    owner, name = repository.split("/", 1)
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    package = f"go-{slug}"
    if not GO_PACKAGE_PATTERN.fullmatch(package):
        return None
    if package in used:
        owner_slug = re.sub(r"[^a-z0-9]+", "-", owner.casefold()).strip("-")
        package = f"go-{owner_slug}-{slug}"
    return package if GO_PACKAGE_PATTERN.fullmatch(package) else None


def _go_candidates(limit: int) -> tuple[list[str], dict[str, str]]:
    packages: list[str] = []
    repositories: dict[str, str] = {}
    seen_repositories: set[str] = set()
    used_packages: set[str] = set()
    for query in GITHUB_QUERIES:
        url = GITHUB_SEARCH_URL + "?" + urllib.parse.urlencode(
            {"q": query, "sort": "stars", "order": "desc", "per_page": 100}
        )
        payload = _get_json(url, github=True)
        items = payload.get("items", [])
        if not isinstance(items, list):
            continue
        for item in items:
            repository = item.get("full_name") if isinstance(item, dict) else None
            if (
                not isinstance(repository, str)
                or not REPOSITORY_PATTERN.fullmatch(repository)
                or repository.casefold() in seen_repositories
            ):
                continue
            package = _go_package(repository, used_packages)
            if package is None:
                continue
            seen_repositories.add(repository.casefold())
            used_packages.add(package)
            repositories[package] = repository
            packages.append(package)
            if len(packages) >= limit:
                return packages, repositories
    return packages, repositories


def _valid_entries(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        item
        for item in value
        if isinstance(item, str) and PACKAGE_PATTERN.fullmatch(item)
    ]


def merge_pool(
    seed: dict[str, Any],
    current: dict[str, Any],
    discovered: dict[str, list[str]],
    go_repositories: dict[str, str],
    *,
    max_per_language: int,
) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "schema_version": "2.1",
        "purpose": "Mutable runtime candidate pool refreshed from bounded public indexes.",
        "refreshed_at": datetime.now(UTC).isoformat(),
    }
    for language in ("python", "node", "go"):
        values = {
            *_valid_entries(seed.get(language)),
            *_valid_entries(current.get(language)),
            *_valid_entries(discovered.get(language)),
        }
        merged[language] = sorted(values, key=str.casefold)[:max_per_language]
    mapping: dict[str, str] = {}
    for source in (
        seed.get("go_repositories"),
        current.get("go_repositories"),
        go_repositories,
    ):
        if not isinstance(source, dict):
            continue
        for package, repository in source.items():
            if (
                isinstance(package, str)
                and GO_PACKAGE_PATTERN.fullmatch(package)
                and isinstance(repository, str)
                and REPOSITORY_PATTERN.fullmatch(repository)
            ):
                mapping.setdefault(package, repository)
    merged["go_repositories"] = {
        package: mapping[package]
        for package in merged["go"]
        if package in mapping
    }
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-pool", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--limit-per-source", type=int, default=250)
    parser.add_argument("--max-per-language", type=int, default=500)
    args = parser.parse_args()
    if args.limit_per_source < 1 or args.max_per_language < args.limit_per_source:
        parser.error("pool limits are invalid")
    seed = _load_object(args.seed_pool)
    current = _load_object(args.output) if args.output.is_file() else {}
    discovered: dict[str, list[str]] = {"python": [], "node": [], "go": []}
    go_repositories: dict[str, str] = {}
    errors: list[dict[str, str]] = []
    for language, fetch in (
        ("python", lambda: _python_candidates(args.limit_per_source)),
        ("node", lambda: _node_candidates(args.limit_per_source)),
    ):
        try:
            discovered[language] = fetch()
        except Exception as exc:  # noqa: BLE001 - preserve source-specific failure
            errors.append({"source": language, "error": f"{type(exc).__name__}: {exc}"})
    try:
        discovered["go"], go_repositories = _go_candidates(args.limit_per_source)
    except Exception as exc:  # noqa: BLE001 - preserve source-specific failure
        errors.append({"source": "go", "error": f"{type(exc).__name__}: {exc}"})
    pool = merge_pool(
        seed,
        current,
        discovered,
        go_repositories,
        max_per_language=args.max_per_language,
    )
    _atomic_write(args.output, pool)
    report = {
        "schema_version": "1.0",
        "recorded_at": datetime.now(UTC).isoformat(),
        "output": str(args.output),
        "counts": {language: len(pool[language]) for language in discovered},
        "discovered": {language: len(values) for language, values in discovered.items()},
        "errors": errors,
    }
    _atomic_write(args.report, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if any(discovered.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
