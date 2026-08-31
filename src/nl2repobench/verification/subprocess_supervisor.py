"""Shared, bounded subprocess primitive for untrusted candidate processes."""

from __future__ import annotations

import base64
import ctypes
import errno
import json
import os
import resource
import select
import selectors
import signal
import stat
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, cast

from .process_cleanup import candidate_pids, terminate_uid_processes

SCHEMA_VERSION = "1.0"
CANDIDATE_UID = 10001
CANDIDATE_GID = 10001
HARD_TIMEOUT_SEC = 600.0
HARD_CPU_SEC = 600
HARD_STDIN_BYTES = 1 * 1024 * 1024
HARD_OUTPUT_BYTES = 8 * 1024 * 1024
HARD_FILE_BYTES = 512 * 1024 * 1024
HARD_OPEN_FILES = 256
HARD_PROCESSES = 64
MAX_ERROR_MESSAGE = 4096
MAX_ERROR_PIDS = 64
MAX_REQUEST_JSON_BYTES = 1 * 1024 * 1024
MAX_RESULT_JSON_BYTES = 20 * 1024 * 1024

_PR_SET_NO_NEW_PRIVS = 38
_PR_CAPBSET_DROP = 24
_PR_CAP_AMBIENT = 47
_PR_CAP_AMBIENT_CLEAR_ALL = 4
_CAP_LAST_CAP = 63


class ProcessContractError(ValueError):
    """The trusted caller supplied a malformed process request."""


@dataclass(frozen=True)
class ProcessError:
    code: str
    stage: str
    message: str
    pids: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        codes = {
            "spawn-failed",
            "preexec-failed",
            "exec-failed",
            "cleanup-timeout",
            "cleanup-residue",
        }
        stages = {"spawn", "privilege-transition", "exec", "cleanup"}
        expected_stage = {
            "spawn-failed": "spawn",
            "preexec-failed": "privilege-transition",
            "exec-failed": "exec",
            "cleanup-timeout": "cleanup",
            "cleanup-residue": "cleanup",
        }
        if self.code not in codes or self.stage not in stages:
            raise ProcessContractError("invalid process error code or stage")
        if expected_stage[self.code] != self.stage:
            raise ProcessContractError("process error code and stage do not match")
        if len(self.message) > MAX_ERROR_MESSAGE or not self.message:
            raise ProcessContractError("invalid process error message")
        if len(self.pids) > MAX_ERROR_PIDS or any(pid <= 0 for pid in self.pids):
            raise ProcessContractError("invalid process error PID list")

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "stage": self.stage,
            "message": self.message,
            "pids": list(self.pids),
        }


@dataclass(frozen=True)
class SubprocessLimits:
    timeout_sec: float = HARD_TIMEOUT_SEC
    cpu_sec: int = HARD_CPU_SEC
    max_stdin_bytes: int = HARD_STDIN_BYTES
    max_output_bytes: int = HARD_OUTPUT_BYTES
    max_file_bytes: int = HARD_FILE_BYTES
    max_open_files: int = HARD_OPEN_FILES
    uid: int = CANDIDATE_UID
    gid: int = CANDIDATE_GID
    max_processes: int = HARD_PROCESSES

    def __post_init__(self) -> None:
        values = (
            self.timeout_sec,
            self.cpu_sec,
            self.max_stdin_bytes,
            self.max_output_bytes,
            self.max_file_bytes,
            self.max_open_files,
            self.max_processes,
        )
        if any(value <= 0 for value in values):
            raise ProcessContractError("process limits must be positive")
        if self.timeout_sec > HARD_TIMEOUT_SEC or self.cpu_sec > HARD_CPU_SEC:
            raise ProcessContractError("process timeout exceeds hard limit")
        if self.max_stdin_bytes > HARD_STDIN_BYTES or self.max_output_bytes > HARD_OUTPUT_BYTES:
            raise ProcessContractError("process I/O limit exceeds hard limit")
        if self.max_file_bytes > HARD_FILE_BYTES or self.max_open_files > HARD_OPEN_FILES:
            raise ProcessContractError("process resource limit exceeds hard limit")
        if self.max_processes > HARD_PROCESSES:
            raise ProcessContractError("process count exceeds hard limit")
        if not 1 <= self.uid <= 65535 or not 1 <= self.gid <= 65535:
            raise ProcessContractError("invalid process UID or GID")


def _absolute_root(value: Path, name: str) -> Path:
    if not value.is_absolute() or value.is_symlink() or not value.is_dir():
        raise ProcessContractError(f"{name} must be an absolute directory")
    return value.resolve()


