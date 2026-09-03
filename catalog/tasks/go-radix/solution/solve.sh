#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/armon/go-radix"
readonly UPSTREAM_REVISION="54df44f2176c4a553657a4f0dbe6fdb108288be3"
readonly SOURCE_ARCHIVE_SHA256="71091da25cb789fffd397ff8b4e1b460e88dda2ef31ae981d520426f26b8ff47"
readonly SOURCE_DIR="/tmp/go-radix-source"
readonly SOURCE_ARCHIVE="/tmp/go-radix-source.tar"

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

git -C "$SOURCE_DIR" archive --format=tar --prefix=go-radix/ "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace --strip-components=1

# The frozen repository predates the locked evaluator toolchain and has no
# module directive. This changes only the Oracle workspace metadata.
printf 'module github.com/armon/go-radix\n\ngo 1.26.5\n' > /workspace/go.mod
: > /workspace/go.sum
mkdir -p /workspace/vendor
: > /workspace/vendor/modules.txt
