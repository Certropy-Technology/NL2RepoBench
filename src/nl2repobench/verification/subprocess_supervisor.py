"""Shared, bounded subprocess primitive for untrusted candidate processes."""

from __future__ import annotations

import base64
import ctypes
import errno
import json
import os
import resource
import selectors
import signal
import stat
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

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
        for root in self.allowed_executable_roots:
            _absolute_root(root, "allowed executable root")
        if self.require_no_new_privs is not True or self.require_empty_capabilities is not True:
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


def _reject_special(path: Path, *, reject_symlink: bool = True) -> None:
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise ProcessContractError(f"cannot inspect policy path: {path}") from exc
    if reject_symlink and any(
        checker(mode)
        for checker in (stat.S_ISLNK, stat.S_ISSOCK, stat.S_ISFIFO, stat.S_ISBLK, stat.S_ISCHR)
    ):
        raise ProcessContractError(f"special or symlink path is forbidden: {path}")
    if not reject_symlink and any(
        checker(mode) for checker in (stat.S_ISSOCK, stat.S_ISFIFO, stat.S_ISBLK, stat.S_ISCHR)
    ):
        raise ProcessContractError(f"special path is forbidden: {path}")
    if stat.S_ISREG(mode):
        if mode & (stat.S_ISUID | stat.S_ISGID):
            raise ProcessContractError(f"setuid/setgid file is forbidden: {path}")
        if path.stat().st_nlink != 1:
            raise ProcessContractError(f"hardlink file is forbidden: {path}")


def _validate_tree(root: Path, *, reject_symlinks: bool = True) -> None:
    _reject_special(root, reject_symlink=reject_symlinks)
    for path in root.rglob("*"):
        _reject_special(path, reject_symlink=reject_symlinks)


def _validate_executable_root(root: Path, uid: int, gid: int) -> None:
    """Require an immutable executable tree from the candidate's perspective."""
    _validate_tree(root)
    for path in (root, *root.rglob("*")):
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise ProcessContractError(f"cannot inspect executable root: {path}") from exc
        mode = metadata.st_mode
        candidate_writable = (
            (metadata.st_uid == uid and bool(mode & stat.S_IWUSR))
            or (metadata.st_gid == gid and bool(mode & stat.S_IWGRP))
            or bool(mode & stat.S_IWOTH)
        )
        if candidate_writable:
            raise ProcessContractError(f"executable root is writable by candidate: {path}")


def _prctl(option: int, arg2: int = 0, arg3: int = 0, arg4: int = 0, arg5: int = 0) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    result = libc.prctl(option, arg2, arg3, arg4, arg5)
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def _child_status_ok(uid: int, gid: int) -> None:
    fields: dict[str, list[int]] = {}
    capabilities: dict[str, int] = {}
    no_new_privs: str | None = None
    for line in Path("/proc/self/status").read_text(encoding="ascii").splitlines():
        key, separator, raw = line.partition(":")
        if not separator:
            continue
        if key in {"Uid", "Gid"}:
            fields[key] = [int(value) for value in raw.split()]
        elif key in {"CapInh", "CapPrm", "CapEff", "CapAmb", "CapBnd"}:
            capabilities[key] = int(raw.strip(), 16)
        elif key == "NoNewPrivs":
            no_new_privs = raw.strip()
    if fields.get("Uid") != [uid] * 4 or fields.get("Gid") != [gid] * 4:
        raise OSError(errno.EPERM, "child UID/GID verification failed")
    required_capabilities = {"CapInh", "CapPrm", "CapEff", "CapAmb", "CapBnd"}
    if set(capabilities) != required_capabilities or any(capabilities.values()):
        raise OSError(errno.EPERM, "child capability verification failed")
    if no_new_privs != "1":
        raise OSError(errno.EPERM, "no_new_privs verification failed")


def _close_inherited_fds(keep: set[int]) -> None:
    """Close every inherited descriptor except the stdio and error pipe FDs."""
    try:
        with os.scandir("/proc/self/fd") as entries:
            inherited = [int(entry.name) for entry in entries]
    except OSError as exc:
        raise ProcessContractError("cannot enumerate inherited file descriptors") from exc
    for fd in inherited:
        if fd > 2 and fd not in keep:
            try:
                os.close(fd)
            except OSError:
                pass


def _privilege_setup(uid: int, gid: int, limits: SubprocessLimits) -> None:
    _prctl(_PR_SET_NO_NEW_PRIVS, 1)
    _prctl(_PR_CAP_AMBIENT, _PR_CAP_AMBIENT_CLEAR_ALL)
    for capability in range(_CAP_LAST_CAP + 1):
        try:
            _prctl(_PR_CAPBSET_DROP, capability)
        except OSError as exc:
            if exc.errno != errno.EINVAL:
                raise
    os.setgroups([])
    os.setresgid(gid, gid, gid)
    os.setresuid(uid, uid, uid)
    resource.setrlimit(resource.RLIMIT_CPU, (int(limits.cpu_sec), int(limits.cpu_sec)))
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits.max_file_bytes, limits.max_file_bytes))
    resource.setrlimit(resource.RLIMIT_NOFILE, (limits.max_open_files, limits.max_open_files))
    resource.setrlimit(resource.RLIMIT_NPROC, (limits.max_processes, limits.max_processes))
    _child_status_ok(uid, gid)


