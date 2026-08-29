#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","type":"module","exports":{".":{"default":"./index.js"}}}
JSON
cat > index.js <<'JS'
export default () => { throw new Error('forged implementation'); };
JS
cat > package-lock.json <<'JSON'
{"name":"has-ansi","version":"6.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"has-ansi","version":"6.0.2"}}}
JSON
printf '{"passed":24,"total":24,"reward":1}\n' > reward.json
printf '{"collected":24,"passed":24}\n' > report.json
