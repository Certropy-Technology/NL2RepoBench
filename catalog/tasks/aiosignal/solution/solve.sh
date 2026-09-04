#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_REVISION="1c2bdc6dbd222463627638d2b46e9c3864e07597"
readonly SOURCE_ARCHIVE_SHA256="3cce05c57a65da0028ebd03992845c571d9d5368524529acd422a77e9f283bde"
readonly ROOT="/workspace"
readonly SOURCE_ARCHIVE="/solution/source.tar"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/docs" "$ROOT/requirements"
echo "restored aiosignal at $UPSTREAM_REVISION"
