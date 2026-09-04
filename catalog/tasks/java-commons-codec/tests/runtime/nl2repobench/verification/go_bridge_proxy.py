"""Root-owned proxy that executes a Go bridge under the candidate UID."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).parents[2]))
    from nl2repobench.verification.go_supervisor import run_go_bridge
else:
    from .go_supervisor import run_go_bridge


def main() -> int:
    if len(sys.argv) < 2:
        return 64
    result = run_go_bridge((sys.argv[-1],), sys.stdin.buffer.read())
    sys.stdout.buffer.write(result.stdout)
    sys.stderr.buffer.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
