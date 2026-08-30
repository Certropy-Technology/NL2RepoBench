#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This bundle is uploaded only to the trusted
# Oracle run; the model Agent receives no source-host authorization.
UPSTREAM_URL="https://github.com/regebro/tzlocal"
UPSTREAM_REVISION="6ef2c295f36c6053b13dc77e59e629d943e3ac91"
SOURCE_ARCHIVE_SHA256="c1466d3636fa00320760c2e5ae8f287c10f978a80b529690b6afb4bcdbebe935"
SOURCE_DIR="/tmp/tzlocal-source"
SOURCE_ARCHIVE="/tmp/tzlocal-source.tar"

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

git -C "$SOURCE_DIR" archive --format=tar --output "$SOURCE_ARCHIVE" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# Upstream's test fixture tree intentionally contains timezone symlinks. The
# generic candidate workspace boundary rejects all symlinks, so retain only the
# distribution inputs after verifying the complete frozen archive above.
rm -rf /workspace/tests /workspace/docs /workspace/.github
