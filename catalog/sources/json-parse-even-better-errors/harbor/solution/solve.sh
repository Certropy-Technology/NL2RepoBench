#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/npm/json-parse-even-better-errors.git"
UPSTREAM_REVISION="098b8d00e72e4807adba733c2cdde686b2b9bf82"
SOURCE_ARCHIVE_SHA256="6bcf80e775ad5481a30fc401ede155fc49ebc44ae03a2f76f323430ce28c5f9f"
SOURCE_DIR="/tmp/json-parse-even-better-errors-source"
SOURCE_ARCHIVE="/tmp/json-parse-even-better-errors-source.tar"

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
rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
cat > /workspace/package.json <<'JSON'
{"name":"json-parse-even-better-errors","version":"6.0.0","main":"lib/index.js"}
JSON
printf '%s\n' '{"name":"json-parse-even-better-errors","version":"6.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"json-parse-even-better-errors","version":"6.0.0"}}}' > /workspace/package-lock.json
