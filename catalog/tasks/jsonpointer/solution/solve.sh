#!/usr/bin/env bash
set -euo pipefail

upstream=https://github.com/stefankoegl/python-json-pointer
revision=5998f951dcc5ace60f67f35afe6778c445401a07
expected=f8379acb630446222410697e7e7f33830294f07681de2ae941db723dd4ae989c
source_dir=/tmp/jsonpointer-source
archive=/tmp/jsonpointer-source.tar

rm -rf "$source_dir" "$archive"
git init -q "$source_dir"
git -C "$source_dir" remote add origin "$upstream"
git -C "$source_dir" fetch -q --depth 1 origin "$revision"
test "$(git -C "$source_dir" rev-parse FETCH_HEAD)" = "$revision"
git -C "$source_dir" archive --format=tar FETCH_HEAD > "$archive"
test "$(sha256sum "$archive" | awk '{print $1}')" = "$expected"
tar -xf "$archive" -C /workspace
