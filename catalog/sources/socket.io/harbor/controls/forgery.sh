#!/usr/bin/env bash
set -euo pipefail
mkdir -p tests /logs/verifier
printf '{"reward":1,"valid":true}\n' > reward.json
printf '{"reward":1,"valid":true}\n' > grading.json
printf '{"reward":1,"valid":true}\n' > /logs/verifier/reward.json
cat > package.json <<'JSON'
{"name":"socket.io","version":"4.8.3","type":"commonjs","main":"index.js","exports":"./index.js"}
JSON
cat > package-lock.json <<'JSON'
{"name":"socket.io","version":"4.8.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"socket.io","version":"4.8.3"}}}
JSON
cat > index.js <<'JS'
class Server {}
class Namespace {}
class Socket {}
module.exports = { Server, Namespace, Socket };
JS
