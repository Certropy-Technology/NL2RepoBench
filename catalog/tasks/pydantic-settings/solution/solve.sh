#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. The solution directory is uploaded
# exclusively to the trusted Oracle run, never built into the model image.
UPSTREAM_URL="https://github.com/pydantic/pydantic-settings"
UPSTREAM_REVISION="d26fc0c3944fe68cf169f86386988bb83e3df2d8"
SOURCE_ARCHIVE_SHA256="57b7dab78777c75bcc2c138d561dea097afe3088c0b3e7f1d67481d6b4bbd5aa"
SOURCE_DIR="/tmp/pydantic-settings-source"
SOURCE_ARCHIVE="/tmp/pydantic-settings-source.tar"

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
