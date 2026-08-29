from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SCENARIOS: dict[str, Any] = {
    "metadata/version": "0.5.2",
    "metadata/exports": {
        "api": ["cached_property", "under_cached_property"],
        "helpers": ["cached_property", "under_cached_property"],
        "same": True,
    },
    "metadata/dir": True,
    "metadata/invalid-attr": {
        "type": "builtins.AttributeError",
        "message": "module 'propcache' has no attribute 'invalid_attr'",
    },
    "api/identity": {"cached": True, "under": True},
    "cached/class-access": True,
    "cached/cache-hit": {"calls": 1, "same": True, "stored": True},
    "cached/docstring": "descriptor documentation.",
    "cached/wrapped-callable": 7,
    "cached/delete-recompute": {"calls": 2, "values": [1, 2]},
    "cached/set-name-guard": "builtins.TypeError",
    "cached/missing-set-name": "builtins.TypeError",
    "cached/no-dict": {"one-of": ["builtins.TypeError", "builtins.AttributeError"]},
    "cached/generic-alias": "GenericAlias",
    "under/class-access": True,
    "under/cache-hit": {"calls": 1, "same": True, "stored": True},
    "under/docstring": "under documentation.",
    "under/wrapped-callable": {"value": 9, "cache-key": "prop"},
    "under/readonly": {"type": "builtins.AttributeError", "message": "cached property is read-only"},
    "under/missing-cache": "builtins.AttributeError",
    "under/cache-preserves-none": True,
    "under/generic-alias": "GenericAlias",
    "fallback/cached": [1, 1, 1],
    "fallback/under": [1, 1, 1],
    "extension/import": {"ok": True, "cached": "cached_property", "under": "under_cached_property"},
    "extension/cached": [1, 1, 1],
    "extension/under": [1, 1, 1],
    "metadata/no-wildcard": [],
}


def stage_adapter() -> Path:
    source = Path(__file__).with_name("adapter.py")
    target = Path("/tmp/propcache-adapter.py")
    target.write_bytes(source.read_bytes())
    os.chown(target, 10001, 10001)
    os.chmod(target, 0o500)
    return target


def invoke(adapter: Path, scenario: str) -> dict[str, Any]:
    command = [
        shutil.which("runuser") or "/usr/sbin/runuser", "-u", "candidate", "--", "env",
        "HOME=/tmp", "TMPDIR=/tmp", "PATH=/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1",
        sys.executable, "-I", "-B", str(adapter),
        "--candidate-site", "/tmp/candidate-site", "--scenario", scenario,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
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


def matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict) and "one-of" in expected:
        return actual in expected["one-of"]
    return actual == expected


def main() -> int:
    adapter = stage_adapter()
    leaves = []
    for scenario, expected in SCENARIOS.items():
        result = invoke(adapter, scenario)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        passed = matches(actual, expected)
        leaves.append({
            "id": f"propcache/{scenario}",
            "status": "passed" if passed else "failed",
            "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1000],
        })
    try:
        adapter.unlink()
    except OSError:
        pass
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
