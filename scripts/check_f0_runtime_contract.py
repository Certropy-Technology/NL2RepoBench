#!/usr/bin/env python3
"""Fail closed until the F0 canonical migration has no active runtime bypasses."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

from pydantic import ValidationError

from nl2repobench.domain.canonical_contract import TaskSource


@dataclass(frozen=True, slots=True)
class Violation:
    path: str
    line: int
    token: str


FORBIDDEN = {
    "models_v2": re.compile(r"(?:domain|harbor|verification)\.models_v2|models_v2\.py"),
    "v2-model": re.compile(r"\b(?:TaskManifestV2|DeclarativeTaskSourceV2|V2RecordModel)\b"),
    "legacy-lock": re.compile(r"\b(?:lock_artifact|module_bundle)\b"),
    "schema-dispatch": re.compile(r"schema_version\s*(?:==|!=)\s*[\"']2\.0[\"']"),
    "broad-private": re.compile(r"allow_private|--allow-private"),
}


def scan_runtime(repository_root: Path) -> tuple[Violation, ...]:
    source_root = repository_root / "src/nl2repobench"
    violations: list[Violation] = []
    for path in sorted(source_root.rglob("*.py")):
        relative = path.relative_to(repository_root)
        if "analysis" in relative.parts and "archive" in relative.parts:
            continue
        if "legacy" in relative.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for token, pattern in FORBIDDEN.items():
                if pattern.search(line):
                    violations.append(Violation(relative.as_posix(), line_number, token))
    return tuple(violations)


def canonical_source_errors(repository_root: Path) -> dict[str, tuple[str, ...]]:
    root = repository_root / "catalog/sources"
    errors: dict[str, tuple[str, ...]] = {}
    task_files = sorted(root.rglob("task.toml"))
    for path in task_files:
        if any(
            (parent / "task.toml").is_file()
            for parent in path.parent.parents
            if parent != root and parent.is_relative_to(root)
        ):
            continue
        relative = path.relative_to(repository_root).as_posix()
        try:
            payload = tomllib.loads(path.read_text(encoding="utf-8"))
            TaskSource.model_validate(payload)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            errors[relative] = (str(exc),)
        except ValidationError as exc:
            errors[relative] = tuple(
                ".".join(str(part) for part in item["loc"]) + ": " + str(item["msg"])
                for item in exc.errors(include_url=False)
            )
    return errors


def canonical_source_gaps(repository_root: Path) -> tuple[str, ...]:
    return tuple(canonical_source_errors(repository_root))


def check(repository_root: Path) -> dict[str, object]:
    violations = scan_runtime(repository_root)
    source_errors = canonical_source_errors(repository_root)
    source_gaps = tuple(source_errors)
    staging_contract = repository_root / "harbor-runner/private-staging-contract.json"
    blockers = [] if staging_contract.is_file() else ["private-staging-contract-missing"]
    return {
        "schema_version": "1.0",
        "passed": not violations and not source_gaps and not blockers,
        "blockers": blockers,
        "runtime_violations": [asdict(item) for item in violations],
        "source_migration_gaps": list(source_gaps),
        "source_migration_errors": {
            path: list(messages) for path, messages in source_errors.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    report = check(args.repository_root.resolve())
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
