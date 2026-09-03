#!/usr/bin/env python3
"""Fetch auditable GitHub evidence for bounded Java/Maven candidates.

Discovery only identifies immutable candidate inputs. It does not authorize a
Maven Central dependency fetch in a Harbor run and never upgrades a candidate
to a publishable task.
"""

# The discovery report contains intentionally compact literal payloads.
# ruff: noqa: E501

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from defusedxml import ElementTree

REPOSITORY = re.compile(r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<repository>[A-Za-z0-9_.-]+)$")
PACKAGE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
JAVA_PUBLIC = re.compile(
    r"(?m)^\s*public\s+(?:final\s+|abstract\s+)?(?:class|interface|enum|record)\s+([A-Za-z_$][A-Za-z0-9_$]*)"
)
JUNIT_TEST = re.compile(
    r"(?m)@(?:org\.junit\.jupiter\.api\.)?Test\b|\bvoid\s+test[A-Z_a-z0-9]*\s*\("
)
HARD_RISKS = frozenset(
    {
        "multi-module",
        "snapshot-version",
        "dynamic-version",
        "custom-build",
        "profiles",
        "maven-extension",
        "no-java-tests",
        "non-java-source",
    }
)


def _normalize_repository(value: str) -> str:
    normalized = value.strip().removeprefix("git+").removesuffix(".git")
    if normalized.startswith("git@github.com:"):
        normalized = normalized.removeprefix("git@github.com:")
    elif normalized.startswith("https://github.com/"):
        normalized = urllib.parse.urlparse(normalized).path.strip("/")
    match = REPOSITORY.fullmatch(normalized.strip("/"))
    if match is None:
        raise ValueError(f"Java discovery requires a GitHub owner/repository: {value}")
    return f"{match.group('owner')}/{match.group('repository')}"


def _default_package(repository: str) -> str:
    raw = repository.rsplit("/", 1)[1].casefold()
    value = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    if not value:
        raise ValueError(f"repository has no usable package name: {repository}")
    return f"java-{value}"


def _parse_seed(value: str) -> tuple[str, str]:
    raw = value.strip()
    if not raw or raw.startswith("#"):
        raise ValueError("empty Java discovery seed")
    if "=" in raw:
        package, repository = (part.strip() for part in raw.split("=", 1))
    else:
        repository = raw
        package = _default_package(_normalize_repository(repository))
    repository = _normalize_repository(repository)
    if PACKAGE.fullmatch(package) is None:
        raise ValueError(f"unsafe Java task package name: {package}")
    return package, repository


def _load_seeds(repositories: list[str], seed_files: list[Path]) -> list[tuple[str, str]]:
    values: dict[str, tuple[str, str]] = {}
    for raw in repositories:
        package, repository = _parse_seed(raw)
        values.setdefault(repository.casefold(), (package, repository))
    for path in seed_files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                package, repository = _parse_seed(line)
                values.setdefault(repository.casefold(), (package, repository))
    names: dict[str, str] = {}
    for package, repository in values.values():
        previous = names.setdefault(package, repository)
        if previous != repository:
            raise ValueError(f"Java discovery package collision: {package}")
    return sorted(values.values(), key=lambda item: (item[0], item[1].casefold()))


