#!/usr/bin/env python3
"""Trusted custom-json-v1 driver for the fastvector task.

This process never imports candidate code. It launches the adapter as uid 10001
in a child process (``python -I``) and prints exactly one line of JSON:

    {"schema_version": "1.0", "leaves": [{"id": ..., "status": ...}, ...]}

``len(leaves)`` always equals the frozen denominator (36), so an adapter crash,
timeout or import failure degrades to 36 failed leaves rather than a collection
mismatch. Runs fully offline and deterministically.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cases import CASES  # noqa: E402

VERIFIER_DIR = Path(__file__).resolve().parent
CANDIDATE_SITE = "/tmp/candidate-site"
DEPENDENCY_SITE = "/opt/candidate-dependencies/site"
ADAPTER_TIMEOUT_SEC = 120.0
LOG_DIR = Path("/logs/verifier")
# /tests/verifier is installed 0500 root-only, so uid 10001 cannot read the
# adapter in place. Stage it in a root-owned directory that is world-readable
# but not candidate-writable: the candidate can run it and cannot swap it.
ADAPTER_STAGE = Path("/tmp/verifier-adapter")


def _stage_adapter() -> Path:
    shutil.rmtree(ADAPTER_STAGE, ignore_errors=True)
    ADAPTER_STAGE.mkdir(parents=True)
    os.chown(ADAPTER_STAGE, 0, 0)
    os.chmod(ADAPTER_STAGE, 0o755)
    staged = ADAPTER_STAGE / "client.py"
    shutil.copyfile(VERIFIER_DIR / "client.py", staged)
    os.chown(staged, 0, 0)
    os.chmod(staged, 0o444)
    return staged


def _run_adapter() -> tuple[dict[str, bool], str]:
    try:
        adapter = _stage_adapter()
    except OSError as exc:
        return {}, f"adapter-stage-failed: {type(exc).__name__}: {exc}"
    request = {
        # python -I ignores PYTHONPATH, so the adapter is told both roots.
        "sys_path": [CANDIDATE_SITE, DEPENDENCY_SITE],
        "cases": [dict(case) for case in CASES],
    }
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp/candidate-build/home",
        "PYTHONDONTWRITEBYTECODE=1",
        sys.executable,
        "-I",
        "-B",
        str(adapter),
    ]
    try:
        completed = subprocess.run(
            command,
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=ADAPTER_TIMEOUT_SEC,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {}, f"adapter-launch-failed: {type(exc).__name__}"

    stderr_tail = completed.stderr[-4000:]
    if completed.returncode != 0:
        return {}, f"adapter-exit-{completed.returncode}: {stderr_tail}"
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        return {}, f"adapter-empty-output: {stderr_tail}"
    try:
        response = json.loads(lines[-1])
    except json.JSONDecodeError:
        return {}, f"adapter-bad-json: {stderr_tail}"
    if not response.get("ok"):
        return {}, f"candidate-import-failed: {response.get('error', 'unknown')}"
    outcomes = response.get("outcomes")
    if not isinstance(outcomes, dict):
        return {}, "adapter-bad-outcomes"
    detail = json.dumps(response.get("errors", {}), sort_keys=True)[:4000]
    return {str(k): bool(v) for k, v in outcomes.items()}, detail


def main() -> None:
    outcomes, detail = _run_adapter()
    leaves = [
        {"id": str(case["id"]), "status": "passed" if outcomes.get(case["id"]) else "failed"}
        for case in CASES
    ]
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (LOG_DIR / "adapter-detail.txt").write_text(detail, encoding="utf-8")
    except OSError:
        pass
    json.dump({"schema_version": "1.0", "leaves": leaves}, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
