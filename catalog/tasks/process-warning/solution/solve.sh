#!/usr/bin/env bash
set -euo pipefail

revision='d55637b341e21fef9dc7222590b36b14d030a839'
archive_sha256='6ea9bf54d357fb67d7024510e082e37b59fea0516c32f3e0fdabc897fa9344a4'
temporary="$(mktemp -d)"
trap 'rm -rf "$temporary"' EXIT

git init "$temporary/source"
git -C "$temporary/source" remote add origin https://github.com/fastify/process-warning
git -C "$temporary/source" fetch --depth=1 origin "$revision"
git -C "$temporary/source" checkout --detach FETCH_HEAD
test "$(git -C "$temporary/source" rev-parse HEAD)" = "$revision"
git -C "$temporary/source" archive --format=tar HEAD > "$temporary/source.tar"
echo "$archive_sha256  $temporary/source.tar" | sha256sum --check --status
mkdir "$temporary/archive"
tar -xf "$temporary/source.tar" -C "$temporary/archive"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
install -m 0644 "$temporary/archive/index.js" /workspace/index.js
install -d -m 0755 /workspace/types
install -m 0644 "$temporary/archive/types/index.d.ts" /workspace/types/index.d.ts
install -m 0644 "$temporary/archive/LICENSE" /workspace/LICENSE
cat > /workspace/package.json <<'JSON'
{
  "name": "process-warning",
  "version": "5.1.0",
  "type": "commonjs",
  "main": "index.js",
  "types": "types/index.d.ts",
  "license": "MIT"
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "process-warning",
  "version": "5.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "process-warning",
      "version": "5.1.0",
      "license": "MIT"
    }
  }
}
JSON
