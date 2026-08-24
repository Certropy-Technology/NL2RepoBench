#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is not part of the
# agent image build context, so this never reaches the model agent. Task
# metadata still declares no-network; authorize the source host for an Oracle
# run only, e.g. `harbor run -a oracle --allow-agent-hosts codeload.github.com`.
#
# This upstream marks a file 'export-subst' in .gitattributes and derives its
# version from git, so the tag ref is fetched rather than the bare commit:
#
#   * a SHA-only shallow fetch carries no tags, so `git archive` substitutes an
#     empty describe-name and the tarball digest does not reproduce;
#   * the package version would resolve to 0.0, failing the upstream packaging
#     test that compares metadata.version() with __version__.
#
# The commit SHA is asserted after fetching, so a moved tag is rejected.

UPSTREAM_URL="https://github.com/hynek/structlog"
UPSTREAM_REVISION="f5cbae43c8fd2f20eeb933e5af0134225d3daa9b"
UPSTREAM_TAG="23.2.0"
SOURCE_ARCHIVE_SHA256="c91271214b2cb2583e642edbb058e4c1b8723818ad2d757cbe00cff2aee8af07"
SOURCE_DIR="/tmp/structlog-source"
SOURCE_ARCHIVE="/tmp/structlog-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"

git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin     "refs/tags/${UPSTREAM_TAG}:refs/tags/${UPSTREAM_TAG}"

# Intentionally no checkout: it would add HEAD to the substituted ref list and
# change the archive. git archive reads the object database directly.
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse "refs/tags/${UPSTREAM_TAG}^{commit}")"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "tag ${UPSTREAM_TAG} resolved to $resolved_revision, expected $UPSTREAM_REVISION" >&2
    exit 1
fi

git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
rm -rf /workspace/.github
