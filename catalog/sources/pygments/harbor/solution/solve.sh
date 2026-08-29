#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly SOURCE_ARCHIVE_SHA256="3020b621c9c647c499fe804a4606c9818a3d318af42ee867d653ae7d145bb53c"
readonly ROOT="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/doc" "$ROOT/external" "$ROOT/scripts"
echo "restored Pygments frozen source archive"
