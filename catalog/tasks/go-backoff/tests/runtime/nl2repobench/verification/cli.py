"""Standalone command entry copied into Harbor verifier images."""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

from .registry import VerifierRuntimeRegistry
from .taxonomy import canonical_reason

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
    parser.add_argument(
        "--runtime",
        choices=("python", "node", "go"),
        required=True,
        help="Explicit verifier runtime identity.",
    )
    parser.add_argument("--metric-contract", default="fixed-test-pass-rate-v1")
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--collection", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--report", type=Path, help="Verifier-owned node:test JSON report.")
    parser.add_argument("--runner-exit-code", type=int)
    parser.add_argument("--reason")
    parser.add_argument("--output", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()

    runtime = args.runtime
    if runtime == "python" and (args.report is not None or args.runner_exit_code is not None):
        parser.error("--runtime python cannot receive Node report arguments")
    if runtime in {"node", "go"} and (args.junit is not None or args.collection is not None):
        parser.error("Node/Go runtimes cannot receive pytest report arguments")
    adapter = VerifierRuntimeRegistry.default().resolve(runtime)
    reason = canonical_reason(args.reason) if args.reason else None
    result = adapter.grade(
        expected_total=args.expected,
        metric_contract=args.metric_contract,
        junit_data=_optional_bytes(
            args.junit, max_bytes=adapter.limits.get("junit", MAX_JUNIT_BYTES)
        ),
        collection_data=_optional_bytes(
            args.collection, max_bytes=adapter.limits.get("collection", MAX_COLLECTION_BYTES)
        ),
        report_data=_optional_bytes(
            args.report, max_bytes=adapter.limits.get("report", MAX_JUNIT_BYTES)
        ),
        pytest_exit_code=args.pytest_exit_code,
        runner_exit_code=args.runner_exit_code,
        explicit_reason=reason,
    )
    adapter.write(result, args.output)


if __name__ == "__main__":
    main()
