"""Run the hidden pyrsistent fixture as the unprivileged candidate user."""

from __future__ import annotations

import sys

CANDIDATE_SITE = "/tmp/candidate-site"
DEPENDENCY_SITE = "/opt/candidate-dependencies/site"


def main() -> int:
    for entry in (DEPENDENCY_SITE, CANDIDATE_SITE):
        if entry in sys.path:
            sys.path.remove(entry)
        sys.path.insert(0, entry)

    import pytest

    return int(pytest.main(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
