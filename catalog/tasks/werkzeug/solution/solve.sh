#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/pallets/werkzeug"
readonly UPSTREAM_REVISION="0005c79e09bae5f4cc2bd8ccd468d7dafe24a455"
readonly SOURCE_ARCHIVE_SHA256="239273928c7e07cb69a74fa21305921f41901f59b7e7d188eb46c47e9855ae4c"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/werkzeug-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/docs" "$ROOT/examples"
echo "restored Werkzeug $UPSTREAM_REVISION"
