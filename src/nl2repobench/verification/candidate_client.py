"""Trusted hidden-test client for isolated candidate operations."""

from __future__ import annotations

import base64
import binascii
import json
import os
import secrets
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .candidate_runner import MAX_OUTPUT_BYTES, RESULT_PREFIX
from .subprocess_supervisor import (
    CANDIDATE_GID,
    CANDIDATE_UID,
    HARD_OUTPUT_BYTES,
    HARD_TIMEOUT_SEC,
)

CANDIDATE_SITE = "/tmp/candidate-site"
CANDIDATE_STAGING_ROOT = Path("/tmp")
CANDIDATE_BUILD_ROOT = Path("/tmp/candidate-build")
DEFAULT_TIMEOUT_SEC = 10.0
DEFAULT_TOTAL_TIMEOUT_SEC = 300.0
_TOTAL_TIMEOUT_SEC = float(
    os.environ.get("NL2REPO_CANDIDATE_TOTAL_TIMEOUT_SEC", DEFAULT_TOTAL_TIMEOUT_SEC)
)
_CANDIDATE_DEADLINE = time.monotonic() + _TOTAL_TIMEOUT_SEC
_CLI_RESULT_LIMIT = 20 * 1024 * 1024


@dataclass(frozen=True)
class CandidateCallResult:
    ok: bool
    value: Any = None
    exception_type: str | None = None
    exception_message: str | None = None


@dataclass(frozen=True)
class CandidateProcessResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class _TransportResult:
    process: CandidateProcessResult
    timed_out: bool = False
    output_limit_exceeded: bool = False
    outer_returncode: int | None = None
    trusted_failure: bool = False


def _command(arguments: list[str]) -> list[str]:
    """Build the candidate-runner argv; execution is delegated to the CLI."""

    return [
        os.environ.get("NL2REPO_PYTHON", "/usr/local/bin/python"),
        "-I",
        "-B",
        "-m",
        "nl2repobench.verification.candidate_runner",
        "--candidate-site",
        CANDIDATE_SITE,
        *arguments,
    ]


def _environment() -> tuple[list[list[str]], set[str]]:
    names = {
        "HOME",
        "TMPDIR",
        "PYTHONDONTWRITEBYTECODE",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
        "PYTHONPATH",
        "PIP_DISABLE_PIP_VERSION_CHECK",
        "CFLAGS",
    }
    values = [
        ["HOME", "/home/candidate"],
        ["PYTHONDONTWRITEBYTECODE", "1"],
        ["PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1"],
    ]
    dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    if dependency_root:
        values.append(["PYTHONPATH", dependency_root])
    return values, names


def _build_request(
    command: list[str],
    stdin_data: bytes,
    timeout_sec: float,
    *,
    context: str,
    write_root: Path = CANDIDATE_BUILD_ROOT,
    environment: list[list[str]] | None = None,
) -> tuple[str, bytes]:
    if context not in {"call", "install"}:
        raise ValueError("invalid candidate context")
    if not command or not command[0].startswith("/"):
        raise ValueError("candidate executable must be absolute")
    if not 0 < timeout_sec <= HARD_TIMEOUT_SEC:
        raise ValueError("candidate timeout exceeds hard limit")
    if not CANDIDATE_STAGING_ROOT.is_dir() or CANDIDATE_STAGING_ROOT.is_symlink():
        raise ValueError("candidate staging root is unavailable")
    write_root.mkdir(parents=True, exist_ok=True)
    request_id = secrets.token_hex(16)
    default_environment, names = _environment()
    environment = default_environment if environment is None else environment
    for item in environment:
        if len(item) != 2 or not all(isinstance(value, str) for value in item):
            raise ValueError("candidate environment is malformed")
        names.add(item[0])
    executable = Path(command[0]).resolve()
    payload = {
        "schema_version": "1.0",
        "request_id": request_id,
        "context": context,
        "command": {"argv": command, "cwd": ".", "environment": environment},
        "limits": {
            "timeout_sec": float(timeout_sec),
            "cpu_sec": max(int(timeout_sec), 1),
            "max_stdin_bytes": 1 * 1024 * 1024,
            "max_output_bytes": min(MAX_OUTPUT_BYTES, HARD_OUTPUT_BYTES),
            "max_file_bytes": 512 * 1024 * 1024,
            "max_open_files": 256,
            "uid": CANDIDATE_UID,
            "gid": CANDIDATE_GID,
            "max_processes": 64,
        },
        "policy": {
            "task_id": "python-candidate",
            "staging_root": str(CANDIDATE_STAGING_ROOT),
            "read_only_roots": [],
            "write_root": str(write_root.resolve()),
            "allowed_executable_roots": [str(executable.parent)],
            "allowed_environment_names": sorted(names),
            "require_no_new_privs": True,
            "require_empty_capabilities": True,
        },
        "stdin_base64": base64.b64encode(stdin_data).decode("ascii"),
    }
    return request_id, json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _decode_bounded(value: object, label: str) -> bytes:
    if not isinstance(value, str):
        raise ValueError(f"candidate {label} is not base64")
    try:
        decoded = base64.b64decode(value.encode("ascii"), validate=True)
    except (ValueError, binascii.Error, UnicodeEncodeError) as exc:
        raise ValueError(f"candidate {label} is not valid base64") from exc
    if len(decoded) > MAX_OUTPUT_BYTES:
        raise ValueError(f"candidate {label} exceeds output limit")
    return decoded


