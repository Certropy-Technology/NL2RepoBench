#!/usr/bin/env python3
"""Root-owned grader for the google-auth task.

The grader is stdlib-only and never imports candidate code. It consumes the
nonce-stamped adapter report, enforces the fixed denominator, and writes
``reward.json``/``grading.json`` itself so a candidate cannot forge a score.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MARKER = "NL2REPO_REPORT="
VALID_STATUSES = {"passed", "failed", "skipped"}
LOG_DIR = Path("/logs/verifier")


def _extract(report: Path, nonce: str, expected: int) -> list[dict[str, Any]]:
    """Return the adapter leaves, or raise ValueError with a precise reason."""
    text = report.read_text(encoding="utf-8", errors="replace")
    lines = [line for line in text.splitlines() if line.startswith(MARKER)]
    if len(lines) != 1:
        raise ValueError(f"expected exactly one report marker, found {len(lines)}")

    payload = json.loads(lines[0][len(MARKER) :])
    if not isinstance(payload, dict):
        raise ValueError("report payload is not an object")
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported adapter schema_version")
    # A forged or replayed report cannot know this run's nonce.
    if not nonce or payload.get("nonce") != nonce:
        raise ValueError("report nonce mismatch")

    leaves = payload.get("leaves")
    if not isinstance(leaves, list):
        raise ValueError("adapter leaves is not a list")
    if len(leaves) != expected:
        raise ValueError(f"adapter collection mismatch: {len(leaves)} != {expected}")
    for leaf in leaves:
        if not isinstance(leaf, dict):
            raise ValueError("leaf is not an object")
        if not isinstance(leaf.get("id"), str):
            raise ValueError("leaf id is not a string")
        if leaf.get("status") not in VALID_STATUSES:
            raise ValueError(f"invalid leaf status: {leaf.get('status')!r}")
    if len({leaf["id"] for leaf in leaves}) != len(leaves):
        raise ValueError("duplicate leaf id")
    return leaves


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--nonce", default="")
    parser.add_argument("--adapter-exit-code", type=int)
    parser.add_argument("--reason")
    parser.add_argument("--failure-class")
    args = parser.parse_args()

    counts = {"collected": 0, "passed": 0, "failed": 0, "skipped": 0}
    leaf_status: dict[str, str] = {}
    reason = args.reason
    failure_class = args.failure_class
    valid = reason is None

    if valid:
        if args.report is None:
            valid, reason, failure_class = False, "grader-invoked-without-report", "verifier"
        else:
            try:
                leaves = _extract(args.report, args.nonce, args.expected)
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                valid = False
                reason = f"adapter-report-invalid:{exc}"
                # A missing/short report after a real candidate run reflects the
                # candidate's own code, not broken verifier plumbing.
                failure_class = "model"
            else:
                leaf_status = {leaf["id"]: leaf["status"] for leaf in leaves}
                counts["collected"] = len(leaves)
                for status in VALID_STATUSES:
                    counts[status] = sum(1 for leaf in leaves if leaf["status"] == status)

    effective_total = counts["collected"] - counts["skipped"]
    if valid and effective_total != args.expected:
        valid, reason, failure_class = False, "collection-mismatch", "verifier"

    reward = counts["passed"] / args.expected if valid and args.expected else 0.0

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "reward.json").write_text(
        json.dumps({"reward": reward, "test_pass_rate": reward}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (LOG_DIR / "grading.json").write_text(
        json.dumps(
            {
                **counts,
                "adapter_exit_code": args.adapter_exit_code,
                "effective_total": effective_total,
                "expected": args.expected,
                "failed_leaves": sorted(k for k, v in leaf_status.items() if v == "failed"),
                "failure_class": failure_class,
                "reason": reason,
                "reward": reward,
                "valid": valid,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
