#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference acquisition. The model Agent never receives this tree.
readonly UPSTREAM_URL="https://github.com/emirpasic/gods"
readonly UPSTREAM_REVISION="1d83d5ae39fbb0de45a60365791ff1c8b9bae953"
readonly SOURCE_ARCHIVE_SHA256="a92231b4759f195eb0dc3467badc410494761aeefedbf1afed96411b5f6f2b34"
readonly SOURCE_DIR="/tmp/go-gods-source"
readonly SOURCE_ARCHIVE="/tmp/go-gods-source.tar"

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

# The frozen upstream module targets Go 1.21. The task runtime is locked to
# Go 1.26.5; this directive-only adaptation preserves the source tree while
# making the Oracle workspace satisfy the runtime contract.
sed -i 's/^go 1\.21$/go 1.26.5/' /workspace/go.mod
