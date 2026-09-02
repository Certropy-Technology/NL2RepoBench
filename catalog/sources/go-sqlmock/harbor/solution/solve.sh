#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/DATA-DOG/go-sqlmock"
readonly UPSTREAM_REVISION="4e29cb9ba9984db4da4003b5c813f3747f450bc7"
readonly SOURCE_ARCHIVE_SHA256="359bb2e809bade7c01d70eb5cb05a4ebef6c2a835a63293f0471c53d12b05734"
readonly SOURCE_DIR="/tmp/go-sqlmock-source"
readonly SOURCE_ARCHIVE="/tmp/go-sqlmock-source.tar"

rm -rf -- "$SOURCE_DIR" "$SOURCE_ARCHIVE"
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

# The frozen source declares Go 1.15. This directive-only adaptation keeps the
# upstream bytes intact while satisfying the locked runtime contract.
sed -i 's/^go 1\.15$/go 1.26.5/' /workspace/go.mod
# Go 1.26 vet rejects the legacy dynamic format-string form. This preserves the
# same error text without modifying frozen archive bytes or public behavior.
sed -i 's/fmt\.Errorf(err\.Error())/fmt.Errorf("%s", err)/g' /workspace/sqlmock.go
