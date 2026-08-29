#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"mdast-util-mdxjs-esm","version":"2.0.1","type":"module","exports":{".":"./index.js","./adapter":"./adapter.js"}}
JSON
cat > index.js <<'JS'
export {run} from './adapter.js';
JS
cat > adapter.js <<'JS'
export async function run() { return fetch('https://example.invalid/blocked'); }
JS
cat > package-lock.json <<'JSON'
{"name":"mdast-util-mdxjs-esm","version":"2.0.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-mdxjs-esm","version":"2.0.1","type":"module"}}}
JSON
