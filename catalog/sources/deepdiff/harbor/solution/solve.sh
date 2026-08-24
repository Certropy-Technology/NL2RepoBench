#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# SOURCE_ARCHIVE_SHA256 is source_digest from catalog/tasks/deepdiff/task.toml and
# equals sha256(git archive --format=tar ba85943dc0d188f631f7c0f37d64241d489ad1e1), which is byte-reproducible
# for a fixed revision. A changed remote fails the check instead of being used.

UPSTREAM_URL="https://github.com/seperman/deepdiff"
UPSTREAM_REVISION="ba85943dc0d188f631f7c0f37d64241d489ad1e1"
SOURCE_ARCHIVE_SHA256="0718f90ecd7eeb805fa0ece3f66da47f4555613c3472432f868d4456def0d44e"
SOURCE_DIR="/tmp/deepdiff-source"
SOURCE_ARCHIVE="/tmp/deepdiff-source.tar"

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
rm -rf /workspace/.github
