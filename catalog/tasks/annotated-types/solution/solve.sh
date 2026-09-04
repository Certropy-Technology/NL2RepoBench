#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/annotated-types/annotated-types"
readonly UPSTREAM_REVISION="ceb950e81a79403c911990ce960ecc6f46733508"
readonly SOURCE_ARCHIVE_SHA256="21dc75bcb85e3a2dac6cd1c4d7dfb871b0987d7d612d6b82d9eeb7812cc59a0c"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/tests"
printf 'restored %s at %s\n' "$UPSTREAM_URL" "$UPSTREAM_REVISION"
