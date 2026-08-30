from __future__ import annotations

import json
import runpy
from pathlib import Path

from nl2repobench.verification.candidate_client import execute_script


def main() -> int:
    verifier_root = Path(__file__).resolve().parent
    scenario_module = runpy.run_path(str(verifier_root / "scenarios.py"))
    common = scenario_module["COMMON"]
    scenarios = scenario_module["SCENARIOS"]
    expected = json.loads((verifier_root / "expected.json").read_text())
    leaves = []
    for scenario, source in scenarios.items():
        response = execute_script(common + source, timeout_sec=10.0)
        actual = (
            response.value
            if response.ok
            else {
                "exception_message": response.exception_message,
                "exception_type": response.exception_type,
            }
        )
        wanted = expected[scenario]
        passed = actual == wanted
        leaves.append(
            {
                "id": f"yarl/{scenario}",
                "message": ""
                if passed
                else json.dumps(
                    {"actual": actual, "expected": wanted},
                    ensure_ascii=False,
                    sort_keys=True,
                )[:4000],
                "status": "passed" if passed else "failed",
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
