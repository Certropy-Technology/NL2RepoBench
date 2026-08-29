#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. This directory is never included
# in the model Agent image. The source host is authorized only for Oracle.
UPSTREAM_URL="https://github.com/valyala/bytebufferpool"
UPSTREAM_REVISION="18533face0dfe7042f8157bba9010bd7f8df54b1"
SOURCE_ARCHIVE_SHA256="a070768e029bc8a99e64611b6cf9905c193fe51b7a17044d3fb5b5fec7ca08cd"
SOURCE_DIR="/tmp/go-bytebufferpool-source"
SOURCE_ARCHIVE="/tmp/go-bytebufferpool-source.tar"

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

# The frozen upstream module declares Go 1.12. This is an environment-only
# modernization; the source archive above remains digest-verified and the
# public API is unchanged.
cd /workspace
go mod edit -go=1.26.5
: > go.sum
mkdir -p vendor
: > vendor/modules.txt

env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
    GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
    go test -count=1 ./...
