#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/sysid/sse-starlette"
readonly UPSTREAM_REVISION="a815cd3682ce4b01f28e93f4bc59f3d6d5db3d00"
readonly SOURCE_ARCHIVE_SHA256="9945c5a862cd5d6cd5182347c2dad4a633caea80a4bcd21d7b82fcc0941a9703"
readonly FETCH_ROOT="/tmp/sse-starlette-oracle-source"
readonly WORKSPACE="/workspace"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$WORKSPACE"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$WORKSPACE"
rm -rf "$WORKSPACE/.github" "$WORKSPACE/examples" "$WORKSPACE/tests"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
