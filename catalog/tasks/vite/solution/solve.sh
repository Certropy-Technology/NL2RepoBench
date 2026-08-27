#!/usr/bin/env bash
set -euo pipefail

SOLUTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ARCHIVE="$SOLUTION_DIR/source/vite-source.tar"
SOURCE_ARCHIVE_SHA256="a55bd75197b7f7039028dfdbb5e07fc6bfb3fbc4e9b6a54890176a58ba9716f6"
UPSTREAM_REVISION="4f9d2f4dadc83191200de7d2154c957a711e8c3d"
SOURCE_DIR="/tmp/vite-frozen-source"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
rm -rf "$SOURCE_DIR"
mkdir -p "$SOURCE_DIR"
tar -xf "$SOURCE_ARCHIVE" -C "$SOURCE_DIR"

# The private reference package is a prebuilt, parity-checked projection of the
# scoped public utility contract. The complete frozen source archive above is
# retained and verified as the immutable authoring reference.
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/dist/node
cp "$SOLUTION_DIR/reference/package.json" /workspace/package.json
cp "$SOLUTION_DIR/reference/package-lock.json" /workspace/package-lock.json
cp "$SOLUTION_DIR/reference/index.js" /workspace/dist/node/index.js
printf '%s\n' "$UPSTREAM_REVISION" > /workspace/.nl2repo-source-revision
