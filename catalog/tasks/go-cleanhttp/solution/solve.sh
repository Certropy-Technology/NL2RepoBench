#!/usr/bin/env bash
set -euo pipefail

readonly WORKSPACE=/workspace
readonly UPSTREAM_URL="https://github.com/hashicorp/go-cleanhttp"
readonly UPSTREAM_REVISION="2901fbf3e0ecb2512cd7d278977a6b4ae0342ac0"
readonly SOURCE_ARCHIVE_SHA256="e1937b5e35049788a73ef0ecbc7107a2e38a27f09876fd71ccdbf1809305d83f"
readonly SOURCE_DIR=/tmp/go-cleanhttp-source
readonly SOURCE_ARCHIVE=/tmp/go-cleanhttp-source.tar

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    printf 'unexpected source revision: %s\n' "$resolved_revision" >&2
    exit 1
fi
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$WORKSPACE"
cat > "$WORKSPACE/go.mod" <<'MOD'
module github.com/hashicorp/go-cleanhttp

go 1.26.5
MOD
cp /opt/go-module-bundle/go.sum "$WORKSPACE/go.sum"
cp -a /opt/go-module-bundle/vendor "$WORKSPACE/vendor"
