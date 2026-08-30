#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/python-websockets/websockets"
readonly UPSTREAM_REVISION="e87ea9be0373edd5065b5e94dfa714cfde23023b"
readonly SOURCE_ARCHIVE_SHA256="f2e255aa0f376ef720727ff3568fd8b0614f91bb0b65a43ccd2e44119bb5d672"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/websockets-oracle-source"

rm -rf "$FETCH_ROOT"
git init -q "$FETCH_ROOT"
git -C "$FETCH_ROOT" remote add origin "$UPSTREAM_URL"
git -C "$FETCH_ROOT" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" FETCH_HEAD
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/compliance" "$ROOT/docs" "$ROOT/example" \
    "$ROOT/experiments" "$ROOT/fuzzing" "$ROOT/logo" "$ROOT/tests"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
