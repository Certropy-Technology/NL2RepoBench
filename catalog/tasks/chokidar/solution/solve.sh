#!/usr/bin/env bash
set -euo pipefail

upstream_url='https://github.com/paulmillr/chokidar'
revision='0bc7bed37d6b018e5b11afcce329bbf797d6441f'
source_digest='sha256:db938843dec95dbe7faf8d926240f97429432002a760f9d68dfec049c367c0af'
source_dir=/tmp/chokidar-source
archive=/tmp/chokidar-source.tar
source_tree=/tmp/chokidar-source-tree

rm -rf "$source_dir" "$archive" "$source_tree"
git init "$source_dir" >/dev/null
git -C "$source_dir" remote add origin "$upstream_url"
git -C "$source_dir" fetch --depth 1 origin "$revision" >/dev/null
actual=$(git -C "$source_dir" rev-parse FETCH_HEAD)
test "$actual" = "$revision"
git -C "$source_dir" archive --format=tar "$actual" > "$archive"
test "sha256:$(sha256sum "$archive" | awk '{print $1}')" = "$source_digest"
mkdir "$source_tree"
tar -xf "$archive" -C "$source_tree"
test "sha256:$(sha256sum "$source_tree/LICENSE" | awk '{print $1}')" = 'sha256:bdfd5e0edb6089e6586c8f15e6a86fab83ffbeeda3b3b7b33734ccb8c5906965'

cp -a /solution/reference-build/. /workspace/
