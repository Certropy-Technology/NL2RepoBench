#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/aio-libs/frozenlist"
readonly UPSTREAM_REVISION="381c91e4663b067d5debab4cc19b400d3c459b44"
readonly SOURCE_ARCHIVE_SHA256="0fa249ef870bbbd9267b5427dbcbe7d5a3dc92d439ab677c1f9f6f84717f9b5b"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/frozenlist-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
find "$ROOT" -type l -delete
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests" "$ROOT/requirements"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
