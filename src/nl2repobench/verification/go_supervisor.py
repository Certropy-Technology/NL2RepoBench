"""Thin Go bridge adapter over the shared candidate process boundary."""

from __future__ import annotations

import base64
import binascii
import json
import os
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .subprocess_supervisor import (
    CANDIDATE_GID,
    CANDIDATE_UID,
    HARD_FILE_BYTES,
    HARD_OPEN_FILES,
    HARD_PROCESSES,
    HARD_STDIN_BYTES,
    HARD_TIMEOUT_SEC,
    ProcessContractError,
    ProcessError,
)

VERIFIER_STAGING_PARENT = Path("/var/lib/nl2repobench/verifier-staging")


@dataclass(frozen=True)
class GoBridgeResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    timed_out: bool = False
    output_limit_exceeded: bool = False
    cleanup_complete: bool = True
    verifier_invalid: bool = False


def _error_result(message: str, *, returncode: int = 70) -> GoBridgeResult:
    return GoBridgeResult(
        returncode=returncode,
        stdout=b"",
        stderr=message.encode("utf-8", errors="replace")[:4096],
        verifier_invalid=True,
    )


def _decode_result(
    raw: bytes,
    *,
    request_id: str,
    max_output_bytes: int,
) -> GoBridgeResult:
    try:
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("generic result is not an object")
        if payload.get("schema_version") != "1.0":
            raise ValueError("unsupported generic result schema")
        if payload.get("request_id") != request_id:
            raise ValueError("generic result request_id mismatch")
        stdout = base64.b64decode(payload["stdout_base64"], validate=True)
        stderr = base64.b64decode(payload["stderr_base64"], validate=True)
        if any(not isinstance(payload[key], bool) for key in (
            "timed_out", "output_limit_exceeded", "cleanup_complete"
        )):
            raise ValueError("generic result flags must be booleans")
        timed_out = payload["timed_out"]
        output_limit = payload["output_limit_exceeded"]
        cleanup_complete = payload["cleanup_complete"]
        if timed_out and output_limit:
            raise ValueError("generic result has conflicting timeout and output flags")
        if len(stdout) + len(stderr) > max_output_bytes:
            raise ValueError("decoded bridge output exceeds limit")
        spawn_error = payload.get("spawn_error")
        cleanup_error = payload.get("cleanup_error")
        if spawn_error is not None and not isinstance(spawn_error, dict):
            raise ValueError("invalid spawn_error")
        if cleanup_error is not None and not isinstance(cleanup_error, dict):
            raise ValueError("invalid cleanup_error")
        if spawn_error is not None:
            ProcessError(**spawn_error)
        if cleanup_error is not None:
            ProcessError(**cleanup_error)
        if cleanup_complete and cleanup_error is not None:
            raise ValueError("cleanup error with complete cleanup")
        if not cleanup_complete and cleanup_error is None:
            raise ValueError("incomplete cleanup without cleanup error")
        raw_returncode = payload["returncode"]
        if isinstance(raw_returncode, bool) or not isinstance(raw_returncode, int):
            raise ValueError("generic result returncode must be an integer")
        returncode = raw_returncode
        if timed_out:
            returncode = 124
        elif output_limit:
            returncode = 125
        elif spawn_error is not None:
            returncode = 127
        return GoBridgeResult(
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            timed_out=timed_out,
            output_limit_exceeded=output_limit,
            cleanup_complete=cleanup_complete,
            verifier_invalid=not cleanup_complete,
        )
    except (KeyError, TypeError, ValueError, binascii.Error, json.JSONDecodeError) as exc:
        return _error_result(f"invalid generic bridge result: {exc}")


