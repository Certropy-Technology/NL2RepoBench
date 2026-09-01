"""JSON-only subprocess boundary for Node candidate exports."""

from __future__ import annotations

import base64
import binascii
import json
import os
import re
import secrets
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .subprocess_supervisor import CANDIDATE_GID, CANDIDATE_UID, SCHEMA_VERSION

MAX_REQUEST_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 256 * 1024
MAX_ARGS = 32
NODE_RUNTIME_ROOT = Path("/opt/nl2repobench-node")
NODE_EXECUTABLE = str(NODE_RUNTIME_ROOT / "bin/node")
NODE_RUNNER = str(NODE_RUNTIME_ROOT / "lib/candidate_runner.mjs")
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.@/-]{1,128}$")


@dataclass(frozen=True)
class NodeCandidateResult:
    ok: bool
    value: Any = None
    exception_type: str | None = None
    message: str | None = None
    returncode: int = 0


@dataclass(frozen=True)
class NodeProcessResult:
    returncode: int
    stdout: bytes = b""
    stderr: bytes = b""
    verifier_invalid: bool = False


def sanitized_environment(*, home: Path, tmpdir: Path) -> dict[str, str]:
    """Build a clean environment; loader, registry, and proxy variables are absent."""

    return {
        "HOME": str(home),
        "TMPDIR": str(tmpdir),
    }


def _validate_request(package: str, export: str, args: list[Any]) -> bytes:
    if not NAME_PATTERN.fullmatch(package) or not NAME_PATTERN.fullmatch(export):
        raise ValueError("package and export names are not allowlisted")
    if len(args) > MAX_ARGS:
        raise ValueError("too many candidate arguments")
    payload = json.dumps(
        {"package": package, "export": export, "args": args}, separators=(",", ":")
    )
    encoded = payload.encode("utf-8")
    if len(encoded) > MAX_REQUEST_BYTES:
        raise ValueError("candidate request exceeds the size limit")
    return encoded


def _common_root(*paths: Path) -> Path:
    try:
        common = Path(os.path.commonpath([str(path.resolve()) for path in paths]))
    except (OSError, ValueError) as exc:
        raise ValueError("Node operation paths do not share a safe root") from exc
    if not common.is_dir() or common.is_symlink():
        raise ValueError("Node operation root is unavailable")
    return common


def _make_supervisor_request(
    command: list[str],
    *,
    cwd: Path,
    write_root: Path,
    timeout_sec: float,
    stdin_data: bytes,
    environment: dict[str, str],
    context: str,
) -> tuple[bytes, str]:
    if context not in {"call", "install"}:
        raise ValueError("invalid Node supervisor context")
    executable = Path(command[0])
    if not executable.is_absolute() or executable.is_symlink() or not executable.is_file():
        raise ValueError("Node executable must be a dedicated regular file")
    staging_root = _common_root(cwd, write_root)
    relative_cwd = cwd.resolve().relative_to(staging_root).as_posix() or "."
    request_id = secrets.token_hex(16)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "context": context,
        "command": {
            "argv": command,
            "cwd": relative_cwd,
            "environment": [[name, value] for name, value in sorted(environment.items())],
        },
        "limits": {
            "timeout_sec": timeout_sec,
            "cpu_sec": max(1, int(timeout_sec)),
            "max_stdin_bytes": 1 * 1024 * 1024,
            "max_output_bytes": 8 * 1024 * 1024,
            "max_file_bytes": 512 * 1024 * 1024,
            "max_open_files": 256,
            "uid": CANDIDATE_UID,
            "gid": CANDIDATE_GID,
            "max_processes": 64,
        },
        "policy": {
            "task_id": "node-candidate",
            "staging_root": str(staging_root),
            "read_only_roots": [str(NODE_RUNTIME_ROOT)],
            "write_root": str(write_root.resolve()),
            "allowed_executable_roots": [str(NODE_RUNTIME_ROOT / "bin")],
            "allowed_environment_names": sorted({"HOME", "TMPDIR", *environment}),
            "require_no_new_privs": True,
            "require_empty_capabilities": True,
        },
        "stdin_base64": base64.b64encode(stdin_data).decode("ascii"),
    }
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        request_id,
    )


def _decode_supervisor_response(raw: bytes, *, expected_request_id: str) -> NodeProcessResult:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Node supervisor response is malformed") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Node supervisor response schema is invalid")
    if payload.get("request_id") != expected_request_id:
        raise ValueError("Node supervisor response request_id does not match")
    returncode = payload.get("returncode")
    if not isinstance(returncode, int) or isinstance(returncode, bool):
        raise ValueError("Node supervisor returncode is invalid")
    for key in ("timed_out", "output_limit_exceeded", "cleanup_complete"):
        if not isinstance(payload.get(key), bool):
            raise ValueError("Node supervisor result flags are invalid")
    try:
        stdout = base64.b64decode(
            str(payload.get("stdout_base64", "")).encode("ascii"), validate=True
        )
        stderr = base64.b64decode(
            str(payload.get("stderr_base64", "")).encode("ascii"), validate=True
        )
    except (ValueError, binascii.Error, UnicodeEncodeError) as exc:
        raise ValueError("Node supervisor output is not valid base64") from exc
    if len(stdout) > 8 * 1024 * 1024 or len(stderr) > 8 * 1024 * 1024:
        raise ValueError("Node supervisor output exceeds the bound")
    if payload.get("spawn_error") is not None or payload.get("cleanup_error") is not None:
        return NodeProcessResult(70, stdout, stderr, verifier_invalid=True)
    if not payload["cleanup_complete"]:
        return NodeProcessResult(70, stdout, stderr, verifier_invalid=True)
    result_code = 124 if payload["timed_out"] else (
        125 if payload["output_limit_exceeded"] else returncode
    )
    return NodeProcessResult(result_code, stdout, stderr)


