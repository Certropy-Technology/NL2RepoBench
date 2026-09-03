#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"
python3 - "$bridge" "$proxy" <<'PY'
import json
import subprocess
import sys

bridge, proxy = sys.argv[1:]
cases = {
    "basic": {"Name": "Ari", "Age": 7, "Active": True, "Tags": None, "Meta": None},
    "slice": [
        {"Name": "Ari", "Age": 7, "Active": False, "Tags": None, "Meta": None},
        {"Name": "Bo", "Age": 9, "Active": False, "Tags": None, "Meta": None},
    ],
    "map": {"one": 1, "two": 2},
    "ignore_empty": {"Name": "keep", "Age": 9, "Active": True, "Tags": None, "Meta": None},
    "case_matching": {"insensitive": "case", "sensitive": ""},
    "tags": {"Name": "named", "Ignored": "preserved"},
    "field_mapping": {"Name": "mapped"},
    "converter": 42,
    "deep_copy": {"Name": "origin", "Age": 0, "Active": False, "Tags": ["one"], "Meta": {"count": 1}},
    "invalid": "error",
}

for operation, expected in cases.items():
    request = json.dumps({"operation": operation, "args": []}) + "\n"
    result = subprocess.run(
        [proxy, bridge], input=request, text=True, capture_output=True, timeout=20, check=False
    )
    if result.returncode:
        raise SystemExit(f"{operation}: bridge returned {result.returncode}: {result.stderr[:500]}")
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{operation}: invalid bridge response: {exc}: {result.stdout[:500]}")
    if response.get("value") != expected:
        raise SystemExit(f"{operation}: expected {expected!r}, got {response!r}")
PY
