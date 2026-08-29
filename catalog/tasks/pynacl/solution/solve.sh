#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/pyca/pynacl"
readonly UPSTREAM_REVISION="fddb5f3a012baa28d5ead6497ab2ae72c4221246"
readonly SOURCE_ARCHIVE_SHA256="eec62a1ac27fd9cbe0452b5b7f12f2c1ca4f568c63b3b0b565a4ca0d3c7ac958"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/pynacl-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm "$ROOT/licenses/LICENSE.libsodium.txt"
cp "$ROOT/src/libsodium/LICENSE" "$ROOT/licenses/LICENSE.libsodium.txt"
find "$ROOT" -type l -delete
test -z "$(find "$ROOT" -type l -print -quit)"
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
