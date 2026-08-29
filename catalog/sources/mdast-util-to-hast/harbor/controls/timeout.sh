#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/lib
printf '%s\n' '{"name":"mdast-util-to-hast","version":"13.2.1","type":"module","exports":"./index.js","files":["index.js","index.d.ts","lib/"]}' > /workspace/package.json
printf '%s\n' '{"name":"mdast-util-to-hast","version":"13.2.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-to-hast","version":"13.2.1"}}}' > /workspace/package-lock.json
printf 'while (true) {}\n' > /workspace/index.js
printf 'export {};\n' > /workspace/index.d.ts
