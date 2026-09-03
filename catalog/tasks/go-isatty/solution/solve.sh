#!/usr/bin/env bash
set -euo pipefail

WORKSPACE=/workspace
readonly UPSTREAM_URL="https://github.com/mattn/go-isatty"
readonly UPSTREAM_REVISION="c44dc0b9c702c76577fdb7898032969e0611efc2"
readonly SOURCE_ARCHIVE_SHA256="777f5b348771b16c22295784ad7b225254e1408ff983df7827b65ca819c5c3db"
readonly SOURCE_DIR="/tmp/go-isatty-source"
readonly SOURCE_ARCHIVE="/tmp/go-isatty-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "unexpected source revision: $resolved_revision" >&2
    exit 1
fi
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$WORKSPACE"
sed -i 's/^go 1\.20$/go 1.26.5/' "$WORKSPACE/go.mod"
cat > "$WORKSPACE/go.mod" <<'MOD'
module github.com/mattn/go-isatty

go 1.26.5

require golang.org/x/sys v0.28.0
MOD
cp /opt/go-module-bundle/go.sum "$WORKSPACE/go.sum"
cp -a /opt/go-module-bundle/vendor "$WORKSPACE/vendor"
