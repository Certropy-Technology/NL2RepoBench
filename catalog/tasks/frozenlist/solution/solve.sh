#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_REVISION="381c91e4663b067d5debab4cc19b400d3c459b44"
readonly SOURCE_ARCHIVE_SHA256="0fa249ef870bbbd9267b5427dbcbe7d5a3dc92d439ab677c1f9f6f84717f9b5b"
readonly ROOT="/workspace"
readonly SOURCE_ARCHIVE="/solution/source.tar"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
find "$ROOT" -type l -delete
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests" "$ROOT/requirements"
echo "restored frozenlist at $UPSTREAM_REVISION"
