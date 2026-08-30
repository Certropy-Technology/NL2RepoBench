#!/usr/bin/env python3
"""Retired projection mutator.

Generated Harbor trees are compiler output. This historical entry point is
kept only to fail closed for operators with an old command; it never mutates
``catalog/tasks``. Use the compiler with a source under ``catalog/sources``.
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.parse_args()
    parser.error(
        "projection sync is retired; compile catalog/sources/<task-id> "
        "through the canonical compiler"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
