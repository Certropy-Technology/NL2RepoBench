"""Convert Ruby contract JSONL output into a trusted leaf report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MAX_CONTRACT_OUTPUT_BYTES = 8 * 1024 * 1024
ALLOWED_STATUSES = {"passed", "failed", "error", "skipped", "todo", "xfail"}


def _read_lines(path: Path) -> list[str]:
    data = path.read_bytes()
    if len(data) > MAX_CONTRACT_OUTPUT_BYTES:
        raise ValueError("Ruby contract output exceeds the size limit")
    return data.decode("utf-8").splitlines()


def build_report(path: Path, *, expected: int, runner_exit_code: int) -> dict[str, Any]:
    """Build a report while retaining malformed output as a collection error."""

    if expected <= 0 or runner_exit_code not in {0, 1}:
        raise ValueError("expected must be positive and runner exit must be 0 or 1")
    tests: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(_read_lines(path), start=1):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"message": f"line {line_number}: invalid JSON: {exc.msg}"})
            continue
        if not isinstance(payload, dict):
            errors.append({"message": f"line {line_number}: report leaf must be an object"})
            continue
        test_id = payload.get("test_id")
        status = payload.get("status")
        if not isinstance(test_id, str) or not test_id:
            errors.append({"message": f"line {line_number}: test_id is required"})
            continue
        if test_id in seen:
            errors.append({"message": f"line {line_number}: duplicate test_id {test_id}"})
            continue
        if status not in ALLOWED_STATUSES:
            errors.append({"message": f"line {line_number}: invalid status for {test_id}"})
            continue
        seen.add(test_id)
        test = {"test_id": test_id, "status": status}
        for key in ("duration_ms", "details"):
            if key in payload:
                test[key] = payload[key]
        tests.append(test)
    if len(tests) != expected:
        errors.append({"message": f"report contains {len(tests)} leaves, expected {expected}"})
    return {
        "framework": "ruby",
        "report_format": "ruby-contract-json-v1",
        "collected": len(tests),
        "tests": tests,
        "collection_errors": errors,
        "runner_exit_code": runner_exit_code,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--runner-exit-code", type=int, required=True)
    args = parser.parse_args()
    report = build_report(
        args.input,
        expected=args.expected,
        runner_exit_code=args.runner_exit_code,
    )
    args.output.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
