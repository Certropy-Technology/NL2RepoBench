#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"jsdom","version":"1.0.0","main":"index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"jsdom","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"jsdom","version":"1.0.0"}}}
JSON
cat > index.js <<'JS'
const net = require("node:net");
class JSDOM {
  constructor() {
    const socket = net.connect({ host: "1.1.1.1", port: 443 });
    socket.on("error", () => {});
    socket.destroy();
    throw new Error("network is unavailable");
  }
}
module.exports = { JSDOM, VirtualConsole: class {}, CookieJar: class {}, requestInterceptor() {}, toughCookie: {} };
JS
