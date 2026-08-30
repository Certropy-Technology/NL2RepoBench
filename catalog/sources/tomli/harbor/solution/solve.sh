#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/hukkin/tomli"
readonly UPSTREAM_REVISION="5a77b12a7a9f052ce5a20c335d2825658f6aea52"
readonly SOURCE_ARCHIVE_SHA256="200b6c7f01286ef30a889ff4742c93e333049821badb15b53b8d2c3af584e322"
readonly FETCH_ROOT="/tmp/tomli-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$FETCH_ROOT/source.tar" -C /workspace
echo "restored tomli at $UPSTREAM_REVISION"
