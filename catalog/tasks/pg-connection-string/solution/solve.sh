#!/usr/bin/env bash
set -euo pipefail

readonly REVISION='c9e57617bc92c2ded23a75345f50eadc527bd131'
readonly SOURCE_DIGEST='87330e434dc4d6c02e9f662910d7fcc81af2cc9bbb7bf97d08f72046766c43a6'
readonly REPOSITORY='https://github.com/brianc/node-postgres.git'

workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
git init -q "$workdir/source"
git -C "$workdir/source" remote add origin "$REPOSITORY"
git -C "$workdir/source" fetch -q --depth 1 origin "$REVISION"
actual=$(git -C "$workdir/source" rev-parse FETCH_HEAD)
test "$actual" = "$REVISION"
git -C "$workdir/source" checkout -q --detach "$actual"
archive_digest=$(git -C "$workdir/source" archive --format=tar "$actual" | sha256sum | awk '{print $1}')
test "$archive_digest" = "$SOURCE_DIGEST"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cp "$workdir/source/packages/pg-connection-string/index.js" /workspace/index.js
cp "$workdir/source/packages/pg-connection-string/index.d.ts" /workspace/index.d.ts
cat > /workspace/package.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","main":"./index.js","types":"./index.d.ts","exports":{".":{"types":"./index.d.ts","require":"./index.js","default":"./index.js"}},"files":["index.js","index.d.ts"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"pg-connection-string","version":"2.14.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"pg-connection-string","version":"2.14.0"}}}
JSON
