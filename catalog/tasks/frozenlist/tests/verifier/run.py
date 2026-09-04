from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
RESULT_PREFIX = "NL2REPO_FROZENLIST_RESULT="
MAX_OUTPUT_BYTES = 1024 * 1024
SCENARIOS: dict[str, Any] = {
    "exports-version-metadata": {
        "all": ["FrozenList", "PyFrozenList"],
        "distribution_version": "1.8.1.dev0",
        "py_typed": True,
        "stub": True,
        "version": "1.8.1.dev0",
    },
    "generic-mutable-sequence": {
        "frozen_args": ["int"],
        "frozen_origin": "FrozenList",
        "frozen_subclass": True,
        "py_args": ["str"],
        "py_origin": "FrozenList",
        "py_subclass": True,
    },
    "constructor-copy-iteration": {
        "empty": [[], False],
        "generated": [4, 5],
        "iterated": [1, 2],
        "source": [1, 2, 3],
        "stored": [1, 2],
    },
    "index-slice-reversed": {
        "after": [7, 9],
        "index": 7,
        "reversed": [9, 8, 7],
        "slice": [7, 8, 9],
        "slice_type": "list",
    },
    "comparisons": {"eq": True, "ge": True, "gt": True, "le": True, "lt": True, "ne": True},
    "insert-append-extend-iadd": {"append_result": None, "items": [1, 2, 3, 4, 5, 6], "same_after_iadd": True},
    "remove-clear-reverse-pop": {"cleared": [], "first": 1, "last": 2, "reversed": [5, 4, 3]},
    "count-index-contains": {"contains": True, "count": 2, "index": 0, "missing": False},
    "freeze-idempotent-repr": {"after": "<FrozenList(frozen=True, [1])>", "before": "<FrozenList(frozen=False, [1])>", "first": None, "frozen": True, "second": None},
    "frozen-setitem": {"error": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"}, "items": [1, 2]},
    "frozen-delitem": {"error": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"}, "items": [1, 2]},
    "frozen-insert": {"error": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"}, "items": [1]},
    "frozen-append-extend-iadd": {
        "append": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
        "extend": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
        "iadd": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
        "items": [1],
    },
    "frozen-remove-clear-reverse-pop": {
        "clear": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
        "items": [1, 2],
        "pop": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
        "remove": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
        "reverse": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
    },
    "hash-contract": {
        "after_matches_tuple": True,
        "before": {"message": "Cannot hash unfrozen list.", "type": "builtins.RuntimeError"},
        "dict_lookup": "ok",
    },
    "shallow-copy": {"different": True, "frozen_copy": [[4], True], "lengths": [3, 2], "shared_item": True},
    "deepcopy-nested": {"different_inner": True, "frozen": True, "nested_copy": [1, 3], "nested_original": [1]},
    "deepcopy-circular": {"different": True, "items": 1, "self_cycle": True},
    "deepcopy-shared-reference": {"copy_items": [1, 2], "new_shared": True, "original_items": [1], "same_reference": True},
    "pyfrozenlist-parity": {
        "append_error": {"message": "Cannot modify frozen list.", "type": "builtins.RuntimeError"},
        "before": "<FrozenList(frozen=False, [1, 2, 3])>",
        "frozen": True,
        "hash_matches": True,
        "items": [1, 2, 3],
    },
    "pure-python-selection": {"disabled": "1", "module": "frozenlist", "same": True},
}


def _stage_adapter() -> Path:
    source = Path(__file__).resolve().parent / "adapter.py"
    target = Path("/tmp/frozenlist-adapter.py")
    data = source.read_bytes()
    target.write_bytes(data)
    os.chown(target, 10001, 10001)
    os.chmod(target, 0o500)
    return target


def invoke(adapter: Path, scenario: str) -> dict[str, Any]:
    environment = [
        "HOME=/tmp/candidate-build/home",
        "TMPDIR=/tmp/candidate-build/tmp",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
    ]
    if scenario == "pure-python-selection":
        environment.append("FROZENLIST_NO_EXTENSIONS=1")
    command = [
        RUNUSER,
        "-u",
        "candidate",
        "--",
        "env",
        *environment,
        sys.executable,
        "-I",
        "-B",
        str(adapter),
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        scenario,
    ]
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            completed = subprocess.run(
                command,
                stdout=stdout,
                stderr=stderr,
                timeout=20,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
        stdout.seek(0)
        stderr.seek(0)
        output = stdout.read(MAX_OUTPUT_BYTES + 1)
        error = stderr.read(MAX_OUTPUT_BYTES + 1)
    if completed.returncode != 0 or len(output) > MAX_OUTPUT_BYTES or len(error) > MAX_OUTPUT_BYTES:
        return {
            "ok": False,
            "exception_type": "CandidateProcessError",
            "exception_message": error[-1000:].decode("utf-8", "replace"),
        }
    lines = [line for line in output.decode("utf-8", "replace").splitlines() if line.startswith(RESULT_PREFIX)]
    if len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": "expected one result line"}
    try:
        result = json.loads(lines[0][len(RESULT_PREFIX) :])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return result if isinstance(result, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    adapter = _stage_adapter()
    leaves = []
    try:
        for scenario, expected in SCENARIOS.items():
            result = invoke(adapter, scenario)
            actual = result.get("value") if result.get("ok") is True else {
                "exception_message": result.get("exception_message"),
                "exception_type": result.get("exception_type"),
            }
            passed = actual == expected
            message = ""
            if not passed:
                message = json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:2000]
            leaves.append({
                "id": f"frozenlist/{scenario}",
                "message": message,
                "status": "passed" if passed else "failed",
            })
    finally:
        adapter.unlink(missing_ok=True)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
