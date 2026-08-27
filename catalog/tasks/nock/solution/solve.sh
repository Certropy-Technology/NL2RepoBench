#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. The solution directory is uploaded
# only for the trusted Oracle run; model runs remain offline and never receive
# these bytes or a source-host override.
readonly UPSTREAM_URL="https://github.com/nock/nock"
readonly UPSTREAM_REVISION="1ee467c68d601ddc22629d7a657061e6c27097c2"
readonly SOURCE_ARCHIVE_SHA256="8c54a05e667935a42b69be72e1a95d0fb027805068dcc11b0d42b654525e0918"
readonly SOURCE_DIR="/tmp/nock-source"
readonly SOURCE_ARCHIVE="/tmp/nock-source.tar"
readonly SOLUTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" |
  sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$SOURCE_DIR/index.js" "$SOURCE_DIR/lib" "$SOURCE_DIR/types" /workspace/
install -m 0644 "$SOLUTION_DIR/package.json" /workspace/package.json
install -m 0644 "$SOLUTION_DIR/package-lock.json" /workspace/package-lock.json
