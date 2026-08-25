"""Hardened JUnit parsing that never trusts aggregate XML attributes."""

from __future__ import annotations

from defusedxml import ElementTree

from .models import TestCounts


class JUnitError(ValueError):
    """Raised when a JUnit document cannot be graded safely."""


def parse_junit(data: bytes) -> TestCounts:
    """Count testcase elements and classify each terminal child exactly once."""

    if not data.strip():
        raise JUnitError("JUnit document is empty")
    try:
        root = ElementTree.fromstring(data)
    except Exception as exc:  # defusedxml exposes several parser-specific errors
        raise JUnitError(f"cannot parse JUnit XML: {exc}") from exc

    passed = failed = errors = skipped = 0
    cases = list(root.iter("testcase"))
    for case in cases:
        if case.find("error") is not None:
            errors += 1
        elif case.find("failure") is not None:
            failed += 1
        elif case.find("skipped") is not None:
            skipped += 1
        else:
            passed += 1
    return TestCounts(
        collected=len(cases),
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
    )
