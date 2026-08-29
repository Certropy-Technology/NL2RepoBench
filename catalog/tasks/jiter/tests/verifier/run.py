from __future__ import annotations

import json
import sys
from pathlib import Path

from nl2repobench.verification.candidate_client import execute_script

# `python -I script.py` does not retain the script directory on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cases import CASES


def main() -> None:
    leaves = []
    for case_id, source in CASES:
        observed = execute_script(source, timeout_sec=8.0)
        passed = observed.ok and observed.value is True
        leaves.append({
            "id": f"jiter::{case_id}",
            "status": "passed" if passed else "failed",
            "message": "ok" if passed else (observed.exception_message or "scenario returned false"),
        })
    if len(leaves) != 32 or len({leaf["id"] for leaf in leaves}) != 32:
        raise RuntimeError("private scenario collection is not the frozen 32-leaf contract")
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
