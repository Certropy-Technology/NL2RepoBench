#!/usr/bin/env bash
set -euo pipefail

revision="01810fd7f1123a3e2e52a7320d5eb49215ca2474"
source_digest="08ed69c80663ed3926e5bce8db647519324b4b20ca9eec839acbd4d5c3fae9cc"
source_dir="/tmp/go-ordered-map-oracle-source"
rm -rf "$source_dir"
git init -q "$source_dir"
git -C "$source_dir" remote add origin https://github.com/iancoleman/orderedmap
git -C "$source_dir" fetch --depth=1 origin "$revision"
test "$(git -C "$source_dir" rev-parse FETCH_HEAD)" = "$revision"
test "$(git -C "$source_dir" archive --format=tar "$revision" | sha256sum | awk '{print $1}')" = "$source_digest"
git -C "$source_dir" checkout -q --detach "$revision"

find "$source_dir" -mindepth 1 -maxdepth 1 ! -name .git -exec cp -a {} /workspace/ \;
go mod edit -go=1.26.5
: > go.sum
rm -rf .git