def _request(
    command: tuple[str, ...],
    request: bytes,
    *,
    timeout_sec: float,
    max_output_bytes: int,
    staging_root: Path,
) -> tuple[str, bytes]:
    if not command or any(not isinstance(item, str) or not item for item in command):
        raise ProcessContractError("bridge command must be non-empty strings")
    executable = Path(command[0])
    if not executable.is_absolute() or executable.is_symlink() or not executable.is_file():
        raise ProcessContractError("bridge executable must be an existing absolute file")
    if len(request) > HARD_STDIN_BYTES:
        raise ProcessContractError("bridge request exceeds stdin limit")
    if timeout_sec <= 0 or timeout_sec > HARD_TIMEOUT_SEC:
        raise ProcessContractError("bridge timeout exceeds hard limit")
    if max_output_bytes <= 0 or max_output_bytes > 8 * 1024 * 1024:
        raise ProcessContractError("bridge output limit exceeds hard limit")
    request_id = secrets.token_hex(16)
    write_root = staging_root / "write"
    write_root.mkdir()
    write_root.chmod(0o777)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "request_id": request_id,
        "context": "bridge",
        "command": {
            "argv": list(command),
            "cwd": ".",
            "environment": [],
        },
        "limits": {
            "timeout_sec": timeout_sec,
            "cpu_sec": max(1, min(int(timeout_sec), 600)),
            "max_stdin_bytes": HARD_STDIN_BYTES,
            "max_output_bytes": max_output_bytes,
            "max_file_bytes": HARD_FILE_BYTES,
            "max_open_files": HARD_OPEN_FILES,
            "uid": CANDIDATE_UID,
            "gid": CANDIDATE_GID,
            "max_processes": HARD_PROCESSES,
        },
        "policy": {
            "task_id": "go-bridge",
            "staging_root": str(staging_root),
            "read_only_roots": [],
            "write_root": str(write_root),
            "allowed_executable_roots": [str(executable.parent)],
            "allowed_environment_names": [],
            "require_no_new_privs": True,
            "require_empty_capabilities": True,
        },
        "stdin_base64": base64.b64encode(request).decode("ascii"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return request_id, encoded


def _stage_executable(command: tuple[str, ...], staging_root: Path) -> tuple[str, ...]:
    """Copy the bridge into a root-owned, symlink-free executable root."""

    source = Path(command[0])
    if not source.is_absolute() or source.is_symlink() or not source.is_file():
        raise ProcessContractError("bridge executable must be an existing absolute file")
    source = source.resolve()
    executable_root = staging_root / "executable"
    executable_root.mkdir()
    staged = executable_root / source.name
    shutil.copyfile(source, staged)
    staged.chmod(source.stat().st_mode & 0o777)
    return (str(staged), *command[1:])


def _trusted_staging_parent() -> Path:
    """Create and validate the root-owned parent used for bridge staging.

    The system temporary directory is intentionally excluded: it is commonly
    world-writable, while the shared supervisor validates every executable-root
    ancestor before forking.  Only this fixed verifier-owned root may be
    created, and every ancestor is checked before and after creation.
    """

    parent = VERIFIER_STAGING_PARENT
    if not parent.is_absolute() or any(part in {"", ".", ".."} for part in parent.parts):
        raise ProcessContractError("bridge staging parent must be a canonical absolute path")

    missing: list[Path] = []
    current = parent
    while True:
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            missing.append(current)
            ancestor = current.parent
            if ancestor == current:
                raise ProcessContractError(
                    "bridge staging parent has no existing safe ancestor"
                ) from None
            current = ancestor
            continue
        except OSError as exc:
            raise ProcessContractError("cannot inspect bridge staging parent") from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ProcessContractError("bridge staging parent contains an unsafe ancestor")
        break

    while True:
        try:
            metadata = current.lstat()
        except OSError as exc:
            raise ProcessContractError("cannot inspect bridge staging ancestry") from exc
        if (
            stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISDIR(metadata.st_mode)
            or metadata.st_uid != 0
            or metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH)
            or not metadata.st_mode & stat.S_IXOTH
        ):
            raise ProcessContractError("bridge staging ancestry is not trusted-owned/traversable")
        if current == Path(current.anchor):
            break
        current = current.parent

    for directory in reversed(missing):
        try:
            directory.mkdir()
        except FileExistsError:
            pass
        try:
            directory.chmod(0o755)
            metadata = directory.lstat()
        except OSError as exc:
            raise ProcessContractError("cannot create bridge staging parent") from exc
        if (
            stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISDIR(metadata.st_mode)
            or metadata.st_uid != 0
            or metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH)
            or not metadata.st_mode & stat.S_IXOTH
        ):
            raise ProcessContractError("created bridge staging parent is unsafe")
    try:
        parent.chmod(0o755)
    except OSError as exc:
        raise ProcessContractError("cannot make bridge staging parent traversable") from exc
    try:
        metadata = parent.lstat()
    except OSError as exc:
        raise ProcessContractError("cannot inspect bridge staging parent") from exc
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISDIR(metadata.st_mode)
        or metadata.st_uid != 0
        or metadata.st_mode & (stat.S_IWGRP | stat.S_IWOTH)
        or not metadata.st_mode & stat.S_IXOTH
    ):
        raise ProcessContractError("bridge staging parent is unsafe")
    return parent


def run_go_bridge(
    command: tuple[str, ...],
    request: bytes,
    *,
    timeout_sec: float = 30.0,
    max_output_bytes: int = 256 * 1024,
    uid: int = CANDIDATE_UID,
) -> GoBridgeResult:
    """Run a bridge through the shared UID-isolated JSON process boundary."""

    if uid != CANDIDATE_UID:
        return _error_result("bridge UID must use the fixed candidate identity")
    try:
        staging_parent = _trusted_staging_parent()
        with tempfile.TemporaryDirectory(
            prefix="nl2repo-go-bridge-", dir=staging_parent
        ) as temporary:
            staging_root = Path(temporary)
            staging_root.chmod(0o755)
            staged_command = _stage_executable(command, staging_root)
            request_id, encoded = _request(
                staged_command,
                request,
                timeout_sec=timeout_sec,
                max_output_bytes=max_output_bytes,
                staging_root=staging_root,
            )
            completed = subprocess.run(
                [sys.executable, "-m", "nl2repobench.verification.candidate_process_cli"],
                input=encoded,
                capture_output=True,
                cwd=staging_root,
                env={
                    "PATH": "/usr/bin:/bin",
                    "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                timeout=timeout_sec + 5.0,
                check=False,
            )
            if completed.returncode in {64, 70}:
                return _error_result(
                    completed.stderr.decode("utf-8", errors="replace")
                    or "candidate process CLI rejected bridge request"
                )
            result = _decode_result(
                completed.stdout,
                request_id=request_id,
                max_output_bytes=max_output_bytes,
            )
            if completed.returncode == 75:
                return GoBridgeResult(
                    result.returncode,
                    result.stdout,
                    result.stderr,
                    result.timed_out,
                    result.output_limit_exceeded,
                    cleanup_complete=False,
                    verifier_invalid=True,
                )
            if completed.returncode != 0:
                return _error_result(
                    completed.stderr.decode("utf-8", errors="replace")
                    or "candidate process CLI failed"
                )
            return result
    except subprocess.TimeoutExpired as exc:
        return _error_result(f"bridge CLI exceeded wrapper deadline: {exc}")
    except (OSError, ProcessContractError, ValueError) as exc:
        return _error_result(str(exc))


__all__ = ["GoBridgeResult", "run_go_bridge"]
