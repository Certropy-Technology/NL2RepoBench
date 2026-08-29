#!/usr/bin/env bash
set -euo pipefail

"$(dirname "$0")/stub.sh"

node -e '
const fs = require("node:fs");
const packagePath = "/workspace/package.json";
const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf8"));
packageJson.files.push("evil-loader.mjs", "node-options.txt");
fs.writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);
'
cat > /workspace/evil-loader.mjs <<'JS'
throw new Error('untrusted loader executed');
JS
printf 'NODE_OPTIONS=--loader=./evil-loader.mjs\n' > /workspace/node-options.txt
