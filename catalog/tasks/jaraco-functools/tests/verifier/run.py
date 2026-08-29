from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED_TOTAL = 35
CASE_TIMEOUT_SEC = 12.0
CANDIDATE_USER = "candidate"
ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / "adapter.py"
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
SCENARIOS = (
    "compose",
    "compose-empty",
    "once",
    "once-reset",
    "method-cache",
    "method-cache-clear",
    "special-cache",
    "decorators",
    "invoke",
    "method-caller",
    "throttler",
    "throttler-descriptor",
    "first-invoke",
    "retry-call",
    "retry-failure",
    "retry-infinite",
    "retry-defaults",
    "retry-decorator",
    "print-yielded",
    "simple-helpers",
    "assign-params",
    "assign-missing",
    "save-method-args",
    "except-replace",
    "except-use",
    "except-untrapped",
    "identity",
    "bypass-when",
    "bypass-callable",
    "bypass-unless",
    "splat",
    "chainable",
    "chainable-error",
    "noop",
    "metadata",
)


def _invoke(adapter: Path, scenario: str, workspace: Path) -> dict[str, object]:
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
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        "NL2REPO_CANDIDATE_DEPENDENCIES=/opt/candidate-dependencies/site",
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        scenario,
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=CASE_TIMEOUT_SEC, check=False
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "exception_type": "VerifierTimeout",
            "exception_message": "scenario timed out",
        }
    except OSError as exc:
        return {
            "ok": False,
            "exception_type": "VerifierProcessError",
            "exception_message": str(exc),
        }
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode not in (0, 1) or len(lines) != 1:
        return {
            "ok": False,
            "exception_type": "CandidateProcessError",
            "exception_message": (completed.stderr or completed.stdout)[-1200:],
        }
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": str(exc),
        }
    return (
        value
        if isinstance(value, dict)
        else {
            "ok": False,
            "exception_type": "CandidateProtocolError",
            "exception_message": "response is not an object",
        }
    )


def main() -> int:
    if len(SCENARIOS) != EXPECTED_TOTAL or len(set(SCENARIOS)) != EXPECTED_TOTAL:
        raise RuntimeError("scenario denominator mismatch")
    leaves = []
    with tempfile.TemporaryDirectory(prefix="jaraco-functools-verifier-") as directory:
        workspace = Path(directory)
        shutil.chown(workspace, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(workspace, 0o700)
        adapter = workspace / "adapter.py"
        adapter.write_bytes(ADAPTER.read_bytes())
        shutil.chown(adapter, CANDIDATE_USER, CANDIDATE_USER)
        os.chmod(adapter, 0o500)
        for scenario in SCENARIOS:
            actual = _invoke(adapter, scenario, workspace)
            expected = EXPECTED[scenario]
            passed = actual.get("ok") is True and actual.get("value") == expected
            leaf = {
                "id": f"jaraco-functools/{scenario}",
                "status": "passed" if passed else "failed",
            }
            if not passed:
                leaf["message"] = json.dumps(
                    {"actual": actual, "expected": expected}, sort_keys=True
                )[:1000]
            leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


EXPECTED = {
    "compose": {"values": [7, 6]},
    "compose-empty": {"failure": ["builtins.TypeError"]},
    "once": {"calls": [2, 4], "saved": 8, "values": [4, 4, 8]},
    "once-reset": {"calls": [1, 3], "saved": 6, "values": [2, 2, 6]},
    "method-cache": {"calls": [1, 1], "values": [20, 20, 20]},
    "method-cache-clear": {"calls": 2, "values": [20, 20, 20]},
    "special-cache": {"calls": [1, 1], "values": [3, 3, "answer", "answer"]},
    "decorators": {
        "apply": "HELLO",
        "doc": "kept",
        "events": ["value", 7],
        "invoke": 7,
        "passthrough": "value",
    },
    "invoke": {"count": 1, "events": ["called"], "same": True},
    "method-caller": {
        "result": "HELLO",
        "warning_category": "DeprecationWarning",
        "warning_message": (
            "`jaraco.functools.method_caller` is deprecated, "
            "use `operator.methodcaller` instead"
        ),
    },
    "throttler": {"func_unwrapped": True, "last_called": True, "rate": 4, "value": 3},
    "throttler-descriptor": {"last_called": True, "value": "ok"},
    "first-invoke": {"events": ["first", "second"], "value": "second"},
    "retry-call": {"attempts": 3, "cleanup": [1, 2], "result": "ok"},
    "retry-failure": {"failure": ["builtins.KeyError", "'bad'", 3]},
    "retry-infinite": {"attempts": 4, "cleanup": [1, 2, 3], "result": "ok"},
    "retry-defaults": {"calls": 1, "failure": ["builtins.ValueError", "untrapped"]},
    "retry-decorator": {"attempts": 2, "doc": "action", "result": "done"},
    "print-yielded": {"output": ["2", "None", "three"], "result": None},
    "simple-helpers": {
        "calls": ["x"],
        "none": None,
        "none_as": ["fallback", "value"],
        "signed": ["+3.5", "-3.5", "0.0"],
        "value": None,
    },
    "assign-params": {"partial_name": "func", "value": [8, 5]},
    "assign-missing": {"failure": ["builtins.TypeError"]},
    "save-method-args": {"args": [1, 2], "kwargs": {"label": "x"}, "result": 3},
    "except-replace": {"invalid": 0, "valid": 7},
    "except-use": {"invalid": "bad", "valid": 7},
    "except-untrapped": {"failure": ["builtins.KeyError", "'nope'"]},
    "identity": {"same": True, "text": "x"},
    "bypass-when": {"after": 3, "before": 6},
    "bypass-callable": {"after": 4, "before": 8},
    "bypass-unless": {"first": 6, "second": 3},
    "splat": {"mapping": "c:d", "tuple": "a:b"},
    "chainable": {"same": True, "values": [1, 2]},
    "chainable-error": {"failure": ["builtins.AssertionError", ""]},
    "noop": {"value": None},
    "metadata": {"doc": "sample documentation", "name": "sample"},
}


if __name__ == "__main__":
    raise SystemExit(main())
