#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/hashicorp/go-multierror"
readonly UPSTREAM_REVISION="6d4d48630db25c3c83fa83ecd41dd8438b82963c"
readonly SOURCE_ARCHIVE_SHA256="1baf79ff1d042dda283afc4223d47f28b4684361d0bfb338957e873db53aa773"
readonly SOURCE_DIR="/tmp/go-multierror-source"
readonly SOURCE_ARCHIVE="/tmp/go-multierror-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD

resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
# The frozen upstream module declares Go 1.13. This directive-only adaptation
# keeps the source bytes and behavior while satisfying the locked runtime.
sed -i 's/^go 1\.13$/go 1.26.5/' /workspace/go.mod
