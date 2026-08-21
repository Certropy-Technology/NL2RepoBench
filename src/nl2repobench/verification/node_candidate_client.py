"""JSON-only subprocess boundary for Node candidate exports."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_REQUEST_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 256 * 1024
MAX_ARGS = 32
NODE_EXECUTABLE = "/usr/local/bin/node"
RUNNER_NAME = "candidate_runner.mjs"
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.@/-]{1,128}$")
REMOVED_ENVIRONMENT = {
    "NODE_PATH",
    "NODE_OPTIONS",
    "NODE_EXTRA_CA_CERTS",
    "NPM_CONFIG_USERCONFIG",
    "npm_config_userconfig",
    "npm_config_registry",
    "npm_config_proxy",
    "npm_config_https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "LD_PRELOAD",
}


@dataclass(frozen=True)
class NodeCandidateResult:
    ok: bool
    value: Any = None
    exception_type: str | None = None
    message: str | None = None
    returncode: int = 0


def sanitized_environment(*, home: Path, tmpdir: Path) -> dict[str, str]:
    """Build a clean environment; loader, registry, and proxy variables are absent."""

    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
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
    runner = Path(__file__).with_name("node") / RUNNER_NAME
    env = sanitized_environment(home=candidate_site / ".home", tmpdir=candidate_site / ".tmp")
    try:
        completed = subprocess.run(
            [node_executable, "--no-addons", str(runner)],
            input=request + b"\n",
            cwd=candidate_site,
            env=env,
            capture_output=True,
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return NodeCandidateResult(False, message="candidate call timed out", returncode=124)
    stdout = completed.stdout[:MAX_RESPONSE_BYTES]
    if len(completed.stdout) > MAX_RESPONSE_BYTES:
        return NodeCandidateResult(
            False, message="candidate output exceeds the size limit", returncode=70
        )
    try:
        payload = json.loads(stdout)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return NodeCandidateResult(
            False, message="candidate response is malformed", returncode=completed.returncode
        )
    if not isinstance(payload, dict) or not isinstance(payload.get("ok"), bool):
        return NodeCandidateResult(
            False,
            message="candidate response violates the protocol",
            returncode=completed.returncode,
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