def _github_metadata(repository: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "NL2RepoBench-Java-discovery/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://api.github.com/repos/{repository}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read())
    if not isinstance(result, dict):
        raise ValueError(f"GitHub repository response is not an object: {repository}")
    return result


def _clone_repository(repository: str, target: Path) -> str:
    environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    command = [
        "git",
        "clone",
        "--depth",
        "1",
        "--no-tags",
        "--filter=blob:none",
        f"https://github.com/{repository}.git",
        str(target),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        env=environment,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git clone failed for {repository}: {(completed.stderr or completed.stdout)[-1000:]}"
        )
    revision = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
        env=environment,
    ).stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise ValueError(f"Git checkout did not resolve an immutable SHA: {repository}")
    return revision


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _pom_inspection(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size > 256 * 1024:
        return {"risk_flags": ["missing-or-oversized-pom"], "release": None}
    data = path.read_bytes()
    risks: set[str] = set()
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        return {"risk_flags": ["unsafe-pom-xml"], "release": None}
    try:
        root = ElementTree.fromstring(data)
    except Exception:
        return {"risk_flags": ["invalid-pom-xml"], "release": None}
    names = {_local_name(node.tag) for node in root.iter()}
    if "modules" in names:
        risks.add("multi-module")
    if {"build", "profiles", "extensions", "pluginRepositories"}.intersection(names):
        risks.add("custom-build")
    if "profiles" in names:
        risks.add("profiles")
    if "extensions" in names or (path.parent / ".mvn/extensions.xml").is_file():
        risks.add("maven-extension")
    text = data.decode("utf-8", errors="replace")
    if re.search(r"<version>\s*(?:LATEST|RELEASE)\s*</version>|<version>\s*[\[(]", text, re.I):
        risks.add("dynamic-version")
    if "-SNAPSHOT" in text.upper():
        risks.add("snapshot-version")
    release: int | None = None
    for node in root.iter():
        if _local_name(node.tag) in {"maven.compiler.release", "release"}:
            try:
                value = int((node.text or "").strip())
            except ValueError:
                continue
            if value in {8, 11, 17, 21}:
                release = value
            else:
                risks.add("unsupported-java-release")
    return {"risk_flags": sorted(risks), "release": release}


def _license_file(root: Path) -> Path | None:
    return next(
        (
            path
            for path in sorted(root.iterdir())
            if path.is_file() and path.name.casefold().startswith(("license", "copying", "notice"))
        ),
        None,
    )


def _license_spdx(metadata: dict[str, Any], path: Path | None) -> str | None:
    license_value = metadata.get("license")
    api_value = license_value.get("spdx_id") if isinstance(license_value, dict) else None
    if isinstance(api_value, str) and api_value.casefold() not in {"", "noassertion", "other"}:
        return api_value
    if path is None:
        return None
    text = path.read_text(encoding="utf-8", errors="replace").casefold()
    if "permission is hereby granted, free of charge" in text:
        return "MIT"
    if "apache license" in text and "version 2.0" in text:
        return "Apache-2.0"
    if "redistribution and use in source and binary forms" in text:
        return "BSD-3-Clause" if "neither the name" in text else "BSD-2-Clause"
    return None


def _inspect_checkout(root: Path) -> dict[str, Any]:
    pom = _pom_inspection(root / "pom.xml")
    java_files = sorted(path for path in root.rglob("*.java") if ".git" not in path.parts)
    test_files = [path for path in java_files if "test" in {part.casefold() for part in path.parts}]
    source_files = [path for path in java_files if path not in test_files]
    risks = set(pom["risk_flags"])
    if any(path.suffix != ".java" for path in root.rglob("*.kt")):
        risks.add("non-java-source")
    if not test_files:
        risks.add("no-java-tests")
    test_count = sum(
        len(JUNIT_TEST.findall(path.read_text(encoding="utf-8", errors="replace")))
        for path in test_files
    )
    if test_count == 0:
        risks.add("no-java-tests")
    public_symbols = sum(
        len(JAVA_PUBLIC.findall(path.read_text(encoding="utf-8", errors="replace")))
        for path in source_files
    )
    source_sloc = sum(
        1
        for path in source_files
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip() and not line.lstrip().startswith(("//", "*", "/*"))
    )
    return {
        "pom_release": pom["release"],
        "source_files": len(source_files),
        "source_sloc": source_sloc,
        "public_symbols": public_symbols,
        "test_files": len(test_files),
        "test_count": test_count,
        "risk_flags": sorted(risks),
        "profile_eligible": not bool(risks & HARD_RISKS),
        "license_file": _license_file(root).name if _license_file(root) else None,
    }


def discover(package: str, repository: str, observed_at: str, work_root: Path) -> dict[str, Any]:
    metadata = _github_metadata(repository)
    if metadata.get("archived") is True or metadata.get("fork") is True:
        raise ValueError(f"repository is archived or a fork: {repository}")
    work_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="java-discovery-", dir=work_root) as temporary:
        checkout = Path(temporary) / "source"
        revision = _clone_repository(repository, checkout)
        inspection = _inspect_checkout(checkout)
        license_path = _license_file(checkout)
        license_spdx = _license_spdx(metadata, license_path)
        license_name = license_path.name if license_path else None
    inspection.pop("license_file")
    tests = int(inspection["test_count"])
    difficulty = "hard" if tests >= 100 else "medium" if tests >= 20 else "easy"
    return {
        "package": package,
        "repository": repository,
        "language": "java",
        "source_kind": "maven",
        "upstream_url": f"https://github.com/{repository}",
        "revision": revision,
        "license_spdx": license_spdx,
        "license_evidence": (
            f"https://github.com/{repository}/blob/{revision}/{license_name}"
            if license_name
            else f"https://github.com/{repository}/tree/{revision}"
        ),
        "stars": metadata.get("stargazers_count"),
        "last_activity": metadata.get("pushed_at"),
        "category": "java-library",
        "difficulty": difficulty,
        "observed_at": observed_at,
        "test_evidence": (
            "static Java/POM inventory; source-freeze must run Maven offline collection"
        ),
        **inspection,
        "status": "needs-evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", action="append", default=[])
    parser.add_argument("--seed-file", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, default=Path(".nl2repo/java-discovery-work"))
    parser.add_argument("--observed-at", default=datetime.now(UTC).isoformat())
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not args.repository and not args.seed_file:
        parser.error("provide at least one --repository or --seed-file")
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    try:
        seeds = _load_seeds(args.repository, args.seed_file)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(discover, package, repository, args.observed_at, args.work_root): (
                package,
                repository,
            )
            for package, repository in seeds
        }
        for future in as_completed(futures):
            package, repository = futures[future]
            try:
                records.append(future.result())
            except Exception as exc:  # noqa: BLE001 - preserve candidate evidence
                errors.append(
                    {
                        "package": package,
                        "repository": repository,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
    records.sort(key=lambda item: item["package"])
    candidates = [record for record in records if record["profile_eligible"]]
    report = {
        "schema_version": "1.0",
        "report_id": "java-maven-discovery-" + args.observed_at[:10],
        "observed_at": args.observed_at,
        "language": "java",
        "source_kind": "maven",
        "selection_profile": {
            "name": "java-maven-single-module-v1",
            "hard_exclusion_flags": sorted(HARD_RISKS),
            "min_stars": 100,
            "max_activity_months": 36,
        },
        "candidates": candidates,
        "excluded": [record for record in records if not record["profile_eligible"]],
        "errors": sorted(errors, key=lambda item: item["package"]),
        "next_stage": "source-freeze-maven-lock-offline-store-and-junit-inventory",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"output": str(args.output), "candidates": len(candidates), "errors": len(errors)},
            sort_keys=True,
        )
    )
    return 0 if candidates else 1


if __name__ == "__main__":
    raise SystemExit(main())
