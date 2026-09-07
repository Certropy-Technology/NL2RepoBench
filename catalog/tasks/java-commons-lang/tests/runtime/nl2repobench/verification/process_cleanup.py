"""Kill residual processes owned by the unprivileged candidate UID."""

from __future__ import annotations

import argparse
import os
import signal
import time
from pathlib import Path


def candidate_pids(uid: int) -> list[int]:
    pids: list[int] = []
    for status in Path("/proc").glob("[0-9]*/status"):
        try:
            uid_line = next(
                line
                for line in status.read_text(encoding="utf-8").splitlines()
                if line.startswith("Uid:")
            )
            real_uid = int(uid_line.split()[1])
            if real_uid == uid:
                pids.append(int(status.parent.name))
        except (OSError, StopIteration, ValueError):
            continue
    return pids


def terminate_uid_processes(uid: int, *, attempts: int = 20) -> None:
    """Kill and rescan until no process owned by *uid* remains."""

    for _ in range(attempts):
        pids = [pid for pid in candidate_pids(uid) if pid != os.getpid()]
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.01)
    remaining = [pid for pid in candidate_pids(uid) if pid != os.getpid()]
    if remaining:
        raise RuntimeError(f"candidate processes survived cleanup: {remaining}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uid", type=int, required=True)
    args = parser.parse_args()
    terminate_uid_processes(args.uid)


if __name__ == "__main__":
    main()
