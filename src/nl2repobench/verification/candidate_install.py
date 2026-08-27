"""Trusted wall-clock and storage supervisor for candidate package installation."""

from __future__ import annotations

import argparse
import json
import os
import signal
import stat
import subprocess
import time
from pathlib import Path

from .process_cleanup import terminate_uid_processes

CANDIDATE_UID = 10001
CANDIDATE_FAILURE_EXIT = 20
INTERNAL_ERROR_EXIT = 70
MAX_INSTALL_BYTES = 512 * 1024 * 1024
MAX_INSTALL_ENTRIES = 50_000
POLL_INTERVAL_SEC = 0.1


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


def _kill_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def install_candidate(
    source: Path,
    target: Path,
    timeout_sec: float,
    address_space_bytes: int = 512 * 1024 * 1024,
    cflags: str = "-O0 -g0",
) -> dict[str, object]:
    if address_space_bytes <= 0:
        raise ValueError("address-space limit must be positive")
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
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        *environment,
        "prlimit",
        f"--as={address_space_bytes}",
        "--cpu=60",
        "--fsize=67108864",
        "--nofile=128",
        "--nproc=32",
        "--",
        "python",
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
    process = subprocess.Popen(command, start_new_session=True)
    deadline = time.monotonic() + timeout_sec
    outcome = "candidate-failure"
    try:
        while process.poll() is None:
            if time.monotonic() >= deadline:
                outcome = "timeout"
                _kill_group(process)
                break
            entries, total_bytes = tree_usage((source, target, writable_root))
            if entries > MAX_INSTALL_ENTRIES or total_bytes > MAX_INSTALL_BYTES:
                outcome = "storage-limit"
                _kill_group(process)
                break
            time.sleep(POLL_INTERVAL_SEC)
        process.wait(timeout=5)
        if process.returncode == 0 and outcome == "candidate-failure":
            outcome = "success"
    finally:
        _kill_group(process)
        terminate_uid_processes(CANDIDATE_UID)
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
    parser.add_argument("--address-space-bytes", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--cflags", default="-O0 -g0")
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = install_candidate(
            args.source,
            args.target,
            args.timeout_sec,
            args.address_space_bytes,
            args.cflags,
        )
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        args.status.write_text(
            json.dumps({"outcome": "internal-error", "message": str(exc)}, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        raise SystemExit(INTERNAL_ERROR_EXIT) from None
    args.status.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    if result["outcome"] != "success":
        raise SystemExit(CANDIDATE_FAILURE_EXIT)


if __name__ == "__main__":
    main()
