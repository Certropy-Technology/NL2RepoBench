#!/usr/bin/env bash
set -euo pipefail

upstream_url='https://github.com/sindresorhus/p-map'
revision='22dda61ea29037ba85af25e84bc5efba77e62f44'
source_digest='ef544534472632d1bf174753ad75c21496119ff54bef8dedca45bb14cfe90ea2'
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

git -C "$workdir" init -q
git -C "$workdir" remote add origin "$upstream_url"
git -C "$workdir" fetch --depth=1 origin "$revision" >/dev/null
test "$(git -C "$workdir" rev-parse FETCH_HEAD)" = "$revision"
git -C "$workdir" checkout -q --detach FETCH_HEAD
test "$(git -C "$workdir" rev-parse HEAD)" = "$revision"
test "$(git -C "$workdir" archive --format=tar --prefix=p-map/ "$revision" | sha256sum | cut -d' ' -f1)" = "$source_digest"

git -C "$workdir" show "$revision:index.js" > index.js
git -C "$workdir" show "$revision:index.d.ts" > index.d.ts
cat > package.json <<'JSON'
{"name":"p-map","version":"7.0.7","license":"MIT","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"engines":{"node":">=18"},"files":["index.js","index.d.ts"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"p-map","version":"7.0.7","lockfileVersion":3,"requires":true,"packages":{"":{"name":"p-map","version":"7.0.7","license":"MIT","type":"module","engines":{"node":">=18"}}}}
JSON
