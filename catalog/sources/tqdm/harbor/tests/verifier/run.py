from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


EXPECTED = {
    "format_helpers": {
        "sizeof": "1.02k",
        "interval": "1:01:01",
        "number": "12.3",
        "meter": "run|###       |3/10|00:02| 1.50item/s",
    },
    "disabled_iteration": {
        "values": [0, 1, 2],
        "n": 0,
        "total": 3,
        "output": "",
    },
    "update_reset": {
        "before": [2, 5],
        "after_reset": [0, 3],
        "after_update": [1, 3],
    },
    "lazy_iteration": {
        "constructed": [],
        "first": 0,
        "after_first": [0],
        "rest": [1],
    },
    "utilities": {
        "disp_len": 4,
        "disp_trim": "abcd",
        "enumerate": [[2, "a"], [3, "b"]],
        "zip": [[1, 3], [2, 4]],
        "map": [2, 4, 6],
    },
    "public_api": {"range": [0, 1, 2], "same_class": True, "module": "tqdm.std"},
    "format_width": {"meter": "x:  50%|5| 2/4 [00:0"},
    "context_manager": {"values": [0, 1], "disabled": True, "n": 0},
}


def candidate_command(adapter: Path) -> list[str]:
    python = "/usr/local/bin/python" if Path("/usr/local/bin/python").is_file() else sys.executable
    return [python, "-I", str(adapter)]


def main() -> None:
    adapter = Path("/tmp/tqdm-contract-adapter.py")
    adapter.unlink(missing_ok=True)
    adapter.write_bytes(Path(__file__).with_name("adapter.py").read_bytes())
    adapter.chmod(0o444)
    payload = "".join(
        json.dumps({"id": name, "operation": name}, sort_keys=True) + "\n"
        for name in EXPECTED
    )
    try:
        completed = subprocess.run(
            candidate_command(adapter),
            input=payload,
            text=True,
            capture_output=True,
            timeout=45,
            check=False,
            env=os.environ.copy(),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        responses = {}
        diagnostic = type(exc).__name__
    else:
        responses = {}
        for line in completed.stdout.splitlines():
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(response, dict) and response.get("id") not in responses:
                responses[response.get("id")] = response
        diagnostic = f"candidate-exit={completed.returncode}; stderr={completed.stderr[-1000:]}"

    leaves = []
    for name, expected in EXPECTED.items():
        response = responses.get(name)
        passed = (
            isinstance(response, dict)
            and response.get("ok") is True
            and (expected is None or response.get("result") == expected)
        )
        leaves.append({"id": f"tqdm-contract::{name}", "status": "passed" if passed else "failed", "message": "" if passed else diagnostic})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
