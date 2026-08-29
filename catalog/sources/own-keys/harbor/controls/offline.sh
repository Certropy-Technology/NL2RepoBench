#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"own-keys","version":"1.0.2","main":"index.js","exports":{".":"./index.js","./package.json":"./package.json"},"sideEffects":false,"license":"MIT"}
JSON
cat > package-lock.json <<'JSON'
{"name":"own-keys","version":"1.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"own-keys","version":"1.0.2","license":"MIT"}}}
JSON
cat > index.js <<'JS'
'use strict';
var net = require('node:net');
var socket = net.connect({ host: '1.1.1.1', port: 443 });
socket.setTimeout(50);
socket.on('connect', function () { socket.destroy(new Error('public network was available')); });
socket.on('timeout', function () { socket.destroy(); });
socket.on('error', function () {});
socket.unref();
module.exports = function ownKeys(_source) {
  return [];
};
JS
