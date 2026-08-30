#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/gitpython-developers/smmap"
readonly UPSTREAM_REVISION="1ca8ee3f8a0fe17b68ee20d21fa71eedb75c60fe"
readonly SOURCE_ARCHIVE_SHA256="ade73659d62214ea02e04591c5838a37e6c878aafcbc5866026489ed9e404299"
readonly FETCH_ROOT="/tmp/smmap-oracle-source"
readonly ROOT="/workspace"

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
