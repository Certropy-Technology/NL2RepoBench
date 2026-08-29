#!/usr/bin/env bash
set -euo pipefail

revision='2d3c2a9cc518326daf99a383f07c4d3c44317e4d'
expected_source_digest='sha256:e08c0dc34cb6ca21d5ebff08053403b8bf4e91efb97aa2eccf25f17d879bb217'
work="$(mktemp -d /tmp/go-uuid-oracle.XXXXXX)"
trap 'rm -rf -- "$work"' EXIT

git -C "$work" init -q
git -C "$work" remote add origin https://github.com/google/uuid.git
git -C "$work" fetch --depth 1 origin "$revision"
test "$(git -C "$work" rev-parse FETCH_HEAD)" = "$revision"
actual="$(git -C "$work" archive --format=tar --prefix=go-uuid/ "$revision" | sha256sum | awk '{print "sha256:" $1}')"
test "$actual" = "$expected_source_digest"
mkdir -p /workspace
git -C "$work" archive --format=tar --prefix=go-uuid/ "$revision" | tar -x -C /workspace
cp -a /workspace/go-uuid/. /workspace/
rm -rf /workspace/go-uuid

# The frozen upstream module predates the exact toolchain directive required by
# this lane. This packaging-only remediation is applied in the Oracle image
# and is also required of candidate workspaces by the public specification.
printf 'module github.com/google/uuid\n\ngo 1.26.5\n' > /workspace/go.mod
: > /workspace/go.sum
printf '%s\n' "oracle prepared $revision $actual"