def _write_child_error(error_fd: int, code: str, stage: str, message: str) -> None:
    payload = json.dumps(
        {"code": code, "stage": stage, "message": message[:MAX_ERROR_MESSAGE]},
        separators=(",", ":"),
    ).encode("utf-8")
    try:
        os.write(error_fd, payload)
    finally:
        os._exit(127)


def _kill_group(pid: int, signum: int = signal.SIGKILL) -> None:
    try:
        os.killpg(pid, signum)
    except ProcessLookupError:
        pass


class _ForkedProcess:
    def __init__(self, pid: int, stdin_fd: int, stdout_fd: int, stderr_fd: int) -> None:
        self.pid = pid
        self.stdin_fd = stdin_fd
        self.stdout_fd = stdout_fd
        self.stderr_fd = stderr_fd
        self.returncode: int | None = None

    def poll(self) -> int | None:
        if self.returncode is not None:
            return self.returncode
        waited, status = os.waitpid(self.pid, os.WNOHANG)
        if waited == 0:
            return None
        self.returncode = os.waitstatus_to_exitcode(status)
        return self.returncode

    def wait(self, deadline: float | None = None) -> int:
        while self.returncode is None:
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError("candidate process wait exceeded deadline")
            self.poll()
            if self.returncode is None:
                time.sleep(0.01)
        return self.returncode

    def close_stdin(self) -> None:
        if self.stdin_fd >= 0:
            os.close(self.stdin_fd)
            self.stdin_fd = -1


def _fork_exec(
    command: CandidateCommand,
    cwd: Path,
    environment: dict[str, str],
    limits: SubprocessLimits,
) -> tuple[_ForkedProcess, int]:
    stdin_read, stdin_write = os.pipe()
    stdout_read, stdout_write = os.pipe()
    stderr_read, stderr_write = os.pipe()
    error_read, error_write = os.pipe()
    for fd in (stdin_write, stdout_read, stderr_read, error_read):
        os.set_inheritable(fd, False)
    os.set_inheritable(error_write, False)
    pid = os.fork()
    if pid == 0:
        try:
            os.close(stdin_write)
            os.close(stdout_read)
            os.close(stderr_read)
            os.close(error_read)
            os.setsid()
            os.dup2(stdin_read, 0)
            os.dup2(stdout_write, 1)
            os.dup2(stderr_write, 2)
            for fd in (stdin_read, stdout_write, stderr_write):
                if fd not in {0, 1, 2}:
                    os.close(fd)
            os.chdir(cwd)
            _close_inherited_fds({0, 1, 2, error_write})
            try:
                _privilege_setup(limits.uid, limits.gid, limits)
            except BaseException as exc:
                _write_child_error(error_write, "preexec-failed", "privilege-transition", str(exc))
            try:
                os.execve(command.argv[0], list(command.argv), environment)
            except OSError as exc:
                _write_child_error(error_write, "exec-failed", "exec", str(exc))
        except BaseException as exc:
            _write_child_error(error_write, "preexec-failed", "privilege-transition", str(exc))
    os.close(stdin_read)
    os.close(stdout_write)
    os.close(stderr_write)
    os.close(error_write)
    return _ForkedProcess(pid, stdin_write, stdout_read, stderr_read), error_read


def _read_streams(
    process: _ForkedProcess,
    request: bytes,
    limits: SubprocessLimits,
    deadline: float,
    initial_stdout: bytes = b"",
    initial_stderr: bytes = b"",
) -> tuple[bytes, bytes, bool, bool]:
    selector = selectors.DefaultSelector()
    buffers = {
        process.stdout_fd: bytearray(initial_stdout),
        process.stderr_fd: bytearray(initial_stderr),
    }
    captured = len(initial_stdout) + len(initial_stderr)
    if captured > limits.max_output_bytes:
        return initial_stdout[: limits.max_output_bytes], initial_stderr[:0], False, True
    buffers_fds = tuple(buffers)
    for fd in buffers_fds:
        if fd < 0:
            continue
        os.set_blocking(fd, False)
        selector.register(fd, selectors.EVENT_READ)
    if process.stdin_fd >= 0:
        os.set_blocking(process.stdin_fd, False)
        selector.register(process.stdin_fd, selectors.EVENT_WRITE)
    offset = 0
    timed_out = False
    output_limit = False
    while selector.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            break
        for key, _ in selector.select(min(remaining, 0.1)):
            selected_fd = key.fd
            if selected_fd == process.stdin_fd:
                try:
                    written = os.write(process.stdin_fd, request[offset:])
                except (BrokenPipeError, ConnectionResetError):
                    written = len(request) - offset
                except BlockingIOError:
                    continue
                offset += written
                if offset == len(request):
                    selector.unregister(process.stdin_fd)
                    process.close_stdin()
                continue
            try:
                data = os.read(selected_fd, 65536)
            except OSError:
                data = b""
            if not data:
                selector.unregister(selected_fd)
                os.close(selected_fd)
                continue
            if captured + len(data) > limits.max_output_bytes:
                allowed = max(0, limits.max_output_bytes - captured)
                buffers[selected_fd].extend(data[:allowed])
                captured += allowed
                output_limit = True
                break
            buffers[selected_fd].extend(data)
            captured += len(data)
        if timed_out or output_limit:
            break
    for key in list(selector.get_map().values()):
        try:
            selector.unregister(key.fileobj)
            fd = key.fd
            try:
                os.close(fd)
            except OSError:
                pass
        except (OSError, ValueError):
            pass
    selector.close()
    return (
        bytes(buffers.get(process.stdout_fd, b"")),
        bytes(buffers.get(process.stderr_fd, b"")),
        timed_out,
        output_limit,
    )


