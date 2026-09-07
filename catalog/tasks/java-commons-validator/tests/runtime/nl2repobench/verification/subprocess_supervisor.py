"""Shared bounded process lifecycle for candidate-side commands."""

from __future__ import annotations

import math
import os
import pwd
import resource
import selectors
import signal
import subprocess
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import IO, cast

from .process_cleanup import terminate_uid_processes


@dataclass(frozen=True)
class ProcessLimits:
    timeout_sec: float
    max_output_bytes: int
    address_space_bytes: int | None = None
    max_open_files: int = 128
    max_processes: int = 256


@dataclass(frozen=True)
class ProcessResult:
    return_code: int | None
    signal: int | None
    timed_out: bool
    spawn_error: str | None
    stdout: str
    stderr: str
    stdout_bytes: int
    stderr_bytes: int
    stdout_truncated: bool
    stderr_truncated: bool




class _Capture:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.data = bytearray()
        self.total = 0

    def append(self, chunk: bytes) -> None:
        self.total += len(chunk)
        if len(self.data) < self.limit:
            self.data.extend(chunk[: self.limit - len(self.data)])

    def text(self) -> str:
        return bytes(self.data).decode("utf-8", errors="replace")


def apply_process_limits(uid: int, limits: ProcessLimits) -> None:
    """Apply child-side resource limits and permanently drop privileges."""

    cpu_seconds = max(1, math.ceil(limits.timeout_sec))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
    if limits.address_space_bytes is not None:
        resource.setrlimit(
            resource.RLIMIT_AS,
            (limits.address_space_bytes, limits.address_space_bytes),
        )
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(
        resource.RLIMIT_FSIZE,
        (limits.max_output_bytes, limits.max_output_bytes),
    )
    resource.setrlimit(
        resource.RLIMIT_NOFILE,
        (limits.max_open_files, limits.max_open_files),
    )
    resource.setrlimit(
        resource.RLIMIT_NPROC,
        (limits.max_processes, limits.max_processes),
    )
    if os.geteuid() == 0 and uid != 0:
        account = pwd.getpwuid(uid)
        os.setgroups([])
        os.setgid(account.pw_gid)
        os.setuid(uid)


def run_supervised_process(
    command: Sequence[str],
    *,
    cwd: Path,
    uid: int,
    limits: ProcessLimits,
    environment: Mapping[str, str],
    stdin_data: bytes | None = None,
) -> ProcessResult:
    """Run one argv without a shell and kill its complete process group."""

    if not command or any(not isinstance(item, str) or not item for item in command):
        raise ValueError("process command must be a non-empty argv")
    if not math.isfinite(limits.timeout_sec) or limits.timeout_sec <= 0:
        raise ValueError("process timeout must be finite and positive")
    if limits.max_output_bytes <= 0:
        raise ValueError("process output limit must be positive")
    if limits.address_space_bytes is not None and limits.address_space_bytes <= 0:
        raise ValueError("process address space limit must be positive")
    if limits.max_open_files <= 0 or limits.max_processes <= 0:
        raise ValueError("process count and file limits must be positive")
    if uid != os.getuid() and os.geteuid() != 0:
        raise ValueError("dropping to a different UID requires root")
    process_environment = dict(environment)
    try:
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            env=process_environment,
            stdin=subprocess.PIPE if stdin_data is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            shell=False,
            preexec_fn=lambda: apply_process_limits(uid, limits),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return ProcessResult(
            return_code=None,
            signal=None,
            timed_out=False,
            spawn_error=str(exc),
            stdout="",
            stderr="",
            stdout_bytes=0,
            stderr_bytes=0,
            stdout_truncated=False,
            stderr_truncated=False,
        )

    assert process.stdout is not None and process.stderr is not None
    stdout = _Capture(limits.max_output_bytes)
    stderr = _Capture(limits.max_output_bytes)
    selector = selectors.DefaultSelector()
    captures = {process.stdout: stdout, process.stderr: stderr}
    for stream in captures:
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ)
    input_offset = 0
    if stdin_data is not None and process.stdin is not None:
        os.set_blocking(process.stdin.fileno(), False)
        if stdin_data:
            selector.register(process.stdin, selectors.EVENT_WRITE)
        else:
            process.stdin.close()
    timed_out = False
    deadline = time.monotonic() + limits.timeout_sec
    drain_deadline: float | None = None
    while selector.get_map():
        now = time.monotonic()
        if process.poll() is None and now >= deadline and drain_deadline is None:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            drain_deadline = now + 1.0
        elif process.poll() is not None and drain_deadline is None:
            # A detached descendant may retain an inherited pipe forever.
            drain_deadline = now + 1.0
        if drain_deadline is not None and now >= drain_deadline:
            break
        wake_at = deadline if drain_deadline is None else drain_deadline
        for key, _ in selector.select(min(0.1, max(0.0, wake_at - now))):
            stream = cast(IO[bytes], key.fileobj)
            if process.stdin is not None and stream is process.stdin:
                assert stdin_data is not None
                try:
                    written = os.write(process.stdin.fileno(), stdin_data[input_offset:])
                except BlockingIOError:
                    continue
                except (BrokenPipeError, ConnectionResetError):
                    written = len(stdin_data) - input_offset
                input_offset += written
                if input_offset == len(stdin_data):
                    selector.unregister(process.stdin)
                    process.stdin.close()
                continue
            capture = captures.get(stream)
            if capture is None:
                raise RuntimeError("unexpected supervised process stream")
            try:
                chunk = os.read(stream.fileno(), 64 * 1024)
            except BlockingIOError:
                continue
            if chunk:
                capture.append(chunk)
            else:
                selector.unregister(stream)
                stream.close()
    for key in list(selector.get_map().values()):
        try:
            fileobj = cast(IO[bytes], key.fileobj)
            selector.unregister(fileobj)
            fileobj.close()
        except (OSError, ValueError):
            pass
    selector.close()
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=1.0)
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if uid != os.getuid():
            terminate_uid_processes(uid)

    return_code = process.returncode
    signal_number = -return_code if return_code is not None and return_code < 0 else None
    if signal_number is not None:
        return_code = None
    return ProcessResult(
        return_code=return_code,
        signal=signal_number,
        timed_out=timed_out,
        spawn_error=None,
        stdout=stdout.text(),
        stderr=stderr.text(),
        stdout_bytes=stdout.total,
        stderr_bytes=stderr.total,
        stdout_truncated=stdout.total > limits.max_output_bytes,
        stderr_truncated=stderr.total > limits.max_output_bytes,
    )


__all__ = [
    "ProcessLimits",
    "ProcessResult",
    "apply_process_limits",
    "run_supervised_process",
]
