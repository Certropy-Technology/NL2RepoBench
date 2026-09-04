from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

RESULT_PREFIX = "NL2REPO_CFFI_RESULT="
SCENARIOS = [
    "exports-version", "ffi-construction", "primitive-type", "pointer-new",
    "array-new", "struct-new", "cast-and-size", "string-read", "buffer-read",
    "getctype-normalization", "callback-success", "callback-error", "callback-onerror",
    "handle-roundtrip", "handle-identity", "addressof-array", "struct-field",
    "pointer-arithmetic", "cdef-types", "cdef-invalid", "list-types", "dlopen-abs",
    "dlopen-strlen", "emit-c-code", "set-source", "error-hierarchy", "null-and-bool",
    "deterministic-repeat",
]

EXPECTED = {
    "exports-version": {"all": ["FFI", "VerificationError", "VerificationMissing", "CDefError", "FFIError"], "version": "2.2.0.dev0", "ffi": "FFI"},
    "ffi-construction": {"type": "FFI", "null": False, "has_new": True},
    "primitive-type": {"kind": "primitive", "cname": "int", "size": 4, "align": 4, "pointer_item": "int"},
    "pointer-new": {"value": -7, "kind": "pointer", "cname": "int *"},
    "array-new": {"length": 3, "items": [1, 2, 3], "item": "int"},
    "struct-new": {"x": 2, "y": 3, "kind": "pointer", "cname": "struct point *"},
    "cast-and-size": {"unsigned": 4294967295, "int_size": 4, "char_size": 1, "double_size": 8},
    "string-read": {"full": "hello", "max3": "hel", "bytes": 13},
    "buffer-read": {"all": "abc123\u0000", "prefix": "abc"},
    "getctype-normalization": {"plain": "int", "pointer": "int *", "array": "int value[3]"},
    "callback-success": {"result": 42, "kind": "function"},
    "callback-error": {"result": -7},
    "callback-onerror": {"result": -9, "seen": ["ValueError", "ValueError"]},
    "handle-roundtrip": {"same": True, "kind": "pointer"},
    "handle-identity": {"distinct": True, "same_type": True},
    "addressof-array": {"items": [1, 8, 3], "kind": "pointer"},
    "struct-field": {"left": 4, "right": 9, "field": "int *"},
    "pointer-arithmetic": {"first": 10, "second": 20, "third": 30},
    "cdef-types": {"typedef": "primitive", "enum": "enum", "struct": "struct"},
    "cdef-invalid": {"type": "CDefError", "has_message": True},
    "list-types": {"typedefs": ["counter_t"], "structs": ["record"], "unions": []},
    "dlopen-abs": {"result": 12},
    "dlopen-strlen": {"result": 5},
    "emit-c-code": {"result": None, "exists": True, "has_include": True, "has_function": True},
    "set-source": {"result": None, "type": "FFI"},
    "error-hierarchy": {"cdef_is_ffi": False, "verification_is_ffi": False, "missing_is_verification": False},
    "null-and-bool": {"false": True, "equal": True, "cname": "void *"},
    "deterministic-repeat": {"same": True, "sample": {"value": 17, "kind": "pointer", "size": 8}},
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", default="/tmp/candidate-site")
    parser.add_argument("--dependency-site", default="/opt/candidate-dependencies/site")
    args = parser.parse_args()
    adapter = Path("/tmp/cffi-adapter.py")
    adapter.write_bytes((Path(__file__).with_name("adapter.py")).read_bytes())
    os.chown(adapter, 10001, 10001)
    os.chmod(adapter, 0o500)
    leaves: list[dict[str, str]] = []
    environment = {
        "HOME": "/tmp/candidate-build/home",
        "TMPDIR": "/tmp/candidate-build/tmp",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    try:
        for scenario in SCENARIOS:
            command = ["python", "-I", "-B", str(adapter), "--candidate-site", args.candidate_site, "--dependency-site", args.dependency_site, "--scenario", scenario]
            try:
                completed = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=20, check=False, preexec_fn=_drop_candidate_privileges)
                lines = [line for line in completed.stdout.splitlines() if line.startswith(RESULT_PREFIX)]
                payload = json.loads(lines[-1][len(RESULT_PREFIX):]) if completed.returncode == 0 and len(lines) == 1 else {"ok": False, "error": completed.stderr[-1000:]}
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
                payload = {"ok": False, "error": str(exc)}
            actual = payload.get("value") if payload.get("ok") is True else payload
            expected = EXPECTED[scenario]
            passed = actual == expected
            leaves.append({"id": f"cffi/{scenario}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:2000]})
    finally:
        adapter.unlink(missing_ok=True)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


def _drop_candidate_privileges() -> None:
    os.setgroups([])
    os.setgid(10001)
    os.setuid(10001)


if __name__ == "__main__":
    raise SystemExit(main())
