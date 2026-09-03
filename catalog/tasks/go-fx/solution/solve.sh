#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/antonmedv/fx"
UPSTREAM_REVISION="4f31cd3a0c5d66f1b4290a2719bab14a5cee8ebe"
SOURCE_ARCHIVE_SHA256="sha256:efe539dae8dab090b45e4224eaae1e476e61fc3ec4156212087d67dd39f5297c"
SOURCE_DIR="/tmp/go-fx-source"
SOURCE_ARCHIVE="/tmp/go-fx-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "unexpected source revision: $resolved_revision" >&2
    exit 1
fi
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "${SOURCE_ARCHIVE_SHA256#sha256:}" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
cat > /workspace/go.mod <<'MOD'
module github.com/antonmedv/fx

go 1.26.5

require github.com/rivo/uniseg v0.4.7
MOD
cp "$(dirname "$0")/module-bundle/go.sum" /workspace/go.sum
cp -a "$(dirname "$0")/module-bundle/vendor" /workspace/vendor
