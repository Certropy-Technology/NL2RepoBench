#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/Kludex/python-multipart"
readonly UPSTREAM_REVISION="d9cb4c62db5b9defeeaa99bfe0e4da51e760108f"
readonly SOURCE_ARCHIVE_SHA256="8a6e1fa8c2372a6e637d4b202598ab79264c5a81636a35fb0c02d2ad1ae0be67"
readonly FETCH_ROOT="/tmp/python-multipart-oracle-source"
readonly SOURCE_ARCHIVE="$FETCH_ROOT/source.tar"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$SOURCE_ARCHIVE" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$SOURCE_ARCHIVE" -C /workspace
rm -rf /workspace/.github /workspace/tests /workspace/docs /workspace/fuzz /workspace/scripts
printf 'restored %s at %s\n' "$UPSTREAM_URL" "$UPSTREAM_REVISION"
