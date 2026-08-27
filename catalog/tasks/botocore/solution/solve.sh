#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. The solution directory is uploaded
# only to the trusted Oracle run and is never included in the Agent image.
UPSTREAM_URL="https://github.com/boto/botocore"
UPSTREAM_REVISION="577f39f278bec5635ffdc7efd6d99f17687419e2"
SOURCE_ARCHIVE_SHA256="13720b9e9a36c235c45535e1364ec7e5faddd47789b87cd27865b1ec9eafa9a3"
SOURCE_DIR="/tmp/botocore-source"
SOURCE_ARCHIVE="/tmp/botocore-source.tar"

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
rm -rf /workspace/.github
