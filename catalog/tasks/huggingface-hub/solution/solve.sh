#!/usr/bin/env bash
set -euo pipefail

revision='c6be77fb44d91f474da963e5ad6fce4801811027'
expected_archive='sha256:64d379d7374b8afb92dbade7829d328982633d137941ea0aa088d17582e6294d'
workdir=/tmp/huggingface-hub-oracle
rm -rf "$workdir"
mkdir -p "$workdir" /workspace
git clone --no-checkout https://github.com/huggingface/huggingface_hub "$workdir/repo"
git -C "$workdir/repo" checkout --detach "$revision"
test "$(git -C "$workdir/repo" rev-parse HEAD)" = "$revision"
actual_archive="sha256:$(git -C "$workdir/repo" archive HEAD | sha256sum | awk '{print $1}')"
test "$actual_archive" = "$expected_archive"
git -C "$workdir/repo" archive HEAD | tar -xf - -C /workspace
# Harbor's candidate artifact boundary intentionally rejects symlinks. This
# documentation-only upstream link is outside the package and is omitted after
# the archive digest has already been checked.
rm -f /workspace/CLAUDE.md
