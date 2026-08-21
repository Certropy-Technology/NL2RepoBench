from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


MAX_JUNIT_BYTES = 8 * 1024 * 1024


def write_results(
    *,
    counts: dict[str, int],
    expected_effective: int,
    expected_collected: int,
    collection_exit_code: int | None,
    pytest_exit_code: int | None,
    reason: str | None,
    failure_class: str | None,
    valid: bool,
) -> None:
    effective_total = counts["collected"] - counts["skipped"]
    reward = (
        counts["passed"] / expected_effective
        if valid and expected_effective > 0
        else 0.0
    )
    reward = max(0.0, min(reward, 1.0))
    if valid and reward < 1.0 and failure_class is None:
        failure_class = "model"

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
                "collection_exit_code": collection_exit_code,
                "effective_total": effective_total,
                "expected": expected_effective,
                "expected_collected": expected_collected,
                "failure_class": failure_class,
                "metric_contract": "fixed-test-pass-rate-v1",
                "pytest_exit_code": pytest_exit_code,
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
    parser.add_argument("--expected-effective", type=int, required=True)
    parser.add_argument("--expected-collected", type=int, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--collection-exit-code", type=int)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    parser.add_argument("--failure-class", choices=("model", "verifier"))
    args = parser.parse_args()

    counts = {
        "collected": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "passed": 0,
    }
    reason = args.reason
    failure_class = args.failure_class
    valid = reason is None or failure_class == "model"

    if reason is None:
        if args.junit is None or not args.junit.is_file() or args.junit.is_symlink():
            reason = "junit-missing"
            failure_class = "verifier"
            valid = False
        elif args.junit.stat().st_size > MAX_JUNIT_BYTES:
            reason = "junit-oversized"
            failure_class = "verifier"
            valid = False
        else:
            try:
                cases = list(ET.parse(args.junit).getroot().iter("testcase"))
            except (OSError, ET.ParseError):
                reason = "junit-invalid"
                failure_class = "verifier"
                valid = False
            else:
                counts["collected"] = len(cases)
                counts["failed"] = sum(
                    case.find("failure") is not None for case in cases
                )
                counts["errors"] = sum(
                    case.find("error") is not None for case in cases
                )
                counts["skipped"] = sum(
                    case.find("skipped") is not None for case in cases
                )
                counts["passed"] = (
                    counts["collected"]
                    - counts["failed"]
                    - counts["errors"]
                    - counts["skipped"]
                )

    effective_total = counts["collected"] - counts["skipped"]
    if reason is None and args.collection_exit_code != 0:
        reason = "collection-error"
        failure_class = "verifier"
        valid = False
    if reason is None and (
        counts["collected"] != args.expected_collected
        or effective_total != args.expected_effective
    ):
        reason = "collection-mismatch"
        failure_class = "verifier"
        valid = False
    if reason is None and args.pytest_exit_code not in {0, 1}:
        reason = "pytest-abnormal-exit"
        failure_class = "verifier"
        valid = False
    if (
        reason is None
        and args.pytest_exit_code == 0
        and counts["failed"] + counts["errors"] != 0
    ):
        reason = "pytest-status-mismatch"
        failure_class = "verifier"
        valid = False

    write_results(
        counts=counts,
        expected_effective=args.expected_effective,
        expected_collected=args.expected_collected,
        collection_exit_code=args.collection_exit_code,
        pytest_exit_code=args.pytest_exit_code,
        reason=reason,
        failure_class=failure_class,
        valid=valid,
    )


if __name__ == "__main__":
    main()
