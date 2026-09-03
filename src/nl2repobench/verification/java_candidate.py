"""Candidate source boundary for the first Java/Maven profile."""

from __future__ import annotations

import stat
from pathlib import Path

from nl2repobench.package_managers.maven import validate_candidate_pom

MAX_JAVA_FILES = 10_000
MAX_JAVA_SOURCE_BYTES = 64 * 1024 * 1024
MAX_JAVA_TOTAL_BYTES = 256 * 1024 * 1024
ALLOWED_ROOT_FILES = frozenset({"pom.xml"})


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
            validate_candidate_pom(data)
        elif (
            len(relative.parts) >= 4
            and relative.parts[:3] == ("src", "main", "java")
            and path.suffix == ".java"
        ):
            data = _regular(path)
            java_files += 1
        elif len(relative.parts) >= 4 and relative.parts[:3] == ("src", "main", "resources"):
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
    args = parser.parse_args()
    try:
        validate_java_workspace(args.root)
    except JavaWorkspaceRejected as exc:
        print(str(exc))
        raise SystemExit(20) from None


if __name__ == "__main__":
    main()
