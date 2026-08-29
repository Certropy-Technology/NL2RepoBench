#!/usr/bin/env bash
set -euo pipefail

revision='f2fe88e2932603c038c61ca29de6ad5286148e1b'
source_digest='5264a90e047bccde14f6b5705630d7aaf5ade2fa2987f985d517aee1dd5cfc6a'
upstream='https://github.com/sindresorhus/quick-lru.git'
root='/tmp/quick-lru-oracle-source'
rm -rf "$root" /workspace/*
mkdir -p "$root" /workspace
git -C "$root" init -q
git -C "$root" remote add origin "$upstream"
git -C "$root" fetch --depth=1 origin "$revision"
test "$(git -C "$root" rev-parse FETCH_HEAD)" = "$revision"
archive_digest=$(git -C "$root" archive --format=tar FETCH_HEAD | sha256sum | awk '{print $1}')
test "$archive_digest" = "$source_digest"
mkdir "$root/tree"
git -C "$root" archive --format=tar FETCH_HEAD | tar -x -C "$root/tree"
cp "$root/tree/index.js" /workspace/index.js
cp "$root/tree/index.d.ts" /workspace/index.d.ts
printf '%s\n' '{"name":"quick-lru","version":"7.3.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"sideEffects":false,"files":["index.js","index.d.ts"]}' > /workspace/package.json
printf '%s\n' '{"name":"quick-lru","version":"7.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"quick-lru","version":"7.3.0"}}}' > /workspace/package-lock.json
