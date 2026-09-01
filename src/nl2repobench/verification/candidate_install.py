"""Trusted wall-clock and storage supervisor for candidate package installation."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path

from .subprocess_supervisor import CANDIDATE_UID

CANDIDATE_FAILURE_EXIT = 20
INTERNAL_ERROR_EXIT = 70
MAX_INSTALL_BYTES = 512 * 1024 * 1024
MAX_INSTALL_ENTRIES = 50_000


def tree_usage(paths: tuple[Path, ...]) -> tuple[int, int]:
    entries = 0
    total_bytes = 0
    pending = list(paths)
    while pending:
        current = pending.pop()
        try:
            with os.scandir(current) as iterator:
                children = list(iterator)
        except FileNotFoundError:
            continue
        for child in children:
            entries += 1
            try:
                metadata = child.stat(follow_symlinks=False)
            except FileNotFoundError:
                # Build backends may remove a temporary bytecode file between
                # scandir and stat; it is not a candidate failure.
                entries -= 1
                continue
            if stat.S_ISDIR(metadata.st_mode):
                pending.append(Path(child.path))
            elif stat.S_ISREG(metadata.st_mode):
                total_bytes += metadata.st_size
            if entries > MAX_INSTALL_ENTRIES or total_bytes > MAX_INSTALL_BYTES:
                return entries, total_bytes
    return entries, total_bytes


def _parse_build_environment(entries: tuple[str, ...]) -> tuple[str, ...]:
    """Validate trusted, task-declared environment entries for the build child."""

    parsed: list[str] = []
    forbidden = {"PATH", "PYTHONPATH", "LD_PRELOAD", "LD_LIBRARY_PATH"}
    for entry in entries:
        name, separator, value = entry.partition("=")
        if not separator or not re.fullmatch(r"[A-Z_][A-Z0-9_]*", name):
            raise ValueError(f"invalid candidate build environment entry: {entry!r}")
        if name in forbidden:
            raise ValueError(f"candidate build environment cannot override {name}")
        if len(value) > 512:
            raise ValueError("candidate build environment value is too long")
        parsed.append(entry)
    return tuple(parsed)


def install_candidate(
    source: Path,
    target: Path,
    timeout_sec: float,
    cflags: str = "-O0 -g0",
    build_environment: tuple[str, ...] = (),
) -> dict[str, object]:
    writable_root = Path("/tmp/candidate-build")
    home = writable_root / "home"
    temporary = writable_root / "tmp"
    for path in (target, home, temporary):
        path.mkdir(parents=True, exist_ok=True)
        os.chown(path, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(Path("/tmp"), 0o755)
    candidate_home = Path("/home/candidate")
    if candidate_home.exists():
        os.chown(candidate_home, 0, 0)
        os.chmod(candidate_home, 0o555)

    dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    environment = [
        f"HOME={home}",
        f"TMPDIR={temporary}",
        "PYTHONDONTWRITEBYTECODE=1",
        "PIP_DISABLE_PIP_VERSION_CHECK=1",
        f"CFLAGS={cflags}",
    ]
    if dependency_root:
        environment.append(f"PYTHONPATH={dependency_root}")
    environment.extend(_parse_build_environment(build_environment))
    command = [
        "/usr/local/bin/python",
        "-B",
        "-m",
        "pip",
        "install",
        "--target",
        str(target),
        "--no-deps",
        "--no-build-isolation",
        str(source),
    ]
    from .candidate_client import _run_cli_request

    transport = _run_cli_request(
        command,
        b"",
        timeout_sec,
        context="install",
        write_root=writable_root,
        environment=[
            [name, value]
            for entry in environment
            for name, separator, value in [entry.partition("=")]
            if separator
        ],
    )
    process = transport.process
    if transport.trusted_failure or transport.outer_returncode in {64, 70, 75}:
        # These codes belong to the trusted transport, not to pip.  In
        # particular, a malformed or oversized trusted result must not become
        # a candidate installation failure/model zero.
        outcome = "internal-error"
    elif transport.timed_out or process.returncode == 124:
        outcome = "timeout"
    elif transport.output_limit_exceeded or process.returncode == 125:
        outcome = "storage-limit"
    elif process.returncode == 0:
        outcome = "success"
    else:
        outcome = "candidate-failure"
    entries, total_bytes = tree_usage((source, target, writable_root))
    return {
        "entries": entries,
        "outcome": outcome,
        "returncode": process.returncode,
        "total_bytes": total_bytes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--timeout-sec", type=float, default=90.0)
    parser.add_argument("--cflags", default="-O0 -g0")
    parser.add_argument("--build-env", action="append", default=[])
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = install_candidate(
            args.source,
            args.target,
            args.timeout_sec,
            args.cflags,
            tuple(args.build_env),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        args.status.write_text(
            json.dumps({"outcome": "internal-error", "message": str(exc)}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise SystemExit(INTERNAL_ERROR_EXIT) from None
    args.status.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    if result["outcome"] == "internal-error":
        raise SystemExit(INTERNAL_ERROR_EXIT)
    if result["outcome"] != "success":
        raise SystemExit(CANDIDATE_FAILURE_EXIT)


if __name__ == "__main__":
    main()
