#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/sybrenstuvel/python-rsa"
UPSTREAM_REVISION="42b0e14ffbeeb9d99d1037e6440a2cc61780e4ea"
SOURCE_ARCHIVE_SHA256="d5f3ae5ac30dc2c284dd449bb8f3aada2612ed41a0eab1decdd1d70b11806ed8"
SOURCE_DIR="/tmp/rsa-source"
SOURCE_ARCHIVE="/tmp/rsa-source.tar"

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

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
