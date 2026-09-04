#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
archive="$root/source.tar"
expected="ffbc51c1237344db6b47db8000aaa1668e89eb207f6a94b3a5b6472d5dda08d1"
test "$(sha256sum "$archive" | cut -d' ' -f1)" = "$expected"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
tar -xf "$archive" -C "$tmp"
source="$tmp/packages/micromark-util-chunked"
test -f "$source/dev/index.js"
cp "$source/dev/index.js" index.js
cat > package.json <<'JSON'
{"name":"micromark-util-chunked","version":"2.0.1","type":"module","exports":"./index.js","dependencies":{"micromark-util-symbol":"^2.0.0"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"micromark-util-chunked","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"micromark-util-chunked","version":"2.0.1","type":"module","exports":"./index.js","dependencies":{"micromark-util-symbol":"^2.0.0"}},"node_modules/micromark-util-symbol":{"version":"2.0.1","resolved":"https://registry.npmjs.org/micromark-util-symbol/-/micromark-util-symbol-2.0.1.tgz","integrity":"sha512-vs5t8Apaud9N28kgCrRUdEed4UJ+wWNvicHLPxCa9ENlYuAY31M0ETy5y1vA33YoNPDFTghEbnh6efaE8h4x0Q=="}}}
JSON
