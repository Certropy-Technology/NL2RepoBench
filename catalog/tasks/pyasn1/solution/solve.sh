#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_REVISION="8003397013f6c0e0eabbd2605770477acbc2dc44"
readonly SOURCE_ARCHIVE_SHA256="c832e9d224c0a29d2f195f4472045279a9f5a0b02d793da257ab82e4e952586f"
readonly ROOT="/workspace"
readonly SOURCE_ARCHIVE="/solution/source.tar"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
find "$ROOT" -type l -delete
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests"
echo "restored pyasn1 at $UPSTREAM_REVISION"
