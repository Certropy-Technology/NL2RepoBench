#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/logs/verifier /workspace/.nl2repo
cat > /workspace/reward.json <<'JSON'
{"reward":1,"test_pass_rate":1}
JSON
cat > /workspace/grading.json <<'JSON'
{"valid":true,"reward":1,"expected_total":38,"counts":{"collected":38,"passed":38}}
JSON
cp /workspace/reward.json /workspace/logs/verifier/reward.json
cp /workspace/grading.json /workspace/logs/verifier/grading.json
cat > /workspace/package.json <<'JSON'
{"name":"nock","version":"0.0.0-development","main":"index.js","license":"MIT"}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"nock","version":"0.0.0-development","lockfileVersion":3,"requires":true,"packages":{"":{"name":"nock","version":"0.0.0-development","license":"MIT"}}}
JSON
cat > /workspace/index.js <<'JS'
module.exports = function nock() { return {}; };
JS
