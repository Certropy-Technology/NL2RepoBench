#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/darccio/mergo"
readonly UPSTREAM_REVISION="a50922d8566636f636c4ff8892d725f244c49f44"
readonly SOURCE_ARCHIVE_SHA256="1c66e6ededb811969590605ef8049f3686a031adb552376c5771a474e57f1512"
readonly SOURCE_DIR="/tmp/go-mergo-source"
readonly SOURCE_ARCHIVE="/tmp/go-mergo-source.tar"

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
sed -i 's/^go 1\.18$/go 1.26.5/' /workspace/go.mod
mkdir -p /workspace/vendor
printf '# dario.cat/mergo\n' > /workspace/vendor/modules.txt