def _invoke_cli(request_id: str, encoded: bytes, timeout_sec: float) -> _TransportResult:
    command = [
        os.environ.get("NL2REPO_PYTHON", "/usr/local/bin/python"),
        "-I",
        "-m",
        "nl2repobench.verification.candidate_process_cli",
    ]
    try:
        completed = subprocess.run(
            command,
            input=encoded,
            capture_output=True,
            timeout=min(max(timeout_sec, 0.001) + 2.0, HARD_TIMEOUT_SEC + 2.0),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _TransportResult(CandidateProcessResult(124, "", str(exc)), timed_out=True)
    if len(completed.stdout) > _CLI_RESULT_LIMIT:
        return _TransportResult(
            CandidateProcessResult(70, "", "candidate CLI result exceeds size limit"),
            output_limit_exceeded=True,
            outer_returncode=completed.returncode,
            trusted_failure=True,
        )
    if completed.returncode in {64, 70, 75}:
        detail = completed.stderr.decode("utf-8", errors="replace")[-2000:]
        return _TransportResult(
            CandidateProcessResult(completed.returncode, "", detail),
            outer_returncode=completed.returncode,
            trusted_failure=True,
        )
    try:
        response = json.loads(completed.stdout.decode("utf-8"))
        if not isinstance(response, dict):
            raise ValueError("candidate CLI result must be an object")
        if response.get("schema_version") != "1.0":
            raise ValueError("candidate CLI result has unsupported schema")
        if response.get("request_id") != request_id:
            raise ValueError("candidate CLI result request ID mismatch")
        if response.get("cleanup_complete") is not True:
            raise ValueError("candidate cleanup did not complete")
        if response.get("cleanup_error") is not None:
            raise ValueError("candidate cleanup returned an error")
        if not isinstance(response.get("timed_out"), bool):
            raise ValueError("candidate timeout flag is malformed")
        if not isinstance(response.get("output_limit_exceeded"), bool):
            raise ValueError("candidate output-limit flag is malformed")
        if response["timed_out"] and response["output_limit_exceeded"]:
            raise ValueError("candidate timeout and output-limit flags conflict")
        returncode = response.get("returncode")
        if isinstance(returncode, bool) or not isinstance(returncode, int):
            raise ValueError("candidate return code is malformed")
        stdout = _decode_bounded(response.get("stdout_base64"), "stdout")
        stderr = _decode_bounded(response.get("stderr_base64"), "stderr")
        return _TransportResult(
            CandidateProcessResult(
                returncode,
                stdout.decode("utf-8", errors="replace"),
                stderr.decode("utf-8", errors="replace"),
            ),
            bool(response.get("timed_out")),
            bool(response.get("output_limit_exceeded")),
            outer_returncode=completed.returncode,
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return _TransportResult(
            CandidateProcessResult(70, "", f"invalid candidate CLI result: {exc}"),
            outer_returncode=completed.returncode,
            trusted_failure=True,
        )


def _run_cli_request(
    command: list[str],
    stdin_data: bytes,
    timeout_sec: float,
    *,
    context: str,
    write_root: Path = CANDIDATE_BUILD_ROOT,
    environment: list[list[str]] | None = None,
) -> _TransportResult:
    request_id, encoded = _build_request(
        command,
        stdin_data,
        timeout_sec,
        context=context,
        write_root=write_root,
        environment=environment,
    )
    return _invoke_cli(request_id, encoded, timeout_sec)


def run_candidate(
    arguments: list[str],
    *,
    input_text: str | None = None,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
) -> CandidateProcessResult:
    remaining_sec = _CANDIDATE_DEADLINE - time.monotonic()
    if remaining_sec <= 0:
        return CandidateProcessResult(124, "", "candidate cumulative execution budget exhausted")
    try:
        return _run_cli_request(
            _command(arguments),
            (input_text or "").encode("utf-8"),
            min(timeout_sec, remaining_sec),
            context="call",
        ).process
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        return CandidateProcessResult(70, "", f"candidate transport failed: {exc}"[-2000:])


def _call_result(completed: CandidateProcessResult) -> CandidateCallResult:
    if completed.returncode != 0:
        return CandidateCallResult(
            False,
            exception_type="CandidateProcessError",
            exception_message=(completed.stderr or completed.stdout or "no response")[-2000:],
        )
    lines = [line for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if len(lines) != 1:
        return CandidateCallResult(
            False,
            exception_type="CandidateProcessError",
            exception_message="candidate response is malformed",
        )
    try:
        payload = json.loads(lines[0][len(RESULT_PREFIX) :])
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return CandidateCallResult(
            False, exception_type="CandidateProtocolError", exception_message=str(exc)
        )
    if not isinstance(payload, dict):
        return CandidateCallResult(
            False,
            exception_type="CandidateProtocolError",
            exception_message="candidate response is not an object",
        )
    return CandidateCallResult(
        ok=payload.get("ok") is True,
        value=payload.get("value"),
        exception_type=payload.get("exception_type"),
        exception_message=payload.get("exception_message"),
    )


def call(
    module: str, attribute: str, *args: Any, timeout_sec: float = DEFAULT_TIMEOUT_SEC, **kwargs: Any
) -> CandidateCallResult:
    request = json.dumps(
        {
            "args": args,
            "attribute": attribute,
            "kwargs": kwargs,
            "module": module,
            "operation": "call",
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return _call_result(run_candidate(["call"], input_text=request, timeout_sec=timeout_sec))


def call_method(
    module: str,
    attribute: str,
    constructor_args: list[Any],
    member: str,
    *args: Any,
    invoke: bool = True,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    constructor_kwargs: dict[str, Any] | None = None,
    **kwargs: Any,
) -> CandidateCallResult:
    request = json.dumps(
        {
            "args": args,
            "attribute": attribute,
            "constructor_args": constructor_args,
            "constructor_kwargs": constructor_kwargs or {},
            "invoke": invoke,
            "kwargs": kwargs,
            "member": member,
            "module": module,
            "operation": "call_method",
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return _call_result(run_candidate(["call"], input_text=request, timeout_sec=timeout_sec))


def get(module: str, attribute: str) -> CandidateCallResult:
    request = json.dumps(
        {"args": [], "attribute": attribute, "kwargs": {}, "module": module, "operation": "get"},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return _call_result(run_candidate(["call"], input_text=request))


def execute_script(source: str, *, timeout_sec: float = DEFAULT_TIMEOUT_SEC) -> CandidateCallResult:
    request = json.dumps({"source": source}, ensure_ascii=False, separators=(",", ":"))
    return _call_result(run_candidate(["script"], input_text=request, timeout_sec=timeout_sec))


def metadata_requires(distribution: str) -> CandidateCallResult:
    return _call_result(run_candidate(["metadata-requires", distribution]))


def run_module(
    module: str, arguments: list[str], *, input_text: str | None = None
) -> CandidateProcessResult:
    return run_candidate(["module", module, *arguments], input_text=input_text)


def run_console(name: str, arguments: list[str]) -> CandidateProcessResult:
    return run_candidate(["console", name, *arguments])
