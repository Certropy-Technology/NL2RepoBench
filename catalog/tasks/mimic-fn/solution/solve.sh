#!/usr/bin/env bash
set -euo pipefail

upstream_url='https://github.com/sindresorhus/mimic-fn'
revision='3ee1e62d926ac0a5cf631815734d8e06a9381d72'
source_digest='52b0b045635fe457322cea36d04dcaa0b4944d4ac21d07448bb44f93dc3e8101'
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

git -C "$workdir" init -q
git -C "$workdir" remote add origin "$upstream_url"
git -C "$workdir" fetch --depth=1 origin "$revision" >/dev/null
test "$(git -C "$workdir" rev-parse FETCH_HEAD)" = "$revision"
git -C "$workdir" checkout -q --detach FETCH_HEAD
test "$(git -C "$workdir" rev-parse HEAD)" = "$revision"
test "$(git -C "$workdir" archive --format=tar --prefix=mimic-function/ "$revision" | sha256sum | cut -d' ' -f1)" = "$source_digest"

git -C "$workdir" show "$revision:index.js" > index.js
git -C "$workdir" show "$revision:index.d.ts" > index.d.ts
cat > package.json <<'JSON'
{"name":"mimic-function","version":"5.0.1","license":"MIT","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"sideEffects":false,"engines":{"node":">=18"},"files":["index.js","index.d.ts"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"mimic-function","version":"5.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mimic-function","version":"5.0.1","license":"MIT","type":"module","engines":{"node":">=18"}}}}
JSON