def _cleanup(
    uid: int, process: _ForkedProcess | None = None, deadline: float | None = None
) -> tuple[bool, ProcessError | None]:
    if process is not None:
        _kill_group(process.pid, signal.SIGTERM)
        grace = min(0.1, max(0.0, (deadline or time.monotonic() + 0.1) - time.monotonic()))
        if grace:
            time.sleep(grace)
        _kill_group(process.pid)
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
    for root in (*policy.read_only_roots, policy.write_root):
        _validate_tree(root)
    for root in policy.allowed_executable_roots:
        _validate_executable_root(root, limits.uid, limits.gid)
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
    environment = {
        "HOME": "/nonexistent",
        "PYTHONDONTWRITEBYTECODE": "1",
        **dict(command.environment),
    }
    deadline = time.monotonic() + limits.timeout_sec
    try:
        process, error_read = _fork_exec(command, cwd, environment, limits)
    except OSError as exc:
        return SubprocessResult(
            request_id,
            127,
            spawn_error=ProcessError("spawn-failed", "spawn", str(exc)[:MAX_ERROR_MESSAGE]),
        )

    os.set_blocking(error_read, False)
    startup_buffer = bytearray()
    startup_stdout = bytearray()
    startup_stderr = bytearray()
    startup_done = False
    startup_error: ProcessError | None = None
    startup_output_limit = False
    startup_timed_out = False
    selector = selectors.DefaultSelector()
    selector.register(error_read, selectors.EVENT_READ)
    for fd, buffer in ((process.stdout_fd, startup_stdout), (process.stderr_fd, startup_stderr)):
        os.set_blocking(fd, False)
        selector.register(fd, selectors.EVENT_READ, buffer)
    while not startup_done and selector.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            startup_timed_out = True
            break
        for key, _ in selector.select(min(remaining, 0.1)):
            fd = key.fd
            if fd == error_read:
                data = os.read(error_read, MAX_ERROR_MESSAGE + 1)
                if data:
                    startup_buffer.extend(data)
                    try:
                        payload = json.loads(data.decode("utf-8"))
                        startup_error = ProcessError(
                            payload["code"], payload["stage"], payload["message"]
                        )
                    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                        startup_error = ProcessError(
                            "preexec-failed", "privilege-transition", str(exc)[:MAX_ERROR_MESSAGE]
                        )
                    startup_done = True
                else:
                    startup_done = True
                selector.unregister(error_read)
                os.close(error_read)
                continue
            buffer = cast(bytearray, key.data)
            data = os.read(fd, 65536)
            if not data:
                selector.unregister(fd)
                os.close(fd)
                if fd == process.stdout_fd:
                    process.stdout_fd = -1
                elif fd == process.stderr_fd:
                    process.stderr_fd = -1
                continue
            if len(startup_stdout) + len(startup_stderr) + len(data) > limits.max_output_bytes:
                startup_output_limit = True
                startup_done = True
                break
            buffer.extend(data)
    for key in list(selector.get_map().values()):
        fd = key.fd
        try:
            selector.unregister(fd)
            if fd not in {process.stdout_fd, process.stderr_fd}:
                os.close(fd)
        except (OSError, ValueError):
            pass
    selector.close()
    if startup_error or startup_timed_out or startup_output_limit:
        if startup_timed_out:
            startup_error = ProcessError(
                "preexec-failed", "privilege-transition", "privilege transition exceeded deadline"
            )
        complete, cleanup_error = _cleanup(limits.uid, process, deadline)
        return SubprocessResult(
            request_id,
            127,
            bytes(startup_stdout),
            bytes(startup_stderr),
            startup_timed_out,
            startup_output_limit,
            complete,
            spawn_error=startup_error,
            cleanup_error=cleanup_error,
        )
    stdout, stderr, timed_out, output_limit = _read_streams(
        process,
        stdin_data,
        limits,
        deadline,
        bytes(startup_stdout),
        bytes(startup_stderr),
    )
    if not timed_out and not output_limit:
        try:
            process.wait(deadline)
        except TimeoutError:
            timed_out = True
    complete, cleanup_error = _cleanup(limits.uid, process, deadline)
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
