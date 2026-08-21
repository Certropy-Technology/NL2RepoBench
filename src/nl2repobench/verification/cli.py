"""Standalone command entry copied into Harbor verifier images."""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

from .grader import grade_verification, write_grading_outputs
from .models import VerificationReason

MAX_COLLECTION_BYTES = 4 * 1024 * 1024
MAX_JUNIT_BYTES = 64 * 1024 * 1024


def _optional_bytes(path: Path | None, *, max_bytes: int) -> bytes | None:
    if path is None:
        return None
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK,
        )
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > max_bytes:
                return None
            data = os.read(descriptor, max_bytes + 1)
            return data if len(data) <= max_bytes else None
        finally:
            os.close(descriptor)
    except OSError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--metric-contract", default="fixed-test-pass-rate-v1")
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--collection", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--report", type=Path, help="Verifier-owned node:test JSON report.")
    parser.add_argument("--runner-exit-code", type=int)
    # Do not import v2 Node modules while the v1 verifier runtime is running.
    # Each mode validates its own reason after the mode is selected.
    parser.add_argument("--reason")
    parser.add_argument("--output", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()

    node_mode = args.report is not None or args.runner_exit_code is not None
    if node_mode:
        from .node_grader import (
            MAX_NODE_REPORT_BYTES,
            grade_node_test_report,
            write_node_grading_outputs,
        )
        from .node_models import NodeVerificationReason

        node_reason = None
        if args.reason is not None:
            try:
                node_reason = NodeVerificationReason(args.reason)
            except ValueError as exc:
                raise SystemExit(f"Node report mode received a v1 reason: {args.reason}") from exc
        node_result = grade_node_test_report(
            expected_total=args.expected,
            metric_contract=args.metric_contract,
            report_data=_optional_bytes(args.report, max_bytes=MAX_NODE_REPORT_BYTES),
            runner_exit_code=args.runner_exit_code,
            explicit_reason=node_reason,
        )
        write_node_grading_outputs(node_result, args.output)
        return

    result = grade_verification(
        expected_total=args.expected,
        metric_contract=args.metric_contract,
        junit_data=_optional_bytes(args.junit, max_bytes=MAX_JUNIT_BYTES),
        collection_data=_optional_bytes(args.collection, max_bytes=MAX_COLLECTION_BYTES),
        pytest_exit_code=args.pytest_exit_code,
        explicit_reason=VerificationReason(args.reason) if args.reason else None,
    )
    write_grading_outputs(result, args.output)


if __name__ == "__main__":
    main()
