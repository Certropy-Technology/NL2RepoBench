#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{"name":"css-tree","version":"3.2.1","type":"module","exports":"./index.js"}
JSON
cat > /workspace/index.js <<'JS'
export const parse = () => ({type:'StyleSheet',children:[]});
JS
cat > /workspace/package-lock.json <<'JSON'
{"name":"css-tree","version":"3.2.1","lockfileVersion":3,"packages":{"":{"name":"css-tree","version":"3.2.1"}}}
JSON
