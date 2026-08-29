#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/networkx/networkx"
readonly UPSTREAM_REVISION="ff25fa8296d16ad63d6a02b2d9f979dcafbb50ae"
readonly SOURCE_ARCHIVE_SHA256="438319b0534eede5966d6aa88dd6bcea3e0fddb3164040fe982ef5d96580737c"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/networkx-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout --no-tags "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/benchmarks" "$ROOT/doc" "$ROOT/examples" "$ROOT/requirements" "$ROOT/tools"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
