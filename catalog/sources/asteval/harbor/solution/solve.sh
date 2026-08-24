#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# SOURCE_ARCHIVE_SHA256 is source_digest from catalog/tasks/asteval/task.toml and
# equals sha256(git archive --format=tar 633bdc4ee855d426b7dcce8d1c0d907dadde4767), which is byte-reproducible
# for a fixed revision. A changed remote fails the check instead of being used.

UPSTREAM_URL="https://github.com/lmfit/asteval"
UPSTREAM_REVISION="633bdc4ee855d426b7dcce8d1c0d907dadde4767"
SOURCE_ARCHIVE_SHA256="c7cf4dab6b04be26a7ad41ccf05b9980a371c97db6fcc2277b1fb2628184b2a3"
SOURCE_DIR="/tmp/asteval-source"
SOURCE_ARCHIVE="/tmp/asteval-source.tar"

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
