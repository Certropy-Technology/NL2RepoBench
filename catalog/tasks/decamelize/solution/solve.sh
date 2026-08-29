#!/usr/bin/env bash
set -euo pipefail

root=/workspace
tmp=/tmp/decamelize-oracle
rm -rf "$tmp"
mkdir -p "$tmp"
archive="$tmp/source.tar.gz"
curl --fail --silent --show-error --location \
  https://codeload.github.com/sindresorhus/decamelize/tar.gz/365e2e909c93c8a5e7c9398523290ba0b35a3a93 \
  -o "$archive"
test "$(sha256sum "$archive" | cut -d' ' -f1)" = 8fe6e3ec9a058ca9a0cf7a944058f4409dcf3c22b2a15cdc8b892e46163c5e55
rm -rf "$tmp/tree"
mkdir "$tmp/tree"
tar -xzf "$archive" -C "$tmp/tree" --strip-components=1
test "$(git -C "$tmp/tree" rev-parse 2>/dev/null || true)" = "" || true
test -s "$tmp/tree/index.js"
test -s "$tmp/tree/index.d.ts"
rm -rf "$root"
mkdir -p "$root"
cp "$tmp/tree/index.js" "$root/index.js"
cp "$tmp/tree/index.d.ts" "$root/index.d.ts"
cat > "$root/package.json" <<'JSON'
{"name":"decamelize","version":"6.0.1","description":"Convert a camelized string into a lowercased one","license":"MIT","type":"module","exports":"./index.js","types":"./index.d.ts","sideEffects":false,"files":["index.js","index.d.ts"]}
JSON
cat > "$root/package-lock.json" <<'JSON'
{"name":"decamelize","version":"6.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"decamelize","version":"6.0.1","license":"MIT","type":"module","exports":"./index.js","types":"./index.d.ts","sideEffects":false}}}
JSON
rm -rf "$tmp"
