#!/usr/bin/env bash
set -euo pipefail

revision='4c4ee027b830c35ff7605421a8ad92208f1b868a'
source_digest='e5bf56cf0d89d2f6a1191cfea63f77157060ed42dcb3dcedc738de54595103bb'
root=/tmp/locate-path-oracle
rm -rf "$root"
git init -q "$root"
git -C "$root" remote add origin https://github.com/sindresorhus/locate-path
git -C "$root" fetch -q --depth 1 origin "$revision"
test "$(git -C "$root" rev-parse FETCH_HEAD)" = "$revision"
git -C "$root" checkout -q --detach FETCH_HEAD
git -C "$root" archive --format=tar --output="$root/source.tar" HEAD
test "$(sha256sum "$root/source.tar" | cut -d' ' -f1)" = "$source_digest"

install -m 0644 "$root/index.js" /workspace/index.js
install -m 0644 "$root/index.d.ts" /workspace/index.d.ts
install -m 0644 "$root/license" /workspace/license
install -m 0644 /solution/runtime-package.json /workspace/package.json
install -m 0644 /solution/package-lock.json /workspace/package-lock.json
