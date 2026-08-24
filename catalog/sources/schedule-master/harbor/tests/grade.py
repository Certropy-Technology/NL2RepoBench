from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def write_result(
    *,
    expected: int,
    junit: Path | None,
    exit_code: int | None,
    reason: str | None,
) -> None:
    counts = {"collected": 0, "failed": 0, "errors": 0, "skipped": 0, "passed": 0}
    valid = reason is None

    if junit is not None and junit.is_file():
        try:
            cases = list(ET.parse(junit).getroot().iter("testcase"))
        except (ET.ParseError, OSError):
            reason = reason or "junit-malformed"
            valid = False
        else:
            counts["collected"] = len(cases)
            counts["failed"] = sum(case.find("failure") is not None for case in cases)
            counts["errors"] = sum(case.find("error") is not None for case in cases)
            counts["skipped"] = sum(case.find("skipped") is not None for case in cases)
            counts["passed"] = (
                counts["collected"] - counts["failed"] - counts["errors"] - counts["skipped"]
            )
    elif reason is None:
        reason = "junit-missing"
        valid = False

    effective_total = counts["collected"] - counts["skipped"]
    if reason is None and effective_total != expected:
        reason = "collection-mismatch"
        valid = False
    if reason is None and exit_code not in {0, 1}:
        reason = "pytest-abnormal-exit"
        valid = False

    reward = counts["passed"] / expected if valid and expected > 0 else 0.0
    reward = max(0.0, min(reward, 1.0))
    verifier_dir = Path("/logs/verifier")
    verifier_dir.mkdir(parents=True, exist_ok=True)
    (verifier_dir / "reward.json").write_text(
        json.dumps({"reward": reward, "test_pass_rate": reward}, indent=2) + "\n",
        encoding="utf-8",
    )
    (verifier_dir / "grading.json").write_text(
        json.dumps(
            {
                **counts,
                "effective_total": effective_total,
                "expected": expected,
                "pytest_exit_code": exit_code,
                "reason": reason,
                "reward": reward,
                "valid": valid,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    args = parser.parse_args()
    write_result(
        expected=args.expected,
        junit=args.junit,
        exit_code=args.pytest_exit_code,
        reason=args.reason,
    )


if __name__ == "__main__":
    main()
