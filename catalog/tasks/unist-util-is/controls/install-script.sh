#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{"name":"unist-util-is","version":"6.0.1","type":"module","exports":"./index.js","scripts":{"preinstall":"node -e \"require('node:fs').writeFileSync('/tmp/install-script-ran','yes')\""},"dependencies":{"@types/unist":"3.0.3"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"unist-util-is","version":"6.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"unist-util-is","version":"6.0.1","hasInstallScript":true,"dependencies":{"@types/unist":"3.0.3"}},"node_modules/@types/unist":{"version":"3.0.3","resolved":"https://registry.npmjs.org/@types/unist/-/unist-3.0.3.tgz","integrity":"sha512-ko/gIFJRv177XgZsZcBwnqJN5x/Gien8qNOn0D5bQU/zAzVf9Zt3BlcUiLqhV9y4ARk0GbT3tnUiPNgnTXzc/Q=="}}}
JSON
cat > /workspace/index.js <<'JS'
export const is = () => true
export const convert = () => () => true
JS
