from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCENARIOS: dict[str, Any] = {
    "exports": True,
    "delayed-sequential": [0, 1, 4, 9, 16],
    "thread-backend": [1, 2, 3, 4],
    "sequential-config": ["0", "1", "2"],
    "generator-order": [10, 11, 12],
    "backend-invalid": "builtins.ValueError",
    "parallel-error": "builtins.ValueError",
    "dump-load": {"a": 1, "b": [2, 3]},
    "dump-load-zlib": list(range(100)),
    "dump-load-gzip": {"value": "gzip"},
    "dump-file-object": {"result": None, "value": [1, "two"]},
    "numpy-roundtrip": {"shape": [3, 4], "dtype": "float64", "sum": 66.0},
    "numpy-mmap": {"type": "memmap", "values": [0, 1, 2, 3, 4, 5]},
    "numpy-compressed-mmap": {"type": "ndarray", "values": [0, 1, 2, 3], "warning": True},
    "hash-dict-order": True,
    "hash-set-order": True,
    "hash-numpy": True,
    "hash-invalid-method": "builtins.ValueError",
    "memory-cache": {"values": [49, 49], "calls": 1},
    "memory-cache-check": [False, True],
    "memory-clear": 2,
    "memory-kwargs": {"values": [5, 5], "calls": 1},
    "memory-ignore": {"values": [3, 3], "calls": 1},
    "memory-exception-recompute": {"value": 4, "calls": 2},
    "memstr": [1024, 2 * 1024**2, 3 * 1024**3, 4 * 1024, 512],
    "memstr-invalid": "builtins.ValueError",
    "effective-n-jobs": [1, True, True],
    "wrap-non-picklable": 12,
    "register-compressor-invalid": "builtins.ValueError",
    "testing-success": True,
    "testing-failure": "builtins.ValueError",
    "parallel-config-invalid": "builtins.ValueError",
    "memory-pathlib": True,
}


ADAPTER_PATH: Path | None = None


def invoke(name: str) -> dict[str, Any]:
    if ADAPTER_PATH is None:
        return {"ok": False, "exception_type": "VerifierSetupError"}
    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp",
        "TMPDIR=/tmp",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        sys.executable,
        "-I",
        "-B",
        str(ADAPTER_PATH),
        "--candidate-site",
        "/tmp/candidate-site",
        "--dependency-site",
        "/opt/candidate-dependencies/site",
        "--scenario",
        name,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return result if isinstance(result, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    global ADAPTER_PATH
    staged_adapter = Path(tempfile.gettempdir()) / "joblib-verifier-adapter.py"
    shutil.copyfile(Path(__file__).with_name("adapter.py"), staged_adapter)
    os.chmod(staged_adapter, 0o555)
    ADAPTER_PATH = staged_adapter
    leaves = []
    for name, expected in SCENARIOS.items():
        result = invoke(name)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        passed = actual == expected
        leaves.append({
            "id": f"joblib/{name}",
            "status": "passed" if passed else "failed",
            "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1000],
        })
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
