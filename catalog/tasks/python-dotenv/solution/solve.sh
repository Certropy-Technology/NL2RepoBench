#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="$(dirname "$0")/source.tar"
readonly SOURCE_SHA256="e6ec01e11aa990e59b45e40b3f44b597cef8d107fc270e261974ab15fa40371e"

printf '%s  %s\n' "$SOURCE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
# The frozen tree contains documentation-only symlinks. Candidate artifact
# policy accepts regular files and directories only; these links are not part
# of the package build or bounded runtime contract.
find /workspace/docs -type l -delete
