#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/pydantic/typing-inspection"
readonly UPSTREAM_REVISION="83d4dbb74fc367db4403c76be8c0f83cd4b63fbe"
readonly SOURCE_ARCHIVE_SHA256="ae6f6606c1f75628cae5254817e4448da25225123f70ae06ae7e406d6db7418b"
readonly FETCH_ROOT="/tmp/typing-inspection-oracle-source"
readonly WORKSPACE="/workspace"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$WORKSPACE"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$WORKSPACE"
rm -rf "$WORKSPACE/.github" "$WORKSPACE/docs" "$WORKSPACE/tests"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
