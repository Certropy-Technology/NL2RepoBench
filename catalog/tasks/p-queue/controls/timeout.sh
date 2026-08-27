#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/dist
cat > /workspace/package.json <<'JSON'
{"name":"p-queue","version":"9.3.3","type":"module","exports":{"types":"./dist/index.d.ts","default":"./dist/index.js"},"types":"./dist/index.d.ts","files":["dist"],"dependencies":{"eventemitter3":"5.0.4","p-timeout":"7.0.1"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"p-queue","version":"9.3.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"p-queue","version":"9.3.3","dependencies":{"eventemitter3":"5.0.4","p-timeout":"7.0.1"}},"node_modules/eventemitter3":{"version":"5.0.4","resolved":"https://registry.npmjs.org/eventemitter3/-/eventemitter3-5.0.4.tgz","integrity":"sha512-mlsTRyGaPBjPedk6Bvw+aqbsXDtoAyAzm5MO7JgU+yVRyMQ5O8bD4Kcci7BS85f93veegeCPkL8R4GLClnjLFw=="},"node_modules/p-timeout":{"version":"7.0.1","resolved":"https://registry.npmjs.org/p-timeout/-/p-timeout-7.0.1.tgz","integrity":"sha512-AxTM2wDGORHGEkPCt8yqxOTMgpfbEHqF51f/5fJCmwFC3C/zNcGT63SymH2ttOAaiIws2zVg4+izQCjrakcwHg=="}}}
JSON
cat > /workspace/dist/index.js <<'JS'
export default class PQueue {
  constructor() { while (true) {} }
}
export class PriorityQueue {}
export class TimeoutError extends Error {}
JS
cat > /workspace/dist/index.d.ts <<'TS'
export default class PQueue {}
export class PriorityQueue {}
export class TimeoutError extends Error {}
TS
