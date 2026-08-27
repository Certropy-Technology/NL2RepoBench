#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="8f8b212de8c2129d7954c6cd373762880375620a"
readonly ARCHIVE_SHA="be1c2c2e74293ab92b50f6044c345e20ccf2e1b28c1e5bdc73dd17d605cd253d"
readonly ROOT="/workspace"
readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
readonly ARCHIVE="$BUNDLE_ROOT/source.tar"

printf '%s  %s\n' "$ARCHIVE_SHA" "$ARCHIVE" | sha256sum --check --strict
rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?*
mkdir -p "$ROOT/.oracle/source"
tar -xf "$ARCHIVE" -C "$ROOT/.oracle/source"
test -f "$ROOT/.oracle/source/src/requests/__version__.py"
grep -Fq "$REVISION" "$BUNDLE_ROOT/provenance.txt"
cp -a "$ROOT/.oracle/source/src" "$ROOT/src"
cp "$ROOT/.oracle/source/pyproject.toml" "$ROOT/pyproject.toml"
cp "$ROOT/.oracle/source/setup.py" "$ROOT/setup.py"
cp "$ROOT/.oracle/source/README.md" "$ROOT/README.md"
cp "$ROOT/.oracle/source/LICENSE" "$ROOT/LICENSE"
cp "$ROOT/.oracle/source/NOTICE" "$ROOT/NOTICE"
rm -rf "$ROOT/.oracle"
