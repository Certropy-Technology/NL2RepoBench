"""Bounded ingestion of the candidate-controlled Harbor workspace."""

from __future__ import annotations

import argparse
import os
import stat
from dataclasses import dataclass
from pathlib import Path

MAX_ENTRIES = 20_000
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_RELATIVE_PATH_BYTES = 512
COPY_BUFFER_BYTES = 1024 * 1024
CANDIDATE_REJECTION_EXIT = 20
INTERNAL_ERROR_EXIT = 70


class WorkspaceRejected(ValueError):
    """Raised when candidate-controlled workspace content violates limits."""


@dataclass
class CopyBudget:
    entries: int = 0
    total_bytes: int = 0


def _harden_source(path: Path, *, directory: bool) -> None:
    desired_mode = 0o555 if directory else 0o444
    metadata = path.stat(follow_symlinks=False)
    if metadata.st_uid != 0:
        os.chown(path, 0, 0, follow_symlinks=False)
    os.chmod(path, desired_mode, follow_symlinks=False)
    hardened = path.stat(follow_symlinks=False)
    if hardened.st_uid != 0 or hardened.st_mode & 0o222:
        raise OSError(f"cannot make workspace path root-owned and read-only: {path}")


def _copy_regular(source: Path, destination: Path, expected_size: int) -> None:
    source_fd = os.open(source, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    destination_fd = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    copied = 0
    try:
        metadata = os.fstat(source_fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size != expected_size:
            raise WorkspaceRejected(f"workspace file changed while copying: {source}")
        while copied < expected_size:
            chunk = os.read(source_fd, min(COPY_BUFFER_BYTES, expected_size - copied))
            if not chunk:
                raise WorkspaceRejected(f"workspace file ended early: {source}")
            view = memoryview(chunk)
            while view:
                written = os.write(destination_fd, view)
                view = view[written:]
            copied += len(chunk)
    finally:
        os.close(source_fd)
        os.close(destination_fd)


def copy_workspace(source: Path, destination: Path) -> CopyBudget:
    source = source.resolve()
    if source != Path("/workspace") and not source.is_dir():
        raise OSError(f"workspace source is unavailable: {source}")
    destination.mkdir(parents=True, exist_ok=False)
    budget = CopyBudget()

    def visit(source_dir: Path, destination_dir: Path, relative: Path) -> None:
        with os.scandir(source_dir) as iterator:
            entries = sorted(iterator, key=lambda entry: entry.name)
        for entry in entries:
            budget.entries += 1
            if budget.entries > MAX_ENTRIES:
                raise WorkspaceRejected("workspace contains too many entries")
            child_relative = relative / entry.name
            if len(os.fsencode(child_relative.as_posix())) > MAX_RELATIVE_PATH_BYTES:
                raise WorkspaceRejected(f"workspace path is too long: {child_relative}")
            source_path = Path(entry.path)
            destination_path = destination_dir / entry.name
            metadata = entry.stat(follow_symlinks=False)
            if stat.S_ISDIR(metadata.st_mode):
                destination_path.mkdir(mode=0o700)
                visit(source_path, destination_path, child_relative)
                _harden_source(source_path, directory=True)
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise WorkspaceRejected(f"workspace entry is not a regular file: {child_relative}")
            if metadata.st_size > MAX_FILE_BYTES:
                raise WorkspaceRejected(f"workspace file exceeds size limit: {child_relative}")
            budget.total_bytes += metadata.st_size
            if budget.total_bytes > MAX_TOTAL_BYTES:
                raise WorkspaceRejected("workspace total size exceeds limit")
            _copy_regular(source_path, destination_path, metadata.st_size)
            source_mode = stat.S_IMODE(metadata.st_mode)
            os.chmod(destination_path, 0o755 if source_mode & 0o111 else 0o644)
            _harden_source(source_path, directory=False)
        os.chmod(destination_dir, 0o755)

    visit(source, destination, Path())
    _harden_source(source, directory=True)
    return budget


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("/workspace"))
    parser.add_argument("--destination", type=Path, default=Path("/tmp/candidate"))
    args = parser.parse_args()
    try:
        copy_workspace(args.source, args.destination)
    except WorkspaceRejected as exc:
        print(str(exc))
        raise SystemExit(CANDIDATE_REJECTION_EXIT) from None
    except OSError as exc:
        print(str(exc))
        raise SystemExit(INTERNAL_ERROR_EXIT) from None


if __name__ == "__main__":
    main()
