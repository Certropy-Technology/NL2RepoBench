#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This directory is uploaded only to the
# trusted Oracle agent. Task metadata remains no-network; the Oracle runner
# grants github.com only for this phase.
UPSTREAM_URL="https://github.com/tobgu/pyrsistent"
UPSTREAM_REVISION="0c0b7aec8cd25b1d2d8ba07b10acdefd0f38f2c7"
SOURCE_ARCHIVE_SHA256="349f0b11f5eea9c8fa69564a13757352d4136b3c635f4340c695f9da29834aa8"
SOURCE_DIR="/tmp/pyrsistent-source"
SOURCE_ARCHIVE="/tmp/pyrsistent-source.tar"

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
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
    | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# The verifier boundary accepts regular files only. Materialize the frozen
# archive's in-tree documentation links in the Oracle workspace without
# dereferencing anything outside the workspace.
while IFS= read -r -d '' link; do
    target="$(readlink -f -- "$link")"
    case "$target" in
        /workspace/*) ;;
        *)
            echo "archive link escapes workspace: $link -> $target" >&2
            exit 1
            ;;
    esac
    if [[ ! -f "$target" ]]; then
        echo "archive link target is not a regular file: $link -> $target" >&2
        exit 1
    fi
    temporary="${link}.materialized.$$"
    cp -L -- "$link" "$temporary"
    rm -- "$link"
    mv -- "$temporary" "$link"
done < <(find /workspace -type l -print0)
