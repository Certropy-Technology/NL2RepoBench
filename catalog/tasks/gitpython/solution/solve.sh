#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/gitpython-developers/GitPython"
readonly UPSTREAM_REVISION="3481da9618e69063464c94447167d83bd45505a9"
readonly SOURCE_ARCHIVE_SHA256="8d6e3300bf477e7276e3a7280abf0bcb84c0f6b63ce05caa1ca70bfa4e50e8d8"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/gitpython-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/fuzzing" "$ROOT/test" "$ROOT/gitdb" "$ROOT/smmap"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
