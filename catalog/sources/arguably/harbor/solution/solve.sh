#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# SOURCE_ARCHIVE_SHA256 is source_digest from catalog/tasks/arguably/task.toml and
# equals sha256(git archive --format=tar 86648796c4a28fa59f6f059b673694929c7df534), which is byte-reproducible
# for a fixed revision. A changed remote fails the check instead of being used.

UPSTREAM_URL="https://github.com/treykeown/arguably"
UPSTREAM_REVISION="86648796c4a28fa59f6f059b673694929c7df534"
SOURCE_ARCHIVE_SHA256="125938624742c388ef9130408a620769742b5388b5ce1a04d028751224f6650e"
SOURCE_DIR="/tmp/arguably-source"
SOURCE_ARCHIVE="/tmp/arguably-source.tar"

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