@dataclass(frozen=True)
class CandidateCommand:
    argv: tuple[str, ...]
    cwd: str
    environment: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.argv or any(not isinstance(value, str) or not value for value in self.argv):
            raise ProcessContractError("candidate argv must be non-empty strings")
        path = Path(self.cwd)
        if path.is_absolute() or ".." in path.parts or not self.cwd:
            raise ProcessContractError("candidate cwd must be a safe relative path")
        for name, value in self.environment:
            if not name.isidentifier() or not value or len(value) > 4096:
                raise ProcessContractError("invalid candidate environment")


@dataclass(frozen=True)
class CandidateProcessPolicy:
    task_id: str
    staging_root: Path
    read_only_roots: tuple[Path, ...]
    write_root: Path
    allowed_executable_roots: tuple[Path, ...]
    allowed_environment_names: frozenset[str]
    require_no_new_privs: bool = True
    require_empty_capabilities: bool = True

    def __post_init__(self) -> None:
        if not self.task_id or "/" in self.task_id or ".." in Path(self.task_id).parts:
            raise ProcessContractError("invalid task ID")
        staging = _absolute_root(self.staging_root, "staging_root")
        write = _absolute_root(self.write_root, "write_root")
        if staging not in write.parents and write != staging:
            raise ProcessContractError("write_root escapes staging_root")
        for root in self.read_only_roots:
            _absolute_root(root, "policy root")
        if not self.require_no_new_privs or not self.require_empty_capabilities:
            raise ProcessContractError("candidate security requirements cannot be disabled")
        if any(
            not name.isidentifier()
            or name in {"PATH", "LD_PRELOAD", "LD_LIBRARY_PATH"}
            for name in self.allowed_environment_names
        ):
            raise ProcessContractError("invalid or unsafe environment name")

    def validate_command(self, command: CandidateCommand) -> Path:
        executable = Path(command.argv[0])
        if not executable.is_absolute() or executable.is_symlink() or not executable.is_file():
            raise ProcessContractError("candidate executable must be an existing absolute file")
        executable = executable.resolve()
        if not any(
            executable == root or root in executable.parents
            for root in self.allowed_executable_roots
        ):
            raise ProcessContractError("candidate executable is outside allowed roots")
        cwd = (self.staging_root / command.cwd).resolve()
        if cwd != self.staging_root and self.staging_root not in cwd.parents:
            raise ProcessContractError("candidate cwd escapes staging root")
        if not cwd.is_dir() or cwd.is_symlink():
            raise ProcessContractError("candidate cwd is not a regular directory")
        allowed = self.allowed_environment_names
        if any(name not in allowed for name, _ in command.environment):
            raise ProcessContractError("candidate environment is not allowlisted")
        return cwd


@dataclass(frozen=True)
class SubprocessResult:
    request_id: str
    returncode: int
    stdout: bytes = b""
    stderr: bytes = b""
    timed_out: bool = False
    output_limit_exceeded: bool = False
    cleanup_complete: bool = True
    spawn_error: ProcessError | None = None
    cleanup_error: ProcessError | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "request_id": self.request_id,
            "returncode": self.returncode,
            "stdout_base64": base64.b64encode(self.stdout).decode("ascii"),
            "stderr_base64": base64.b64encode(self.stderr).decode("ascii"),
            "timed_out": self.timed_out,
            "output_limit_exceeded": self.output_limit_exceeded,
            "cleanup_complete": self.cleanup_complete,
            "spawn_error": self.spawn_error.as_dict() if self.spawn_error else None,
            "cleanup_error": self.cleanup_error.as_dict() if self.cleanup_error else None,
        }


def _reject_special(path: Path) -> None:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise ProcessContractError(f"cannot inspect policy path: {path}") from exc
    if any(
        checker(mode)
        for checker in (stat.S_ISLNK, stat.S_ISSOCK, stat.S_ISFIFO, stat.S_ISBLK, stat.S_ISCHR)
    ):
        raise ProcessContractError(f"special or symlink path is forbidden: {path}")
    if stat.S_ISREG(mode) and mode & (stat.S_ISUID | stat.S_ISGID):
        raise ProcessContractError(f"setuid/setgid file is forbidden: {path}")


def _validate_tree(root: Path) -> None:
    _reject_special(root)
    for path in root.rglob("*"):
        _reject_special(path)


