from __future__ import annotations

import json
import importlib.util
from pathlib import Path

from nl2repobench.verification.candidate_client import execute_script

_SCENARIOS_PATH = Path(__file__).with_name("scenarios.py")
_SPEC = importlib.util.spec_from_file_location("oauthlib_private_scenarios", _SCENARIOS_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("private scenario bundle is unavailable")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
SCENARIOS = _MODULE.SCENARIOS


def main() -> int:
    leaves = []
    for name, source, expected in SCENARIOS:
        observed = execute_script(source, timeout_sec=10.0)
        actual = observed.value if observed.ok else observed.exception_type
        passed = actual == expected
        leaves.append(
            {
                "id": f"oauthlib/{name}",
                "status": "passed" if passed else "failed",
                "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True, default=repr)[:1200],
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
