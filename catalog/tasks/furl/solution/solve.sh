#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/gruns/furl"
readonly UPSTREAM_REVISION="46d9ea79c98bb14b970a199fb924705d024f29ad"
readonly SOURCE_ARCHIVE_SHA256="11dfb073771de0ecf9117808aa37282afff150be2ba809f15e01f9802b21a197"
readonly FETCH_ROOT="/tmp/furl-oracle-source"
readonly ROOT="/workspace"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
