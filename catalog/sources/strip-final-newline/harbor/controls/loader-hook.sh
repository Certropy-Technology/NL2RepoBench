#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"name":"strip-final-newline","version":"4.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","evil-loader.mjs","node-options.txt"]}' > /workspace/package.json
printf '%s\n' '{"name":"strip-final-newline","version":"4.0.0","lockfileVersion":3,"packages":{"":{"name":"strip-final-newline","version":"4.0.0","type":"module"}}}' > /workspace/package-lock.json
printf '%s\n' 'export default input => input;' > /workspace/index.js
printf '%s\n' 'throw new Error("untrusted loader executed");' > /workspace/evil-loader.mjs
printf '%s\n' 'NODE_OPTIONS=--loader=./evil-loader.mjs' > /workspace/node-options.txt
