#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' '{"name":"range-parser","version":"1.2.1","main":"index.js"}' > package.json
printf '%s\n' '{"name":"range-parser","version":"1.2.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"range-parser","version":"1.2.1"}}}' > package-lock.json
printf '%s\n' "'use strict'; module.exports = function () { return -2 }" > index.js
printf '%s\n' 'NODE_OPTIONS=--require=/tmp/evil.js' > node-options.txt
