#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/tidwall/gjson"
UPSTREAM_REVISION="7d8b3821e9d2acf35e8a226b63fcf801078e9b96"
SOURCE_ARCHIVE_SHA256="sha256:91ec8257d29e04f0b67cac8641197ddb86d975138a8588d128bf4f27b447692a"
SOURCE_DIR="/tmp/go-gjson-source"
SOURCE_ARCHIVE="/tmp/go-gjson-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "unexpected source revision: $resolved_revision" >&2
    exit 1
fi
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "${SOURCE_ARCHIVE_SHA256#sha256:}" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
sed -i 's/^go 1\.23$/go 1.26.5/' /workspace/go.mod
cp -a "$(dirname "$0")/module-bundle/vendor" /workspace/vendor
rm -rf /workspace/.github
