#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. Harbor uploads this script only to the
# trusted Oracle and grants the exact source host for that run.
readonly UPSTREAM_URL="https://github.com/python/importlib_metadata"
readonly UPSTREAM_REVISION="9757b400ee412ddb1d685f139ed3300f607c059a"
readonly SOURCE_ARCHIVE_SHA256="921c3509959fd9a207da52966da0d4fb2da167e51a9b7a4abb8eff4f46abbf39"
readonly LICENSE_SHA256="074e6e32c86a4c0ef8b3ed25b721ca23aca83df277cd88106ef7177c354615ff"
readonly SOURCE_DIR="/tmp/importlib-metadata-source"
readonly SOURCE_ARCHIVE="/tmp/importlib-metadata-source.tar"
readonly SOLUTION_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

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
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
    | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
printf '%s  %s\n' "$LICENSE_SHA256" "$SOLUTION_DIR/LICENSE" \
    | sha256sum --check --strict
install -m 0644 "$SOLUTION_DIR/LICENSE" /workspace/LICENSE
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
