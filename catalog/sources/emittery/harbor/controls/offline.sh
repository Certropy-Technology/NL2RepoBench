#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"emittery","version":"2.0.0","type":"module","exports":{"types":"./index.d.ts","default":"./index.js"},"files":["index.js","index.d.ts"]}
JSON
cat > package-lock.json <<'JSON'
{"name":"emittery","version":"2.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"emittery","version":"2.0.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export default class Emittery {
  on() { return () => {}; }
  async emit() { await fetch('https://registry.npmjs.org/emittery'); }
}
JS
printf 'export default class Emittery {}\n' > index.d.ts
