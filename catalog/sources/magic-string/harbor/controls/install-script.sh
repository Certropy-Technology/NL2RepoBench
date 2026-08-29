#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/dist
printf '%s\n' '{"name":"magic-string","version":"1.2.3","type":"module","scripts":{"postinstall":"echo forbidden"},"exports":"./dist/index.mjs"}' > /workspace/package.json
printf '%s\n' '{"name":"magic-string","version":"1.2.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"magic-string","version":"1.2.3","type":"module"}}}' > /workspace/package-lock.json
printf '%s\n' 'export default class MagicString { constructor(value) { this.value = value; } toString() { return this.value; } }' > /workspace/dist/index.mjs
