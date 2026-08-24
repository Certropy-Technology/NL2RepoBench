"""Private custom-json-v1 verifier for the GraphNeuralNetwork hidden slice.

This entrypoint is trusted: it never imports candidate code. Each leaf runs
``adapter.py`` in a child process as the unprivileged ``candidate`` user and
reads back a small JSON verdict file that the child owns. Only an allowlisted
case name crosses the process boundary, never Python source, import paths or
shell fragments.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED_TOTAL = 4
CANDIDATE_USER = "candidate"
CANDIDATE_SITE = "/tmp/candidate-site"
DEPENDENCY_SITE = os.environ.get(
    "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
)
CASE_TIMEOUT_SEC = 300.0
ADAPTER = Path(__file__).resolve().parent / "adapter.py"
# runuser lives in /usr/sbin, which is not always on root's PATH in slim images.
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"

# Allowlisted leaf identifiers. The adapter resolves each name through its own
# in-process mapping, so the boundary only ever carries one of these tokens.
CASES = (
    "data-pipeline-and-splits",
    "gcn-featureless-training",
    "gat-multihead-attention-training",
    "graphsage-mean-aggregator-training",
)


def _run_case(case: str, workspace: Path, adapter: Path) -> tuple[str, str | None]:
    verdict_path = workspace / f"{case}.json"
    command = [
        RUNUSER,
        "-u",
        CANDIDATE_USER,
        "--",
        "env",
        f"HOME={workspace}",
        f"TMPDIR={workspace}",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "LANG=C.UTF-8",
        "PYTHONDONTWRITEBYTECODE=1",
        "TF_CPP_MIN_LOG_LEVEL=3",
        "TF_ENABLE_ONEDNN_OPTS=0",
        "CUDA_VISIBLE_DEVICES=-1",
        f"NL2REPO_CANDIDATE_SITE={CANDIDATE_SITE}",
        f"NL2REPO_CANDIDATE_DEPENDENCIES={DEPENDENCY_SITE}",
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        "--case",
        case,
        "--output",
        str(verdict_path),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=CASE_TIMEOUT_SEC,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "failed", f"case timed out after {CASE_TIMEOUT_SEC:.0f}s"
    except OSError as exc:
        return "failed", f"child process error: {exc}"
    if not verdict_path.is_file():
        detail = (completed.stderr or completed.stdout)[-900:]
        return "failed", f"child exit {completed.returncode} without a verdict: {detail}"
    try:
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "failed", f"verdict was not readable JSON: {exc}"
    if not isinstance(verdict, dict) or verdict.get("status") not in {"passed", "failed"}:
        return "failed", "verdict did not carry a known status"
    if verdict["status"] != "passed":
        message = verdict.get("message")
        return "failed", str(message)[-900:] if message else "case reported failure"
    return "passed", None


def main() -> int:
    leaves: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="gnn-verifier-") as temporary:
        workspace = Path(temporary)
        # The adapter writes its verdict as the candidate user, so the shared
        # scratch directory has to be writable by that account.
        shutil.chown(workspace, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(workspace, 0o700)
        # The compiler installs /tests/verifier as root-only (0500), so the
        # adapter is staged into the candidate-owned scratch directory. Trusted
        # bytes are copied by this process; the child never chooses the path.
        adapter = workspace / "adapter.py"
        adapter.write_bytes(ADAPTER.read_bytes())
        shutil.chown(adapter, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(adapter, 0o500)
        for case in CASES:
            status, message = _run_case(case, workspace, adapter)
            leaf = {"id": case, "status": status}
            if message:
                leaf["message"] = message
            leaves.append(leaf)
    if len(leaves) != EXPECTED_TOTAL or len({leaf["id"] for leaf in leaves}) != EXPECTED_TOTAL:
        leaves = [{"id": case, "status": "failed"} for case in CASES]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
