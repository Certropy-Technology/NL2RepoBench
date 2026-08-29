#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/yaml/pyyaml"
readonly UPSTREAM_REVISION="34a9bf82357f4952d8f194a5a31f1c39743652d0"
readonly SOURCE_ARCHIVE_SHA256="18387c6163aa3de3221240cade5f77768963c1096061119d67503462049eab68"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/pyyaml-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
printf 'restored %s at %s\n' "$UPSTREAM_URL" "$UPSTREAM_REVISION"
