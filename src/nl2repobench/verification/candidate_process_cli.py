"""Drop privileges and exec one candidate process inside its parent group."""

from __future__ import annotations

import argparse
import math
import os
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from .subprocess_supervisor import ProcessLimits, apply_process_limits

SAFE_ENVIRONMENT_NAMES = frozenset({"PATH", "JAVA_HOME", "LANG", "LC_ALL"})


def exec_candidate_process(
    command: Sequence[str],
    *,
    cwd: Path,
    uid: int,
    timeout_sec: float,
    address_space_bytes: int,
) -> NoReturn:
    """Exec candidate argv after applying the shared child-side policy."""

    if not command or any(not isinstance(item, str) or not item for item in command):
        raise ValueError("candidate command must be a non-empty argv")
    if not math.isfinite(timeout_sec) or timeout_sec <= 0:
        raise ValueError("candidate timeout must be finite and positive")
    if address_space_bytes <= 0:
        raise ValueError("candidate address space limit must be positive")
    if cwd.is_symlink() or not cwd.is_dir():
        raise ValueError("candidate working directory must be a regular directory")
    environment = {
        name: os.environ[name]
        for name in SAFE_ENVIRONMENT_NAMES
        if name in os.environ
    }
    environment.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    environment["HOME"] = "/home/candidate"
    os.chdir(cwd)
    apply_process_limits(
        uid,
        ProcessLimits(
            timeout_sec=timeout_sec,
            max_output_bytes=8 * 1024 * 1024,
            address_space_bytes=address_space_bytes,
            max_open_files=128,
            max_processes=256,
        ),
    )
    os.execvpe(command[0], list(command), environment)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--uid", type=int, required=True)
    parser.add_argument("--timeout-sec", type=float, required=True)
    parser.add_argument("--address-space-bytes", type=int, default=4 * 1024 * 1024 * 1024)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    try:
        exec_candidate_process(
            command,
            cwd=args.cwd,
            uid=args.uid,
            timeout_sec=args.timeout_sec,
            address_space_bytes=args.address_space_bytes,
        )
    except (OSError, ValueError) as exc:
        print(f"candidate process setup failed: {exc}", file=__import__("sys").stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["exec_candidate_process", "main"]
