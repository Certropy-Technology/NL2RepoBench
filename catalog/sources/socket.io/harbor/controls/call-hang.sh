#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"socket.io","version":"4.8.3","type":"commonjs","main":"index.js","exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"socket.io","version":"4.8.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"socket.io","version":"4.8.3"}}}
JSON
cat > index.js <<'JS'
class Server { constructor() { while (true) {} } }
class Namespace {}
class Socket {}
module.exports = { Server, Namespace, Socket };
JS
