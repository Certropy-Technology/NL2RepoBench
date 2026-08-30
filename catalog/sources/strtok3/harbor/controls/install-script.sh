#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/package.json <<'JSON'
{"name":"strtok3","version":"10.3.5","type":"module","main":"index.js","scripts":{"preinstall":"node -e process.exit(0)"},"dependencies":{"@tokenizer/token":"0.3.0"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"strtok3","version":"10.3.5","lockfileVersion":3,"requires":true,"packages":{"":{"name":"strtok3","version":"10.3.5","hasInstallScript":true,"dependencies":{"@tokenizer/token":"0.3.0"}},"node_modules/@tokenizer/token":{"version":"0.3.0","resolved":"https://registry.npmjs.org/@tokenizer/token/-/token-0.3.0.tgz","integrity":"sha512-OvjF+z51L3ov0OyAU0duzsYuvO01PH7x4t6DJx+guahgTnBHkhJdG7soQeTSFLWN3efnHyibZ4Z8l2EuWwJN3A=="}}}
JSON
printf '%s\n' 'export default {};' > /workspace/index.js
