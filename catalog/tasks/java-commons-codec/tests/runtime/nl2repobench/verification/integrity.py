"""Snapshot and verify root-owned verifier files around candidate execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def hash_paths(paths: list[Path]) -> dict[str, dict[str, int | str]]:
    records: dict[str, dict[str, int | str]] = {}
    for root in paths:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.is_symlink():
                raise ValueError(f"trusted tree contains symlink: {path}")
            data = path.read_bytes()
            records[str(path)] = {
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
                "mode": path.stat().st_mode & 0o777,
            }
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["snapshot", "verify"])
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    current = hash_paths(args.paths)
    if args.mode == "snapshot":
        args.record.write_text(
            json.dumps(current, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return
    expected = json.loads(args.record.read_text(encoding="utf-8"))
    if current != expected:
        expected_paths = set(expected)
        current_paths = set(current)
        details = {
            "added": sorted(current_paths - expected_paths),
            "changed": sorted(
                path
                for path in current_paths & expected_paths
                if current[path] != expected[path]
            ),
            "removed": sorted(expected_paths - current_paths),
        }
        raise SystemExit(
            "trusted verifier files changed during candidate execution: "
            + json.dumps(details, ensure_ascii=False, sort_keys=True)
        )


if __name__ == "__main__":
    main()
