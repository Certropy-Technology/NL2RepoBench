#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/Kludex/uvicorn"
readonly UPSTREAM_REVISION="9ee5694516b01f1d3d6ff9ed38f117fc869ee6ae"
readonly SOURCE_ARCHIVE_SHA256="ea14dd890be1bf0e78f1a5f4984794b9c1b762251a2701435f8d7c29145b0184"
readonly FETCH_ROOT="/tmp/uvicorn-oracle-source"
readonly WORKSPACE="/workspace"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$WORKSPACE"
rm -rf "$WORKSPACE/.github" "$WORKSPACE/CHANGELOG.md" "$WORKSPACE/docs" "$WORKSPACE/scripts" "$WORKSPACE/tests"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
