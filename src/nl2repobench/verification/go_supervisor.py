"""Bounded subprocess supervisor for generated Go bridges."""

from __future__ import annotations

import os
import resource
import signal
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class GoBridgeResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    timed_out: bool = False


def run_go_bridge(
    command: tuple[str, ...],
    request: bytes,
    *,
    timeout_sec: float = 30.0,
    max_output_bytes: int = 256 * 1024,
    uid: int = 10001,
) -> GoBridgeResult:
    """Run a bridge with bounded output and process/resource cleanup."""

    if not command or timeout_sec <= 0 or max_output_bytes <= 0:
        raise ValueError("bridge command and limits must be positive")

    def limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (int(timeout_sec), int(timeout_sec) + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (max_output_bytes, max_output_bytes))
        resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
        if os.geteuid() == 0:
            os.setuid(uid)

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            preexec_fn=limits,
        )
    except OSError as exc:
        return GoBridgeResult(returncode=127, stdout=b"", stderr=str(exc).encode())
    try:
        stdout, stderr = process.communicate(request, timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        return GoBridgeResult(
            returncode=124,
            stdout=stdout[:max_output_bytes],
            stderr=stderr[:max_output_bytes],
            timed_out=True,
        )
    return GoBridgeResult(
        returncode=process.returncode,
        stdout=stdout[:max_output_bytes],
        stderr=stderr[:max_output_bytes],
    )


__all__ = ["GoBridgeResult", "run_go_bridge"]
