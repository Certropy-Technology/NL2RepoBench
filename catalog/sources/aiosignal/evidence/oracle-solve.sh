#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/aio-libs/aiosignal"
readonly UPSTREAM_REVISION="1c2bdc6dbd222463627638d2b46e9c3864e07597"
readonly SOURCE_ARCHIVE_SHA256="3cce05c57a65da0028ebd03992845c571d9d5368524529acd422a77e9f283bde"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/aiosignal-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/docs" "$ROOT/requirements"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
