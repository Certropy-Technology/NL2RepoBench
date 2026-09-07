"""Bounded subprocess supervisor for generated Go bridges."""

from __future__ import annotations

import os
import resource
import selectors
import signal
import subprocess
import time
from dataclasses import dataclass
from typing import IO, cast


@dataclass(frozen=True)
class GoBridgeResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    timed_out: bool = False
    output_limit_exceeded: bool = False


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
    if len(request) > max_output_bytes:
        raise ValueError("bridge request exceeds output limit")

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
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None
    selector = selectors.DefaultSelector()
    streams = {process.stdout: bytearray(), process.stderr: bytearray()}
    for registered_stream in streams:
        os.set_blocking(registered_stream.fileno(), False)
        selector.register(registered_stream, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout_sec
    timed_out = False
    output_limit_exceeded = False
    captured_total = 0
    request_offset = 0
    os.set_blocking(process.stdin.fileno(), False)
    selector.register(process.stdin, selectors.EVENT_WRITE)
    while selector.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            break
        for key, _ in selector.select(min(remaining, 0.25)):
            selected_file = key.fileobj
            if selected_file is process.stdin:
                try:
                    written = os.write(process.stdin.fileno(), request[request_offset:])
                except BlockingIOError:
                    continue
                except (BrokenPipeError, ConnectionResetError):
                    written = len(request) - request_offset
                request_offset += written
                if request_offset == len(request):
                    selector.unregister(process.stdin)
                    process.stdin.close()
                continue
            if selected_file is process.stdout:
                output_stream = process.stdout
            elif selected_file is process.stderr:
                output_stream = process.stderr
            else:
                raise RuntimeError("unexpected bridge selector stream")
            data = os.read(output_stream.fileno(), 64 * 1024)
            if not data:
                selector.unregister(output_stream)
                output_stream.close()
                continue
            target = streams[output_stream]
            remaining_output = max_output_bytes - captured_total
            if len(data) > remaining_output:
                if remaining_output > 0:
                    target.extend(data[:remaining_output])
                    captured_total += remaining_output
                output_limit_exceeded = True
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                selector.unregister(output_stream)
                output_stream.close()
                break
            target.extend(data)
            captured_total += len(data)
        if timed_out or output_limit_exceeded:
            break
    for key in list(selector.get_map().values()):
        try:
            selector.unregister(key.fileobj)
            if isinstance(key.fileobj, int):
                os.close(key.fileobj)
            else:
                cast(IO[bytes], key.fileobj).close()
        except (OSError, ValueError):
            pass
    selector.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    return GoBridgeResult(
        returncode=124 if timed_out else (125 if output_limit_exceeded else process.returncode),
        stdout=bytes(streams[process.stdout]),
        stderr=bytes(streams[process.stderr]),
        timed_out=timed_out,
        output_limit_exceeded=output_limit_exceeded,
    )


__all__ = ["GoBridgeResult", "run_go_bridge"]
