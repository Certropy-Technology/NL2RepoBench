#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/sarugaku/shellingham"
readonly UPSTREAM_REVISION="926401c4543b84f9f579932d30fb52a104639398"
readonly SOURCE_ARCHIVE_SHA256="b936de13a28f170163f749e81556a65834f630af7e7f08914749c5c64fff728b"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/shellingham-oracle-source"

rm -rf "$FETCH_ROOT"
git init -q "$FETCH_ROOT"
git -C "$FETCH_ROOT" remote add origin "$UPSTREAM_URL"
git -C "$FETCH_ROOT" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" checkout -q --detach FETCH_HEAD
test "$(git -C "$FETCH_ROOT" rev-parse HEAD)" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
