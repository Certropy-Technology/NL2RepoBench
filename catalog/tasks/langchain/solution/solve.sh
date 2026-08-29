#!/usr/bin/env bash
set -euo pipefail

revision=502b2b445b89b753cd468df979b71503f8f99425
expected_archive=324411670c256bcbdf4dfab75a1b099910b6fc8880a4e9722270288c5a1e4ccd
source_root=/tmp/langchain-reference
archive=/tmp/langchain-v1-source.tar

rm -rf "$source_root" "$archive"
git init -q "$source_root"
git -C "$source_root" remote add origin https://github.com/langchain-ai/langchain
git -C "$source_root" fetch -q --depth=1 origin "$revision"
resolved=$(git -C "$source_root" rev-parse FETCH_HEAD^{commit})
test "$resolved" = "$revision"
git -C "$source_root" archive --format=tar --output "$archive" "$resolved" libs/langchain_v1
actual_archive=$(sha256sum "$archive" | cut -d ' ' -f 1)
test "$actual_archive" = "$expected_archive"
git -C "$source_root" checkout -q --detach "$resolved"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$source_root/libs/langchain_v1/." /workspace/
