#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REVISION="88e3d965c0b1628642a30a841745b410d6835052"
SOURCE_TARBALL_SHA256="4223c7a31191c6117f6ad21b40a5e391c1d130da85e2cfe482ef2c38bccf0dea"
SOURCE_ARCHIVE="/tmp/css-tree-${UPSTREAM_REVISION}.tar.gz"
SOURCE_ROOT="/tmp/css-tree-source"
rm -f "$SOURCE_ARCHIVE"
rm -rf "$SOURCE_ROOT"
mkdir -p "$SOURCE_ROOT"
node /solution/fetch-source.mjs "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_TARBALL_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1 -C "$SOURCE_ROOT"
(
  cd "$SOURCE_ROOT"
  sha256sum --check --strict /solution/source-files.sha256
)
rm -rf /workspace/*
mkdir -p /workspace/lib /workspace/data
cp -a "$SOURCE_ROOT/lib/." /workspace/lib/
cp -a "$SOURCE_ROOT/data/." /workspace/data/
cp "$SOURCE_ROOT/LICENSE" "$SOURCE_ROOT/README.md" /workspace/
cp /solution/package.json /workspace/package.json
cp /solution/package-lock.json /workspace/package-lock.json
chmod 0444 /workspace/package.json /workspace/package-lock.json
printf 'oracle source revision %s verified; codeload sha256 %s\n' "$UPSTREAM_REVISION" "$SOURCE_TARBALL_SHA256"
