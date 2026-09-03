#!/usr/bin/env python3
"""Fetch auditable GitHub and source evidence for Go module candidates."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_PATTERN = re.compile(
    r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<repository>[A-Za-z0-9_.-]+)$"
)
PACKAGE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEST_PATTERN = re.compile(
    r"(?m)^func\s+(?:Test|Benchmark|Fuzz|Example)[A-Za-z0-9_]*\s*\("
)
EXPORTED_DECLARATION_PATTERN = re.compile(
    r"(?m)^(?:type|var|const)\s+([A-Z][A-Za-z0-9_]*)\b"
    r"|^func\s+(?:\([^\n)]*\)\s*)?([A-Z][A-Za-z0-9_]*)\s*\("
)
HARD_EXCLUSION_FLAGS = frozenset(
    {
        "cgo",
        "go-generate",
        "go-workspace",
        "local-replace",
        "missing-go-mod",
        "multi-module",
        "no-go-tests",
        "plugin",
    }
)


def _normalize_repository(value: str) -> str:
    normalized = value.strip().removeprefix("git+").removesuffix(".git")
    if normalized.startswith("git@github.com:"):
        normalized = normalized.removeprefix("git@github.com:")
    elif normalized.startswith("https://github.com/"):
        normalized = urllib.parse.urlparse(normalized).path.strip("/")
    match = REPOSITORY_PATTERN.fullmatch(normalized.strip("/"))
    if match is None:
        raise ValueError(f"Go discovery requires a GitHub owner/repository: {value}")
    return f"{match.group('owner')}/{match.group('repository')}"


def _default_package(repository: str) -> str:
    name = repository.rsplit("/", 1)[1].casefold()
    slug = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    if not slug:
        raise ValueError(f"repository has no usable package name: {repository}")
    return f"go-{slug}"


def _parse_seed(value: str) -> tuple[str, str]:
    raw = value.strip()
    if not raw or raw.startswith("#"):
        raise ValueError("empty Go discovery seed")
    if "=" in raw:
        package, repository = (part.strip() for part in raw.split("=", 1))
    else:
        repository = raw
        package = _default_package(_normalize_repository(repository))
    repository = _normalize_repository(repository)
    if PACKAGE_PATTERN.fullmatch(package) is None:
        raise ValueError(f"unsafe Go task package name: {package}")
    return package, repository


def _load_seeds(repositories: list[str], seed_files: list[Path]) -> list[tuple[str, str]]:
    seeds: dict[str, tuple[str, str]] = {}
    for raw in repositories:
        package, repository = _parse_seed(raw)
        seeds.setdefault(repository.casefold(), (package, repository))
    for path in seed_files:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            package, repository = _parse_seed(stripped)
            seeds.setdefault(repository.casefold(), (package, repository))
    packages: dict[str, str] = {}
    for package, repository in seeds.values():
        previous = packages.setdefault(package, repository)
        if previous != repository:
            raise ValueError(
                f"Go discovery package collision: {package} maps to {previous} and {repository}"
            )
    return sorted(seeds.values(), key=lambda item: (item[0], item[1].casefold()))


def _github_metadata(repository: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "NL2RepoBench-Go-discovery/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}", headers=headers
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        value = json.loads(response.read())
    if not isinstance(value, dict):
        raise ValueError(f"GitHub repository response is not an object: {repository}")
    return value


def _clone_repository(repository: str, target: Path) -> str:
    environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    url = f"https://github.com/{repository}.git"
    commands = (
        ["git", "clone", "--depth", "1", "--no-tags", "--filter=blob:none", url, str(target)],
        ["git", "clone", "--depth", "1", "--no-tags", url, str(target)],
    )
    errors: list[str] = []
    for command in commands:
        shutil.rmtree(target, ignore_errors=True)
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env=environment,
        )
        if completed.returncode == 0:
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
        errors.append((completed.stderr or completed.stdout).strip()[-1000:])
    raise RuntimeError(f"git clone failed for {repository}: {' | '.join(errors)}")


def _source_files(checkout: Path) -> list[Path]:
    return sorted(
        path
        for path in checkout.rglob("*.go")
        if ".git" not in path.parts and "vendor" not in path.parts
    )


def _license_file(checkout: Path) -> Path | None:
    candidates = sorted(
        path
        for path in checkout.iterdir()
        if path.is_file()
        and path.name.casefold().startswith(("license", "copying", "notice"))
    )
    return candidates[0] if candidates else None


def _license_spdx(metadata: dict[str, Any], license_path: Path | None) -> str | None:
    license_info = metadata.get("license")
    api_value = license_info.get("spdx_id") if isinstance(license_info, dict) else None
    if isinstance(api_value, str) and api_value.casefold() not in {
        "",
        "noassertion",
        "other",
    }:
        return api_value
    if license_path is None:
        return None
    text = license_path.read_text(encoding="utf-8", errors="replace").casefold()
    if "permission is hereby granted, free of charge" in text:
        return "MIT"
    if "apache license" in text and "version 2.0" in text:
        return "Apache-2.0"
    if "mozilla public license" in text and "version 2.0" in text:
        return "MPL-2.0"
    if "redistribution and use in source and binary forms" in text:
        return "BSD-3-Clause" if "neither the name" in text else "BSD-2-Clause"
    if "permission to use, copy, modify, and/or distribute" in text:
        return "ISC"
    if "this is free and unencumbered software released into the public domain" in text:
        return "Unlicense"
    return None


def _inspect_checkout(checkout: Path) -> dict[str, Any]:
    go_mods = sorted(
        path
        for path in checkout.rglob("go.mod")
        if ".git" not in path.parts and "vendor" not in path.parts
    )
    top_level_mod = checkout / "go.mod"
    go_mod_text = top_level_mod.read_text(encoding="utf-8") if top_level_mod.is_file() else ""
    module_match = re.search(r"(?m)^\s*module\s+(\S+)\s*$", go_mod_text)
    go_match = re.search(r"(?m)^\s*go\s+(\S+)\s*$", go_mod_text)
    toolchain_match = re.search(r"(?m)^\s*toolchain\s+(\S+)\s*$", go_mod_text)
    files = _source_files(checkout)
    test_files = [path for path in files if path.name.endswith("_test.go")]
    implementation_files = [path for path in files if not path.name.endswith("_test.go")]
    implementation_texts = [
        path.read_text(encoding="utf-8", errors="replace")
        for path in implementation_files
    ]
    test_texts = [path.read_text(encoding="utf-8", errors="replace") for path in test_files]
    risks: set[str] = set()
    if not top_level_mod.is_file():
        risks.add("missing-go-mod")
    if len(go_mods) > 1:
        risks.add("multi-module")
    if (checkout / "go.work").is_file():
        risks.add("go-workspace")
    if any('import "C"' in text for text in implementation_texts):
        risks.add("cgo")
    if any("//go:generate" in text for text in implementation_texts):
        risks.add("go-generate")
    if any(re.search(r'(?m)^\s*"plugin"\s*$', text) for text in implementation_texts):
        risks.add("plugin")
    if any(re.search(r'(?m)^\s*"unsafe"\s*$', text) for text in implementation_texts):
        risks.add("unsafe")
    if re.search(r"(?m)^\s*replace\s+.*=>\s+(?:\.|/)", go_mod_text):
        risks.add("local-replace")
    if re.search(r"(?m)^\s*replace\s+", go_mod_text):
        risks.add("replace-directive")
    if toolchain_match:
        risks.add("toolchain-directive")
    if any(
        re.search(r'(?m)^\s*"(?:net|net/http|database/sql|cloud\.google\.com/[^\"]+)"\s*$', text)
        for text in implementation_texts
    ):
        risks.add("network-or-external-io")
    test_count = sum(len(TEST_PATTERN.findall(text)) for text in test_texts)
    if test_count == 0:
        risks.add("no-go-tests")
    exported = {
        first or second
        for text in implementation_texts
        for first, second in EXPORTED_DECLARATION_PATTERN.findall(text)
    }
    source_sloc = sum(
        1
        for text in implementation_texts
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("//")
    )
    return {
        "module_path": module_match.group(1) if module_match else None,
        "go_version": go_match.group(1) if go_match else None,
        "toolchain": toolchain_match.group(1) if toolchain_match else None,
        "go_mod_files": len(go_mods),
        "source_files": len(implementation_files),
        "source_sloc": source_sloc,
        "public_symbols": len(exported),
        "test_files": len(test_files),
        "test_count": test_count,
        "risk_flags": sorted(risks),
        "profile_eligible": not bool(risks & HARD_EXCLUSION_FLAGS),
        "license_file": _license_file(checkout).name if _license_file(checkout) else None,
    }


def discover(
    package: str,
    repository: str,
    observed_at: str,
    work_root: Path,
) -> dict[str, Any]:
    metadata = _github_metadata(repository)
    if metadata.get("archived") is True:
        raise ValueError(f"repository is archived: {repository}")
    if metadata.get("fork") is True:
        raise ValueError(f"repository is a fork: {repository}")
    work_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="go-discovery-", dir=work_root) as temporary:
        checkout = Path(temporary) / "source"
        revision = _clone_repository(repository, checkout)
        inspection = _inspect_checkout(checkout)
        license_file = _license_file(checkout)
        license_spdx = _license_spdx(metadata, license_file)
        license_file_name = license_file.name if license_file else None
    inspection.pop("license_file")
    test_count = int(inspection["test_count"])
    public_symbols = int(inspection["public_symbols"])
    if test_count >= 100 or public_symbols >= 100:
        difficulty = "hard"
    elif test_count >= 20:
        difficulty = "medium"
    else:
        difficulty = "easy"
    risks = list(inspection["risk_flags"])
    return {
        "package": package,
        "repository": repository,
        "language": "go",
        "source_kind": "go-modules",
        "upstream_url": f"https://github.com/{repository}",
        "revision": revision,
        "license_spdx": license_spdx,
        "license_evidence": (
            f"https://github.com/{repository}/blob/{revision}/{license_file_name}"
            if license_file_name
            else f"https://github.com/{repository}/tree/{revision}"
        ),
        "stars": metadata.get("stargazers_count"),
        "last_activity": metadata.get("pushed_at"),
        "category": "go-library",
        "difficulty": difficulty,
        "observed_at": observed_at,
        "test_evidence": "static source inventory; source-freeze must run go test -json",
        **inspection,
        "risk_flags": risks,
        "status": "needs-evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", action="append", default=[])
    parser.add_argument("--seed-file", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, default=Path(".nl2repo/go-discovery-work"))
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
    rejected: list[dict[str, str]] = []
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
            except Exception as exc:  # noqa: BLE001 - preserve candidate-specific evidence
                message = f"{type(exc).__name__}: {exc}"
                if message in {
                    f"ValueError: repository is archived: {repository}",
                    f"ValueError: repository is a fork: {repository}",
                }:
                    rejected.append(
                        {
                            "package": package,
                            "repository": repository,
                            "reason": message,
                        }
                    )
                else:
                    errors.append(
                        {
                            "package": package,
                            "repository": repository,
                            "error": message,
                        }
                    )
    records.sort(key=lambda item: item["package"])
    candidates = [record for record in records if record["profile_eligible"]]
    excluded = [record for record in records if not record["profile_eligible"]]
    report = {
        "schema_version": "1.0",
        "report_id": "go-production-discovery-" + args.observed_at[:10],
        "observed_at": args.observed_at,
        "language": "go",
        "source_kind": "go-modules",
        "selection_profile": {
            "name": "pure-go-single-module-public-api-v1",
            "hard_exclusion_flags": sorted(HARD_EXCLUSION_FLAGS),
            "min_stars": 100,
            "max_activity_months": 36,
        },
        "candidates": candidates,
        "excluded": excluded,
        "rejected": sorted(rejected, key=lambda item: item["package"]),
        "errors": sorted(errors, key=lambda item: item["package"]),
        "next_stage": "queue-build-source-freeze-go-packages-test-inventory",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "candidates": len(candidates),
                "excluded": len(excluded),
                "rejected": len(rejected),
                "errors": len(errors),
            },
            sort_keys=True,
        )
    )
    return 0 if candidates or not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
