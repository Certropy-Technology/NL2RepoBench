#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"mdast-util-mdxjs-esm","version":"2.0.1","type":"module","exports":"./index.js"}
JSON
cat > index.js <<'JS'
export function mdxjsEsmFromMarkdown() { return {}; }
export function mdxjsEsmToMarkdown() { return {}; }
JS
cat > package-lock.json <<'JSON'
{"name":"mdast-util-mdxjs-esm","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-mdxjs-esm","version":"2.0.1","type":"module"}}}
JSON
