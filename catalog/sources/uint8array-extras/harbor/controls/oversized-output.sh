#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' '{"name":"uint8array-extras","version":"1.5.0","type":"module","exports":"./index.js"}' > package.json
printf '%s\n' '{"name":"uint8array-extras","version":"1.5.0","lockfileVersion":3,"packages":{"":{"name":"uint8array-extras","version":"1.5.0"}}}' > package-lock.json
printf '%s\n' 'export const isUint8Array = () => "x".repeat(300000);' > index.js
