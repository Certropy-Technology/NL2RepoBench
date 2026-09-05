"""Candidate source boundary for the first Java/Maven profile."""

from __future__ import annotations

import json
import stat
from pathlib import Path

from nl2repobench.package_managers.maven import validate_candidate_pom

MAX_JAVA_FILES = 10_000
MAX_JAVA_SOURCE_BYTES = 64 * 1024 * 1024
MAX_JAVA_TOTAL_BYTES = 256 * 1024 * 1024
ALLOWED_ROOT_FILES = frozenset({"pom.xml"})
FORBIDDEN_RESOURCE_SUFFIXES = frozenset(
    {".a", ".bat", ".class", ".cmd", ".dll", ".dylib", ".exe", ".jar", ".o", ".sh", ".so"}
)


class JavaWorkspaceRejected(ValueError):
    """Candidate workspace contains an unsupported or unsafe Java asset."""


def _regular(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise JavaWorkspaceRejected(f"Java candidate path is not a regular file: {path}")
    mode = path.stat().st_mode
    if stat.S_ISLNK(mode) or mode & 0o111:
        raise JavaWorkspaceRejected(f"Java candidate file is executable: {path}")
    data = path.read_bytes()
    if len(data) > MAX_JAVA_SOURCE_BYTES:
        raise JavaWorkspaceRejected(f"Java candidate file is too large: {path}")
    return data


def validate_java_workspace(root: Path) -> dict[str, int | bool]:
    """Validate allowed Java source paths and parse ``pom.xml`` as metadata."""

    if root.is_symlink() or not root.is_dir():
        raise JavaWorkspaceRejected(f"Java candidate root is not a directory: {root}")
    total = 0
    java_files = 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise JavaWorkspaceRejected(f"Java candidate contains a symlink: {relative}")
        if path.is_dir():
            if path.name in {"target", ".mvn"}:
                raise JavaWorkspaceRejected(
                    f"Java candidate build directory is not allowed: {relative}"
                )
            if relative.parts and relative.parts[0] not in {"src"}:
                raise JavaWorkspaceRejected(f"Java candidate directory is not allowed: {relative}")
            if relative.parts[:3] == ("src", "main", "resources"):
                continue
            if relative.parts[:3] not in {
                ("src",),
                ("src", "main"),
                ("src", "main", "java"),
            } and not (len(relative.parts) >= 4 and relative.parts[:3] == ("src", "main", "java")):
                raise JavaWorkspaceRejected(f"Java candidate directory is not allowed: {relative}")
            continue
        if relative.parts == ("pom.xml",):
            data = _regular(path)
            try:
                validate_candidate_pom(data)
            except ValueError as exc:
                raise JavaWorkspaceRejected(str(exc)) from exc
        elif (
            len(relative.parts) >= 4
            and relative.parts[:3] == ("src", "main", "java")
            and path.suffix == ".java"
        ):
            data = _regular(path)
            java_files += 1
        elif len(relative.parts) >= 4 and relative.parts[:3] == ("src", "main", "resources"):
            if path.suffix.lower() in FORBIDDEN_RESOURCE_SUFFIXES:
                raise JavaWorkspaceRejected(
                    f"Java candidate resource type is not allowed: {relative}"
                )
            data = _regular(path)
        else:
            raise JavaWorkspaceRejected(f"Java candidate file is not allowed: {relative}")
        total += len(data)
        if java_files > MAX_JAVA_FILES:
            raise JavaWorkspaceRejected("Java candidate contains too many source files")
        if total > MAX_JAVA_TOTAL_BYTES:
            raise JavaWorkspaceRejected("Java candidate source exceeds the total size limit")
    if java_files == 0:
        raise JavaWorkspaceRejected("Java candidate contains no src/main/java source")
    return {
        "java_files": java_files,
        "total_bytes": total,
        "pom_present": (root / "pom.xml").is_file(),
    }


__all__ = ["JavaWorkspaceRejected", "validate_java_workspace"]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        summary = validate_java_workspace(args.root)
        if args.report is not None:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(
                    {"policy": "java-candidate-policy-v1", "status": "accepted", **summary},
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
    except JavaWorkspaceRejected as exc:
        if args.report is not None:
            message = str(exc)
            lowered = message.casefold()
            category = (
                "pom-forbidden-build-configuration"
                if "forbidden build or dependency" in lowered
                else "pom-unsupported-metadata"
                if "pom" in lowered
                else "workspace-boundary"
            )
            args.report.parent.mkdir(parents=True, exist_ok=True)
            detail = {
                "policy_version": "java-candidate-policy-v1",
                "phase": "candidate-installation",
                "category": category,
                "path": "pom.xml" if "pom" in lowered else None,
                "message": message,
                "workspace_root": str(args.root),
            }
            args.report.write_text(
                json.dumps(
                    {"policy": "java-candidate-policy-v1", "status": "rejected", **detail},
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
        print(str(exc))
        raise SystemExit(20) from None


if __name__ == "__main__":
    main()
