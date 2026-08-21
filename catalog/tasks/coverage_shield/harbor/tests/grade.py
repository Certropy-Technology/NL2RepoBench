from __future__ import annotations

import argparse
import json
import os
import stat
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_JUNIT_BYTES = 16 * 1024 * 1024


def read_regular_file(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("JUnit report is not a regular file")
        if metadata.st_size > MAX_JUNIT_BYTES:
            raise ValueError("JUnit report exceeds size limit")
        data = bytearray()
        while len(data) <= MAX_JUNIT_BYTES:
            chunk = os.read(descriptor, min(1024 * 1024, MAX_JUNIT_BYTES + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        if len(data) > MAX_JUNIT_BYTES:
            raise ValueError("JUnit report exceeds size limit")
        return bytes(data)
    finally:
        os.close(descriptor)


def junit_counts(path: Path) -> dict[str, int]:
    root = ET.fromstring(read_regular_file(path))
    cases = list(root.iter("testcase"))
    failed = sum(case.find("failure") is not None for case in cases)
    errors = sum(case.find("error") is not None for case in cases)
    skipped = sum(case.find("skipped") is not None for case in cases)
    return {
        "collected": len(cases),
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "passed": len(cases) - failed - errors - skipped,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    parser.add_argument("--failure-class", choices=("model", "verifier"))
    parser.add_argument("--output-dir", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()

    counts = {"collected": 0, "failed": 0, "errors": 0, "skipped": 0, "passed": 0}
    reason = args.reason
    failure_class = args.failure_class
    valid = reason is None or failure_class == "model"

    if reason is None:
        if args.junit is None:
            reason = "junit-missing"
            failure_class = "verifier"
            valid = False
        else:
            try:
                counts = junit_counts(args.junit)
            except (OSError, ET.ParseError, ValueError):
                reason = "junit-missing-or-malformed"
                failure_class = "verifier"
                valid = False

    effective_total = counts["collected"] - counts["skipped"]
    if reason is None and effective_total != args.expected:
        reason = "collection-mismatch"
        failure_class = "verifier"
        valid = False
    if reason is None and args.pytest_exit_code not in {0, 1}:
        reason = "pytest-abnormal-exit"
        failure_class = "verifier"
        valid = False

    score = counts["passed"] / args.expected if valid and reason is None else 0.0
    score = max(0.0, min(score, 1.0))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "reward.json").write_text(
        json.dumps({"reward": score, "test_pass_rate": score}, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "grading.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                **counts,
                "effective_total": effective_total,
                "expected": args.expected,
                "failure_class": failure_class,
                "pytest_exit_code": args.pytest_exit_code,
                "reason": reason,
                "reward": score,
                "valid": valid,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
