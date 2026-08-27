"""Trusted hidden-test client for isolated candidate operations."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

from .candidate_install import MAX_INSTALL_BYTES, MAX_INSTALL_ENTRIES, tree_usage
from .candidate_runner import MAX_OUTPUT_BYTES, RESULT_PREFIX
from .process_cleanup import terminate_uid_processes

CANDIDATE_UID = 10001
CANDIDATE_SITE = "/tmp/candidate-site"
DEFAULT_TIMEOUT_SEC = 10.0
DEFAULT_TOTAL_TIMEOUT_SEC = 300.0
_TOTAL_TIMEOUT_SEC = float(
    os.environ.get("NL2REPO_CANDIDATE_TOTAL_TIMEOUT_SEC", DEFAULT_TOTAL_TIMEOUT_SEC)
)
_CANDIDATE_DEADLINE = time.monotonic() + _TOTAL_TIMEOUT_SEC


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


def _command(arguments: list[str]) -> list[str]:
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/home/candidate",
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
        "/usr/local/bin/python",
        "-I",
        "-B",
        "-m",
        "nl2repobench.verification.candidate_runner",
        "--candidate-site",
        CANDIDATE_SITE,
        *arguments,
    ]
    dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    if dependency_root:
        command.insert(6, f"NL2REPO_CANDIDATE_DEPENDENCIES={dependency_root}")
    return command


def _read_bounded(handle: BinaryIO) -> str:
    handle.seek(0)
    data = handle.read(MAX_OUTPUT_BYTES + 1)
    if len(data) > MAX_OUTPUT_BYTES:
        raise RuntimeError("candidate output exceeds size limit")
    return data.decode("utf-8", errors="replace")


def run_candidate(
    arguments: list[str],
    *,
    input_text: str | None = None,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
) -> CandidateProcessResult:
    remaining_sec = _CANDIDATE_DEADLINE - time.monotonic()
    if remaining_sec <= 0:
        return CandidateProcessResult(
            returncode=124,
            stdout="",
            stderr="candidate cumulative execution budget exhausted",
        )
    effective_timeout_sec = min(timeout_sec, remaining_sec)
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen(
            _command(arguments),
            stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
            text=True,
        )
        try:
            process.communicate(input=input_text, timeout=effective_timeout_sec)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            timed_out = True
        else:
            timed_out = False
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            terminate_uid_processes(CANDIDATE_UID)
            entries, total_bytes = tree_usage(
                (
                    Path("/tmp/candidate"),
                    Path(CANDIDATE_SITE),
                    Path("/tmp/candidate-build"),
                )
            )
            if entries > MAX_INSTALL_ENTRIES or total_bytes > MAX_INSTALL_BYTES:
                raise RuntimeError("candidate storage exceeds verifier limit")
        return CandidateProcessResult(
            returncode=124 if timed_out else process.returncode,
            stdout=_read_bounded(stdout),
            stderr=_read_bounded(stderr),
        )


def call(
    module: str,
    attribute: str,
    *args: Any,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    **kwargs: Any,
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
    completed = run_candidate(["call"], input_text=request, timeout_sec=timeout_sec)
    lines = [line for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if completed.returncode != 0 or len(lines) != 1:
        return CandidateCallResult(
            ok=False,
            exception_type="CandidateProcessError",
            exception_message=(completed.stderr or completed.stdout or "no response")[-2000:],
        )
    try:
        payload = json.loads(lines[0][len(RESULT_PREFIX) :])
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return CandidateCallResult(
            ok=False,
            exception_type="CandidateProtocolError",
            exception_message=str(exc),
        )
    return CandidateCallResult(
        ok=payload.get("ok") is True,
        value=payload.get("value"),
        exception_type=payload.get("exception_type"),
        exception_message=payload.get("exception_message"),
    )


def get(module: str, attribute: str) -> CandidateCallResult:
    request = json.dumps(
        {
            "args": [],
            "attribute": attribute,
            "kwargs": {},
            "module": module,
            "operation": "get",
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    completed = run_candidate(["call"], input_text=request)
    lines = [line for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if completed.returncode != 0 or len(lines) != 1:
        return CandidateCallResult(
            ok=False,
            exception_type="CandidateProcessError",
            exception_message=(completed.stderr or completed.stdout or "no response")[-2000:],
        )
    payload = json.loads(lines[0][len(RESULT_PREFIX) :])
    return CandidateCallResult(
        ok=payload.get("ok") is True,
        value=payload.get("value"),
        exception_type=payload.get("exception_type"),
        exception_message=payload.get("exception_message"),
    )


def execute_script(source: str, *, timeout_sec: float = DEFAULT_TIMEOUT_SEC) -> CandidateCallResult:
    """Run a trusted scenario as the unprivileged candidate user."""

    request = json.dumps({"source": source}, ensure_ascii=False, separators=(",", ":"))
    completed = run_candidate(["script"], input_text=request, timeout_sec=timeout_sec)
    lines = [line for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if completed.returncode != 0 or len(lines) != 1:
        return CandidateCallResult(
            ok=False,
            exception_type="CandidateProcessError",
            exception_message=(completed.stderr or completed.stdout or "no response")[-2000:],
        )
    try:
        payload = json.loads(lines[0][len(RESULT_PREFIX) :])
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return CandidateCallResult(
            ok=False,
            exception_type="CandidateProtocolError",
            exception_message=str(exc),
        )
    return CandidateCallResult(
        ok=payload.get("ok") is True,
        value=payload.get("value"),
        exception_type=payload.get("exception_type"),
        exception_message=payload.get("exception_message"),
    )


def metadata_requires(distribution: str) -> CandidateCallResult:
    completed = run_candidate(["metadata-requires", distribution])
    lines = [line for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if completed.returncode != 0 or len(lines) != 1:
        return CandidateCallResult(
            ok=False,
            exception_type="CandidateProcessError",
            exception_message=(completed.stderr or completed.stdout or "no response")[-2000:],
        )
    payload = json.loads(lines[0][len(RESULT_PREFIX) :])
    return CandidateCallResult(
        ok=payload.get("ok") is True,
        value=payload.get("value"),
        exception_type=payload.get("exception_type"),
        exception_message=payload.get("exception_message"),
    )


def run_module(
    module: str,
    arguments: list[str],
    *,
    input_text: str | None = None,
) -> CandidateProcessResult:
    return run_candidate(["module", module, *arguments], input_text=input_text)


def run_console(name: str, arguments: list[str]) -> CandidateProcessResult:
    return run_candidate(["console", name, *arguments])
