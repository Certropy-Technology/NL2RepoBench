#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/andybalholm/brotli"
UPSTREAM_REVISION="6b8aef6ece266fa87b925ce3a913bc30dc4b7b70"
SOURCE_ARCHIVE_SHA256="98f4e975d6de4ee7da812c21d147b57663e25e72a5e53db6673a1d5ffcaa14f8"
SOURCE_DIR="/tmp/go-brotli-source"
SOURCE_ARCHIVE="/tmp/go-brotli-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD^{commit})"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "unexpected source revision: $resolved_revision" >&2
    exit 1
fi
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
cp -a /opt/go-module-bundle/vendor /workspace/vendor
# The frozen upstream declares the minimum supported Go version (1.22). The
# locked Harbor runtime requires an exact 1.26.5 directive for offline install.
sed -i 's/^go 1\.22$/go 1.26.5/' /workspace/go.mod
printf '%s\n' "oracle source $UPSTREAM_REVISION verified $SOURCE_ARCHIVE_SHA256"

