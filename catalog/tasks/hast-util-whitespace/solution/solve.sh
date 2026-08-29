#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
archive="$root/source.tar"
expected="d012e1fee404e631ad5a5b5aa3f338b413417e73f80b53d5d0c0e7a469f8e1be"
test "$(sha256sum "$archive" | cut -d' ' -f1)" = "$expected"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
tar -xf "$archive" -C "$tmp"
source="$tmp/hast-util-whitespace"
test -f "$source/index.js"
test -f "$source/lib/index.js"
cp "$source/index.js" index.js
mkdir -p lib
cp "$source/lib/index.js" lib/index.js
cat > package.json <<'JSON'
{"name":"hast-util-whitespace","version":"3.0.0","type":"module","exports":"./index.js","files":["index.js","lib/"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"hast-util-whitespace","version":"3.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"hast-util-whitespace","version":"3.0.0","type":"module","exports":"./index.js","files":["index.js","lib/"]}}}
JSON
