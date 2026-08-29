#!/usr/bin/env python3
"""Execute pytest with candidate and dependency sites explicitly isolated."""

from __future__ import annotations

import sys
from pathlib import Path


class ResultPlugin:
    def pytest_runtest_logreport(self, report):
        del report


def main() -> int:
    tests = Path(sys.argv[1]).resolve()
    junit = Path(sys.argv[2]).resolve()
    sys.path.insert(0, "/tmp/candidate-site")
    sys.path.insert(1, "/opt/candidate-dependencies/site")
    import pytest

    return int(
        pytest.main(
            [
                "-c",
                "/dev/null",
                "-p",
                "no:cacheprovider",
                "--continue-on-collection-errors",
                f"--junitxml={junit}",
                str(tests),
            ],
            plugins=[ResultPlugin()],
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
