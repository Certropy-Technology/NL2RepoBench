from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def write_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--expected-collected", type=int)
    parser.add_argument("--expected-skipped", type=int, default=0)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    args = parser.parse_args()

    counts = {
        "collected": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "passed": 0,
    }
    reason = args.reason
    valid = reason is None

    if args.junit is not None and args.junit.is_file() and reason is None:
        try:
            root = ET.parse(args.junit).getroot()
        except (ET.ParseError, OSError):
            root = None
            reason = "junit-malformed"
            valid = False

        if root is not None:
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
        valid = False

    effective_total = counts["collected"] - counts["skipped"]
    expected_collected = (
        args.expected if args.expected_collected is None else args.expected_collected
    )

    if reason is None and counts["collected"] != expected_collected:
        reason = "collection-mismatch"
        valid = False
    if reason is None and effective_total != args.expected:
        reason = "collection-mismatch"
        valid = False
    if reason is None and counts["skipped"] != args.expected_skipped:
        reason = "collection-mismatch"
        valid = False
    if reason is None and counts["errors"]:
        reason = "collection-error"
        valid = False
    if reason is None and args.pytest_exit_code not in {0, 1}:
        reason = "pytest-abnormal-exit"
        valid = False

    score = counts["passed"] / args.expected if valid and args.expected > 0 else 0.0
    score = max(0.0, min(score, 1.0))

    verifier_dir = Path("/logs/verifier")
    verifier_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        verifier_dir / "reward.json",
        {"reward": score, "test_pass_rate": score},
    )
    write_json(
        verifier_dir / "grading.json",
        {
            **counts,
            "effective_total": effective_total,
            "expected": args.expected,
            "expected_collected": expected_collected,
            "expected_skipped": args.expected_skipped,
            "pytest_exit_code": args.pytest_exit_code,
            "reason": reason,
            "failure_reason": reason,
            "reward": score,
            "valid": valid,
        },
    )


if __name__ == "__main__":
    main()
