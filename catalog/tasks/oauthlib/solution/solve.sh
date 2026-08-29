#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/oauthlib/oauthlib"
readonly UPSTREAM_REVISION="40b0ab56da3682c2484a4b78bbff309f8025d950"
readonly SOURCE_ARCHIVE_SHA256="7d459f401eb8595ad42c7a77edfb0ee17b67acf27213812d1c13a1ed505d7c2b"
readonly FETCH_ROOT="/tmp/oauthlib-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$FETCH_ROOT/source.tar" -C /workspace
echo "restored oauthlib $UPSTREAM_REVISION"
