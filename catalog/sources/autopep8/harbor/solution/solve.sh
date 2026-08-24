#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# SOURCE_ARCHIVE_SHA256 is source_digest from catalog/tasks/autopep8/task.toml and
# equals sha256(git archive --format=tar 4046ad49e25b7fa1db275bf66b1b7d60600ac391), which is byte-reproducible
# for a fixed revision. A changed remote fails the check instead of being used.

UPSTREAM_URL="https://github.com/hhatto/autopep8"
UPSTREAM_REVISION="4046ad49e25b7fa1db275bf66b1b7d60600ac391"
SOURCE_ARCHIVE_SHA256="b0604345a9ac804f5eb6d30a0f779f61f64e679d651f43d16b2445b8ba799114"
SOURCE_DIR="/tmp/autopep8-source"
SOURCE_ARCHIVE="/tmp/autopep8-source.tar"

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
