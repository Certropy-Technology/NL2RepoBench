#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/rosedblabs/rosedb"
UPSTREAM_REVISION="bcb43052ada686ec6d1345328e8299f502d3ef01"
SOURCE_ARCHIVE_SHA256="sha256:41153fd1e40c1e7b18b90d46cfcf3a4bdc93fdc54c286823d2966b01686f527e"
SOURCE_DIR="/tmp/go-rosedb-source"
SOURCE_ARCHIVE="/tmp/go-rosedb-source.tar"

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
sed -i 's/^go 1\.21$/go 1.26.5/' /workspace/go.mod
cp -a "$(dirname "$0")/module-bundle/vendor" /workspace/vendor
rm -rf /workspace/.github
