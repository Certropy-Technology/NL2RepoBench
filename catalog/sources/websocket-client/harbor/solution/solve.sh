#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/websocket-client/websocket-client.git"
readonly UPSTREAM_REVISION="26f1c6439eb71489f2c5a2869942e049b78c2e41"
readonly SOURCE_ARCHIVE_SHA256="dd31f1cc888e206078188aa1b208ec9ffdc887ed5108f49ed837ecba3ddeccb2"
readonly FETCH_ROOT="/tmp/websocket-client-source"
readonly SOURCE_ARCHIVE="$FETCH_ROOT/source.tar"

rm -rf "$FETCH_ROOT"
mkdir -p "$FETCH_ROOT"
git clone --quiet "$UPSTREAM_URL" "$FETCH_ROOT/repository"
git -C "$FETCH_ROOT/repository" checkout --quiet --detach "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT/repository" rev-parse HEAD)" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT/repository" archive --format=tar --prefix=websocket-client/ "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
test "$(git -C "$FETCH_ROOT/repository" show -s --format=%s HEAD)" = "Fix custom dispatcher SSL errors and socket timeouts (#1049)"
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf "$SOURCE_ARCHIVE" -C /workspace --strip-components=1
rm -rf "$FETCH_ROOT"