def run_node_command(
    command: list[str],
    *,
    cwd: Path,
    write_root: Path,
    timeout_sec: float,
    stdin_data: bytes = b"",
    environment: dict[str, str] | None = None,
    context: str = "install",
) -> NodeProcessResult:
    """Submit one fixed Node command to the shared candidate supervisor."""

    request, request_id = _make_supervisor_request(
        command,
        cwd=cwd,
        write_root=write_root,
        timeout_sec=timeout_sec,
        stdin_data=stdin_data,
        environment=environment or {},
        context=context,
    )
    runtime_root = "/opt/nl2repobench-runtime"
    bootstrap = (
        "import sys;sys.path.insert(0, "
        + repr(runtime_root)
        + ");from nl2repobench.verification.candidate_process_cli import main;"
        + "raise SystemExit(main())"
    )
    try:
        transport = subprocess.run(
            ["/usr/local/bin/python3", "-I", "-B", "-c", bootstrap],
            input=request,
            capture_output=True,
            cwd=str(cwd),
            env={
                "PATH": "/usr/bin:/bin",
                "HOME": "/nonexistent",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            timeout=timeout_sec + 5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return NodeProcessResult(124, stderr=b"Node supervisor transport timed out")
    if transport.returncode in {64, 70, 75} or transport.returncode != 0:
        return NodeProcessResult(
            70, transport.stdout, transport.stderr, verifier_invalid=True
        )
    try:
        return _decode_supervisor_response(transport.stdout, expected_request_id=request_id)
    except ValueError as exc:
        return NodeProcessResult(70, transport.stdout, str(exc).encode(), verifier_invalid=True)


def run_candidate(
    candidate_site: Path,
    request: bytes,
    *,
    timeout_sec: float = 30.0,
    node_executable: str = NODE_EXECUTABLE,
) -> NodeCandidateResult:
    if candidate_site.is_symlink() or not candidate_site.is_dir():
        return NodeCandidateResult(False, message="candidate site is unavailable", returncode=70)
    if len(request) > MAX_REQUEST_BYTES:
        return NodeCandidateResult(
            False, message="candidate request exceeds the size limit", returncode=64
        )
    if Path(node_executable).is_symlink() or not Path(node_executable).is_file():
        return NodeCandidateResult(False, message="Node executable is unavailable", returncode=70)
    if Path(NODE_RUNNER).is_symlink() or not Path(NODE_RUNNER).is_file():
        return NodeCandidateResult(False, message="Node runner is unavailable", returncode=70)
    environment = sanitized_environment(
        home=candidate_site / ".home", tmpdir=candidate_site / ".tmp"
    )
    try:
        completed = run_node_command(
            [node_executable, "--no-addons", NODE_RUNNER],
            cwd=candidate_site,
            write_root=candidate_site,
            timeout_sec=timeout_sec,
            stdin_data=request + b"\n",
            environment=environment,
            context="call",
        )
    except (OSError, ValueError) as exc:
        return NodeCandidateResult(False, message=str(exc), returncode=70)
    if completed.returncode == 124:
        return NodeCandidateResult(False, message="candidate call timed out", returncode=124)
    if len(completed.stdout) > MAX_RESPONSE_BYTES or completed.returncode == 125:
        return NodeCandidateResult(
            False, message="candidate output exceeds the size limit", returncode=70
        )
    try:
        payload = json.loads(completed.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return NodeCandidateResult(False, message="candidate response is malformed", returncode=70)
    if not isinstance(payload, dict) or not isinstance(payload.get("ok"), bool):
        return NodeCandidateResult(
            False, message="candidate response violates the protocol", returncode=70
        )
    if payload["ok"]:
        return NodeCandidateResult(
            True, value=payload.get("value"), returncode=completed.returncode
        )
    return NodeCandidateResult(
        False,
        exception_type=payload.get("exception_type"),
        message=payload.get("message") or payload.get("error"),
        returncode=completed.returncode,
    )


def call(
    package: str,
    export: str,
    *args: Any,
    candidate_site: Path = Path("/tmp/candidate-site"),
    timeout_sec: float = 30.0,
) -> NodeCandidateResult:
    request = _validate_request(package, export, list(args))
    return run_candidate(candidate_site, request, timeout_sec=timeout_sec)
