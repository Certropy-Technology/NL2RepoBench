"""Root-owned proxy that executes a Ruby bridge under the candidate UID."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).parents[2]))
    from nl2repobench.verification.ruby_supervisor import run_ruby_bridge
else:
    from .ruby_supervisor import run_ruby_bridge


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-sec", type=float, default=30.0)
    parser.add_argument("bridge", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("bundle", type=Path)
    try:
        args = parser.parse_args()
    except SystemExit:
        return 64
    bridge = args.bridge
    candidate = args.candidate
    bundle = args.bundle
    if (
        bridge.is_symlink()
        or not bridge.is_file()
        or candidate.is_symlink()
        or not candidate.is_dir()
        or bundle.is_symlink()
        or not bundle.is_dir()
    ):
        return 64
    result = run_ruby_bridge(
        ("/usr/local/bin/ruby", str(bridge), str(candidate), str(bundle)),
        sys.stdin.buffer.read(),
        timeout_sec=args.timeout_sec,
    )
    sys.stdout.buffer.write(result.stdout)
    sys.stderr.buffer.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
