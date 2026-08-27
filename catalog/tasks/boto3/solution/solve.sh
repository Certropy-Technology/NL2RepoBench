#!/usr/bin/env bash
set -euo pipefail

readonly ARCHIVE_SHA="2b56d8a2d4193499e3c3ed6685622e5c75af11c0cfa1e6173d59f10090be3208"
readonly ROOT="/workspace"
readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
readonly ARCHIVE="$BUNDLE_ROOT/source.tar"

printf '%s  %s\n' "$ARCHIVE_SHA" "$ARCHIVE" | sha256sum --check --strict
rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?*
mkdir -p "$ROOT/.oracle/source"
tar -xf "$ARCHIVE" -C "$ROOT/.oracle/source"
cp -a "$ROOT/.oracle/source/boto3" "$ROOT/boto3"
cp -a "$ROOT/.oracle/source/tests" "$ROOT/tests"
cp "$ROOT/.oracle/source/setup.py" "$ROOT/setup.py"
cp "$ROOT/.oracle/source/setup.cfg" "$ROOT/setup.cfg"
cp "$ROOT/.oracle/source/LICENSE" "$ROOT/LICENSE"
cp "$ROOT/.oracle/source/README.rst" "$ROOT/README.rst"
cat > "$ROOT/MANIFEST.in" <<'MANIFEST'
recursive-include boto3/data *.json
recursive-include boto3/examples *.rst
MANIFEST
rm -rf "$ROOT/.oracle"
