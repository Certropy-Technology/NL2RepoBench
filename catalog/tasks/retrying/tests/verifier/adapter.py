"""Unprivileged pytest adapter for the frozen retrying hidden slice.

Launched by run.py as the ``candidate`` user under ``python -I``. Because ``-I``
ignores ``PYTHONPATH`` and drops the script directory, both the candidate site
and the frozen runtime dependency site are inserted explicitly here.

This file is trusted verifier code. It only manipulates ``sys.path`` and hands
control to pytest; it never imports candidate modules itself.
"""

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
