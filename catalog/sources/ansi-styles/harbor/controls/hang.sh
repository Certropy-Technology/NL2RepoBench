#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"ansi-styles","version":"7.0.0","type":"module","exports":"./index.js"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"ansi-styles","version":"7.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"ansi-styles","version":"7.0.0","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
const loop = () => { while (true) {} };
export default {bold: {open: '', close: ''}, rgbToAnsi256: loop};
export const modifierNames = ['bold'];
export const foregroundColorNames = [];
export const backgroundColorNames = [];
export const colorNames = [];
JS
