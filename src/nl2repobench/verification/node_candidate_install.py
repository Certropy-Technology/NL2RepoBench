"""Bounded, allowlisted npm candidate installation supervisor."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from nl2repobench.harbor.node_dependencies import NodeDependencyError, validate_npm_package_tarball
from nl2repobench.storage.files import atomic_write

from .process_cleanup import terminate_uid_processes

CANDIDATE_FAILURE_EXIT = 71
INTERNAL_ERROR_EXIT = 70
MAX_OUTPUT_BYTES = 256 * 1024
MAX_CANDIDATE_TARBALL_BYTES = 512 * 1024 * 1024
NPM_EXECUTABLE = "/usr/local/bin/npm"


def sanitized_node_environment(*, cache: Path, tmpdir: Path) -> dict[str, str]:
    """Return a minimal environment with loader and registry controls removed."""

    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": "/tmp/candidate-home",
        "TMPDIR": str(tmpdir),
        "npm_config_cache": str(cache),
        "npm_config_ignore_scripts": "true",
        "npm_config_offline": "true",
        "npm_config_audit": "false",
        "npm_config_fund": "false",
    }


def _check_directory(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"{label} must be a regular directory")
    if not path.resolve().is_relative_to(path.resolve().parent):
        raise ValueError(f"{label} path is invalid")


def npm_ci_command(source: Path, cache: Path) -> list[str]:
    return [
        NPM_EXECUTABLE,
        "ci",
        "--offline",
        "--ignore-scripts",
        "--no-audit",
        "--no-fund",
        f"--cache={cache}",
        "--prefix",
        str(source),
    ]


def npm_pack_command(source: Path, destination: Path) -> list[str]:
    return [
        NPM_EXECUTABLE,
        "pack",
        "--ignore-scripts",
        "--pack-destination",
        str(destination),
    ]


def npm_install_tar_command(tarball: Path, target: Path, cache: Path) -> list[str]:
    return [
        NPM_EXECUTABLE,
        "install",
        str(tarball),
        "--offline",
        "--ignore-scripts",
        "--no-audit",
        "--no-fund",
        f"--cache={cache}",
        "--prefix",
        str(target),
    ]


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str], timeout_sec: float
) -> dict[str, Any]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        text=False,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()
        return {
            "outcome": "timeout",
            "returncode": CANDIDATE_FAILURE_EXIT,
            "stdout": stdout[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"),
            "stderr": stderr[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"),
        }
    return {
        "outcome": "success" if process.returncode == 0 else "failed",
        "returncode": process.returncode,
        "stdout": stdout[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"),
        "stderr": stderr[:MAX_OUTPUT_BYTES].decode("utf-8", "replace"),
    }


def install_candidate(
    source: Path,
    target: Path,
    *,
    cache: Path = Path("/opt/npm-cache"),
    timeout_sec: float = 90.0,
) -> dict[str, Any]:
    """Run the three fixed npm commands with lifecycle scripts disabled."""

    _check_directory(source, "candidate source")
    if target.exists() and (target.is_symlink() or not target.is_dir()):
        raise ValueError("candidate target must be a regular directory")
    target.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="node-pack-") as temporary:
        pack_root = Path(temporary)
        env = sanitized_node_environment(cache=cache, tmpdir=pack_root)
        ci = _run(npm_ci_command(source, cache), cwd=source, env=env, timeout_sec=timeout_sec)
        if ci["returncode"] != 0:
            return {"outcome": "install-failed", "steps": [ci]}
        packed = _run(
            npm_pack_command(source, pack_root), cwd=source, env=env, timeout_sec=timeout_sec
        )
        if packed["returncode"] != 0:
            return {"outcome": "pack-failed", "steps": [ci, packed]}
        tarballs = sorted(pack_root.glob("*.tgz"))
        if len(tarballs) != 1 or tarballs[0].stat().st_size > MAX_CANDIDATE_TARBALL_BYTES:
            return {
                "outcome": "pack-failed",
                "steps": [ci, packed],
                "reason": "invalid tarball output",
            }
        try:
            validate_npm_package_tarball(tarballs[0])
        except NodeDependencyError as exc:
            return {"outcome": "pack-rejected", "steps": [ci, packed], "reason": str(exc)}
        installed = _run(
            npm_install_tar_command(tarballs[0], target, cache),
            cwd=source,
            env=env,
            timeout_sec=timeout_sec,
        )
        if installed["returncode"] != 0:
            return {"outcome": "package-install-failed", "steps": [ci, packed, installed]}
        terminate_uid_processes(10001)
        return {"outcome": "success", "steps": [ci, packed, installed]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path("/opt/npm-cache"))
    parser.add_argument("--timeout-sec", type=float, default=90.0)
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = install_candidate(
            args.source, args.target, cache=args.cache, timeout_sec=args.timeout_sec
        )
        atomic_write(args.status, json.dumps(result, sort_keys=True).encode() + b"\n")
    except Exception as exc:
        result = {"outcome": "internal-error", "reason": str(exc)}
        atomic_write(args.status, json.dumps(result, sort_keys=True).encode() + b"\n")
        raise SystemExit(INTERNAL_ERROR_EXIT) from exc
    if result.get("outcome") != "success":
        raise SystemExit(CANDIDATE_FAILURE_EXIT)
