#!/usr/bin/env bash
set -euo pipefail

revision="f94143765912425fb94ed6518d3a3d1c54f994d4"
archive_sha256="515825acb5478f8bf59c32403e5febc499a100ed0b1183f4596e8be2f38b5a19"
source_dir="/tmp/mdast-util-from-markdown-reference"
archive="/tmp/mdast-util-from-markdown-reference.tar"
rm -rf "$source_dir" "$archive" /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p "$source_dir" /workspace
cp /solution/source.tar "$archive"
printf '%s  %s\n' "$archive_sha256" "$archive" | sha256sum --check --strict
test "$(cat /solution/revision.txt)" = "$revision"
tar -xf "$archive" -C "$source_dir"
cp -a /solution/reference-build/. "$source_dir/"
cd "$source_dir"
npm pack --ignore-scripts --pack-destination "$source_dir" >/tmp/mdast-util-from-markdown-pack.log
tar -xzf "$source_dir/mdast-util-from-markdown-2.0.3.tgz" --strip-components=1 -C /workspace
cp /solution/reference-build/package-lock.json /workspace/package-lock.json
rm -f /workspace/*.tgz
test -f /workspace/index.js
test -f /workspace/index.d.ts
