#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# SOURCE_ARCHIVE_SHA256 is source_digest from catalog/tasks/flask-restful/task.toml and
# equals sha256(git archive --format=tar 88cce53a8cd65830bf1815185a42ba24e5db78c6), which is byte-reproducible
# for a fixed revision. A changed remote fails the check instead of being used.

UPSTREAM_URL="https://github.com/flask-restful/flask-restful"
UPSTREAM_REVISION="88cce53a8cd65830bf1815185a42ba24e5db78c6"
SOURCE_ARCHIVE_SHA256="82d29fe7e95e4f96dd230547c93d42517a4753d0b9c1c0fc9c0a819a259ee6c3"
SOURCE_DIR="/tmp/flask-restful-source"
SOURCE_ARCHIVE="/tmp/flask-restful-source.tar"

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
