#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/executablebooks/mdurl"
readonly UPSTREAM_REVISION="524d2edbbcb8bb48301ba716c7482827bcabb281"
readonly SOURCE_ARCHIVE_SHA256="f0caa116deb9e08c885a2ae9df766a05b9a4974ea684d298fbaed0f2d0884595"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/mdurl-oracle-source"

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
