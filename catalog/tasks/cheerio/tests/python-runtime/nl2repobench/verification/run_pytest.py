"""Root-owned pytest launcher that imports trusted plugins before candidate code."""

from __future__ import annotations

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", required=True)
    parser.add_argument("--junit", required=True)
    parser.add_argument("tests")
    args = parser.parse_args()

    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    os.environ["NL2REPO_COLLECTION_REPORT"] = args.collection
    import pytest

    from . import pytest_plugin

    exit_code = pytest.main(
        [
            "-p",
            "no:cacheprovider",
            "--continue-on-collection-errors",
            f"--junitxml={args.junit}",
            args.tests,
        ],
        plugins=[pytest_plugin],
    )
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(int(exit_code))


if __name__ == "__main__":
    main()
