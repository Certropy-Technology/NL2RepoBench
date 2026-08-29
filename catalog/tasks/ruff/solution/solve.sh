#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "$0")" && pwd)"
readonly SOURCE_SHA256="16d616d1fd63e53f7f1d7df1453388df09d23148b987f87346561756a81ca3d2"
readonly BINARY_SHA256="2dcebc4afe93291b389026dce3359650508f99b9ed0c2b7fbc71ac0962a2fcc1"

printf '%s  %s\n' "$SOURCE_SHA256" "$ROOT/source.tar" | sha256sum --check --strict
printf '%s  %s\n' "$BINARY_SHA256" "$ROOT/ruff/_ruff_bin" | sha256sum --check --strict

reference_root=/tmp/ruff-reference-source
rm -rf "$reference_root"
mkdir -p "$reference_root"
tar -xf "$ROOT/source.tar" -C "$reference_root"
grep -Fq 'version = "0.16.4"' "$reference_root/pyproject.toml"
grep -Fq 'name = "ruff"' "$reference_root/pyproject.toml"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$ROOT/ruff" /workspace/ruff
cp "$ROOT/setup.py" /workspace/setup.py
chmod 0555 /workspace/ruff/_ruff_bin