def _prctl(option: int, arg2: int = 0, arg3: int = 0, arg4: int = 0, arg5: int = 0) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    result = libc.prctl(option, arg2, arg3, arg4, arg5)
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def _child_status_ok(uid: int, gid: int) -> None:
    fields: dict[str, list[int]] = {}
    for line in Path("/proc/self/status").read_text(encoding="ascii").splitlines():
        key, separator, raw = line.partition(":")
        if separator and key in {"Uid", "Gid"}:
            fields[key] = [int(value) for value in raw.split()]
    if fields.get("Uid") != [uid] * 4 or fields.get("Gid") != [gid] * 4:
        raise OSError(errno.EPERM, "child UID/GID verification failed")
    capabilities = {"CapInh", "CapPrm", "CapEff", "CapAmb"}
    for line in Path("/proc/self/status").read_text(encoding="ascii").splitlines():
        key, separator, raw = line.partition(":")
        if separator and key in capabilities and int(raw.strip(), 16) != 0:
            raise OSError(errno.EPERM, "child capability verification failed")
    for line in Path("/proc/self/status").read_text(encoding="ascii").splitlines():
        if line.startswith("NoNewPrivs:") and line.split()[1] != "1":
            raise OSError(errno.EPERM, "no_new_privs verification failed")


def _privilege_setup(uid: int, gid: int, error_fd: int, limits: SubprocessLimits) -> None:
    try:
        _prctl(_PR_SET_NO_NEW_PRIVS, 1)
        _prctl(_PR_CAP_AMBIENT, _PR_CAP_AMBIENT_CLEAR_ALL)
        for capability in range(_CAP_LAST_CAP + 1):
            try:
                _prctl(_PR_CAPBSET_DROP, capability)
            except OSError as exc:
                if exc.errno not in {errno.EINVAL, errno.EPERM}:
                    raise
        os.setgroups([])
        os.setresgid(gid, gid, gid)
        os.setresuid(uid, uid, uid)
        resource.setrlimit(resource.RLIMIT_CPU, (int(limits.cpu_sec), int(limits.cpu_sec)))
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits.max_file_bytes, limits.max_file_bytes))
        resource.setrlimit(resource.RLIMIT_NOFILE, (limits.max_open_files, limits.max_open_files))
        resource.setrlimit(resource.RLIMIT_NPROC, (limits.max_processes, limits.max_processes))
        _child_status_ok(uid, gid)
    except BaseException as exc:  # child must report typed failure without traceback
        payload = json.dumps(
            {
                "code": "preexec-failed",
                "stage": "privilege-transition",
                "message": str(exc)[:MAX_ERROR_MESSAGE],
            }
        ).encode()
        try:
            os.write(error_fd, payload)
        finally:
            os._exit(127)
    os.close(error_fd)


def _kill_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _read_streams(
    process: subprocess.Popen[bytes], request: bytes, limits: SubprocessLimits
) -> tuple[bytes, bytes, bool, bool]:
    assert process.stdin is not None and process.stdout is not None and process.stderr is not None
    selector = selectors.DefaultSelector()
    buffers = {process.stdout: bytearray(), process.stderr: bytearray()}
    for stream in buffers:
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ)
    os.set_blocking(process.stdin.fileno(), False)
    selector.register(process.stdin, selectors.EVENT_WRITE)
    offset = 0
    captured = 0
    deadline = time.monotonic() + limits.timeout_sec
    timed_out = False
    output_limit = False
    while selector.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            _kill_group(process)
            break
        for key, _ in selector.select(min(remaining, 0.1)):
            selected_file: Any = key.fileobj
            if selected_file is process.stdin:
                try:
                    written = os.write(process.stdin.fileno(), request[offset:])
                except (BrokenPipeError, ConnectionResetError):
                    written = len(request) - offset
                except BlockingIOError:
                    continue
                offset += written
                if offset == len(request):
                    selector.unregister(process.stdin)
                    process.stdin.close()
                continue
            selected = cast(BinaryIO, selected_file)
            try:
                data = os.read(selected.fileno(), 65536)
            except OSError:
                data = b""
            if not data:
                selector.unregister(selected)
                selected.close()
                continue
            if captured + len(data) > limits.max_output_bytes:
                allowed = max(0, limits.max_output_bytes - captured)
                buffers[selected].extend(data[:allowed])
                captured += allowed
                output_limit = True
                _kill_group(process)
                break
            buffers[selected].extend(data)
            captured += len(data)
        if timed_out or output_limit:
            break
    for key in list(selector.get_map().values()):
        try:
            selector.unregister(key.fileobj)
            cast(Any, key.fileobj).close()
        except (OSError, ValueError):
            pass
    selector.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _kill_group(process)
        process.wait()
    return bytes(buffers[process.stdout]), bytes(buffers[process.stderr]), timed_out, output_limit


