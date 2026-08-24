#!/usr/bin/env python3
"""Validate Oracle, control, or blocked evidence from a production gate report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harbor_production_validation import validate_evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--kind", choices=("oracle", "controls", "blocked"), required=True)
    args = parser.parse_args()
    try:
        result = validate_evidence(args.report, args.kind)
    except (OSError, ValueError) as exc:
        print(f"Harbor production evidence gate failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
