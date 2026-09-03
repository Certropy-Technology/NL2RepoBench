#!/usr/bin/env bash
set -euo pipefail

readonly REPOSITORY="https://github.com/minimistjs/minimist.git"
readonly REVISION="ecfdaea23e7931c0d529c52b743c711c3278a8ce"
readonly SOURCE_DIGEST="sha256:880c54feb7058c36a6600d35d58a17d834d403b4460cb9c62c33cb455c8adc3c"

rm -rf /tmp/minimist-source /tmp/minimist-archive
git init --quiet /tmp/minimist-source
git -C /tmp/minimist-source remote add origin "$REPOSITORY"
git -C /tmp/minimist-source fetch --quiet --depth=1 origin "$REVISION"
git -C /tmp/minimist-source checkout --quiet --detach FETCH_HEAD
test "$(git -C /tmp/minimist-source rev-parse HEAD)" = "$REVISION"

git -C /tmp/minimist-source archive --format=tar HEAD > /tmp/minimist-archive
actual_digest="sha256:$(sha256sum /tmp/minimist-archive | awk '{print $1}')"
test "$actual_digest" = "$SOURCE_DIGEST"
license_digest="sha256:$(sha256sum /tmp/minimist-source/LICENSE | awk '{print $1}')"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf /tmp/minimist-archive -C /workspace
version="$(node -p "require('/workspace/package.json').version")"
node - <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));
delete pkg.scripts;
delete pkg.devDependencies;
delete pkg.publishConfig;
pkg.private = false;
fs.writeFileSync(path, `${JSON.stringify(pkg, null, 2)}\n`);
NODE
printf '{"name":"minimist","version":"%s","lockfileVersion":3,"requires":true,"packages":{"":{"name":"minimist","version":"%s"}}}\n' "$version" "$version" > /workspace/package-lock.json
printf '{"revision":"%s","source_digest":"%s","license_digest":"%s","package_version":"%s"}\n' "$REVISION" "$actual_digest" "$license_digest" "$version" > /workspace/.oracle-source-freeze.json
