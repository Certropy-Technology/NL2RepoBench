#!/usr/bin/env python3
"""Summarize Harbor trials with Polars and fixed-task macro averaging."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nl2repobench.analysis.results import load_results, summarize_results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--parquet", type=Path)
    args = parser.parse_args()

    frame, errors = load_results(args.runs_dir)
    summary = {
        "rows": frame.height,
        "columns": frame.columns,
        "parse_errors": errors,
        **summarize_results(frame),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    if args.parquet is not None:
        args.parquet.parent.mkdir(parents=True, exist_ok=True)
        frame.write_parquet(args.parquet)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
