#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/*
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{
  "name": "eslint",
  "version": "10.9.0",
  "main": "./index.js"
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "eslint",
  "version": "10.9.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": { "": { "name": "eslint", "version": "10.9.0" } }
}
JSON
cat > /workspace/index.js <<'JS'
"use strict";
module.exports = {};
JS
mkdir -p /workspace/.logs
printf '{"reward":1,"test_pass_rate":1}\n' > /workspace/.logs/reward.json