def _cleanup(uid: int) -> tuple[bool, ProcessError | None]:
    try:
        terminate_uid_processes(uid)
    except RuntimeError as exc:
        pids = tuple(candidate_pids(uid)[:MAX_ERROR_PIDS])
        return False, ProcessError(
            "cleanup-timeout", "cleanup", str(exc)[:MAX_ERROR_MESSAGE], pids
        )
    remaining = tuple(candidate_pids(uid)[:MAX_ERROR_PIDS])
    if remaining:
        return False, ProcessError(
            "cleanup-residue", "cleanup", "candidate processes remain", remaining
        )
    return True, None


def run_candidate_process(
    command: CandidateCommand,
    limits: SubprocessLimits,
    policy: CandidateProcessPolicy,
    *,
    request_id: str,
    stdin_data: bytes = b"",
) -> SubprocessResult:
    """Run one candidate process with strict validation and typed cleanup."""
    if (
        not isinstance(request_id, str)
        or len(request_id) != 32
        or any(char not in "0123456789abcdef" for char in request_id)
    ):
        raise ProcessContractError("request_id must be 32 lowercase hexadecimal characters")
    if len(stdin_data) > limits.max_stdin_bytes:
        raise ProcessContractError("candidate stdin exceeds limit")
    cwd = policy.validate_command(command)
    roots: tuple[Path, ...] = (*policy.read_only_roots, policy.write_root)
    for root in roots:
        _validate_tree(root)
    before = tuple(candidate_pids(limits.uid))
    if before:
        return SubprocessResult(
            request_id,
            127,
            cleanup_complete=False,
            cleanup_error=ProcessError(
                "cleanup-residue",
                "cleanup",
                "candidate UID is not quiescent",
                before[:MAX_ERROR_PIDS],
            ),
        )
    error_read, error_write = os.pipe()
    os.set_inheritable(error_write, True)
    environment = {
        "HOME": "/nonexistent",
        "PYTHONDONTWRITEBYTECODE": "1",
        **dict(command.environment),
    }
    try:
        process = subprocess.Popen(
            command.argv,
            cwd=cwd,
            env=environment,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            pass_fds=(error_write,),
            preexec_fn=lambda: _privilege_setup(limits.uid, limits.gid, error_write, limits),
        )
    except OSError as exc:
        os.close(error_read)
        os.close(error_write)
        return SubprocessResult(
            request_id,
            127,
            spawn_error=ProcessError("spawn-failed", "spawn", str(exc)[:MAX_ERROR_MESSAGE]),
        )
    os.close(error_write)
    ready, _, _ = select.select([error_read], [], [], limits.timeout_sec)
    child_error = os.read(error_read, MAX_ERROR_MESSAGE + 1) if ready else b""
    os.close(error_read)
    if child_error:
        try:
            payload = json.loads(child_error.decode("utf-8"))
            spawn_error = ProcessError(payload["code"], payload["stage"], payload["message"])
        except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            spawn_error = ProcessError(
                "preexec-failed", "privilege-transition", str(exc)[:MAX_ERROR_MESSAGE]
            )
        _kill_group(process)
        process.wait()
        complete, cleanup_error = _cleanup(limits.uid)
        return SubprocessResult(
            request_id,
            127,
            cleanup_complete=complete,
            spawn_error=spawn_error,
            cleanup_error=cleanup_error,
        )
    stdout, stderr, timed_out, output_limit = _read_streams(process, stdin_data, limits)
    complete, cleanup_error = _cleanup(limits.uid)
    return SubprocessResult(
        request_id,
        124 if timed_out else (125 if output_limit else int(process.returncode or 0)),
        stdout,
        stderr,
        timed_out,
        output_limit,
        complete,
        cleanup_error=cleanup_error,
    )


__all__ = [
    "CANDIDATE_GID",
    "CANDIDATE_UID",
    "CandidateCommand",
    "CandidateProcessPolicy",
    "HARD_FILE_BYTES",
    "HARD_OPEN_FILES",
    "HARD_OUTPUT_BYTES",
    "HARD_PROCESSES",
    "HARD_STDIN_BYTES",
    "HARD_TIMEOUT_SEC",
    "ProcessContractError",
    "ProcessError",
    "SCHEMA_VERSION",
    "SubprocessLimits",
    "SubprocessResult",
    "run_candidate_process",
]
