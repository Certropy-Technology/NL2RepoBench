#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/python-hyper/rfc3986"
readonly UPSTREAM_REVISION="7a64092490c1b3c4f354b9b14d060fa758d66848"
readonly SOURCE_ARCHIVE_SHA256="2a7c7ef66d324b1ba3196e6fdb5be491f7842e6ae96d0f5c3273f5bfc1824346"
readonly FETCH_ROOT="/tmp/rfc3986-oracle-source"
readonly ROOT="/workspace"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/docs"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
