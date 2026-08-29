#!/usr/bin/env bash
set -euo pipefail

repo="${S3FS_ORACLE_REPO:-https://github.com/fsspec/s3fs}"
revision="d3dd9b75bdd699f230d3fd0faffd6ce7a31b1cf3"
expected_archive="0fe21881f4329f8981e139200722a7b6934065d40f976cd3d0afd9878f5a5bdf"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git clone --filter=blob:none --no-checkout --no-tags "$repo" "$work/source"
git -C "$work/source" checkout --detach "$revision"
test "$(git -C "$work/source" rev-parse HEAD)" = "$revision"
git -C "$work/source" archive --format=tar --prefix=s3fs/ "$revision" > "$work/s3fs.tar"
test "$(sha256sum "$work/s3fs.tar" | cut -d' ' -f1)" = "$expected_archive"
mkdir -p /workspace
tar -xf "$work/s3fs.tar" -C /workspace --strip-components=1
printf 'Oracle source revision verified: %s\n' "$revision"
