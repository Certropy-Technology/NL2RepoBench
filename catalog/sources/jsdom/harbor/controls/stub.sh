#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"jsdom","version":"1.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"jsdom","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"jsdom","version":"1.0.0"}}}
JSON
cat > index.js <<'JS'
class JSDOM {}
class VirtualConsole {}
class CookieJar {}
module.exports = { JSDOM, VirtualConsole, CookieJar, requestInterceptor() {}, toughCookie: {} };
JS
