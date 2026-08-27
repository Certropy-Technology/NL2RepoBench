#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"jsdom","version":"1.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"jsdom","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"jsdom","version":"1.0.0"}}}
JSON
cat > index.js <<'JS'
class JSDOM { constructor() { while (true) {} } }
module.exports = { JSDOM, VirtualConsole: class {}, CookieJar: class {}, requestInterceptor() {}, toughCookie: {} };
JS
