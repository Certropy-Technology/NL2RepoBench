from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    args = parser.parse_args()

    counts = {"collected": 0, "failed": 0, "errors": 0, "skipped": 0, "passed": 0}
    reason = args.reason

    if args.junit is not None and args.junit.is_file():
        root = ET.parse(args.junit).getroot()
        cases = list(root.iter("testcase"))
        counts["collected"] = len(cases)
        counts["failed"] = sum(case.find("failure") is not None for case in cases)
        counts["errors"] = sum(case.find("error") is not None for case in cases)
        counts["skipped"] = sum(case.find("skipped") is not None for case in cases)
        counts["passed"] = (
            counts["collected"]
            - counts["failed"]
            - counts["errors"]
            - counts["skipped"]
        )
    elif reason is None:
        reason = "junit-missing"

    passed = min(counts["passed"], args.expected)
    score = passed / args.expected if args.expected > 0 else 0.0

    verifier_dir = Path("/logs/verifier")
    verifier_dir.mkdir(parents=True, exist_ok=True)
    (verifier_dir / "reward.json").write_text(
        json.dumps({"reward": score, "test_pass_rate": score}, indent=2) + "\n",
        encoding="utf-8",
    )
    (verifier_dir / "grading.json").write_text(
        json.dumps(
            {
                **counts,
                "expected": args.expected,
                "pytest_exit_code": args.pytest_exit_code,
                "reason": reason,
                "reward": score,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
