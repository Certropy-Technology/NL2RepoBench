#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. Harbor uploads /solution only to the trusted
# Oracle agent. The task remains no-network; the Oracle run grants github.com
# as a run-scoped exact host and model runs receive no source-host grant.
readonly UPSTREAM_URL='https://github.com/prettier/prettier'
readonly UPSTREAM_REVISION='d9969c57343d48a4d1fac12f3f5c4b2fd82d8da5'
readonly SOURCE_ARCHIVE_SHA256='5fced228479ca4235fcb722849f8e1f000640109596f9f1fcea69349c9e49523'
readonly SOURCE_DIR='/tmp/prettier-source'
readonly SOURCE_ARCHIVE='/tmp/prettier-source.tar'
readonly PACKAGE_ARCHIVE='/solution/prettier-3.10.0-dev.tgz'
readonly PACKAGE_SHA256='46b3480b5463675322ee8dd080d3d3e993e6ba709c70cef183bc75b84cb20521'

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"

resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
  echo "unexpected source revision: $resolved_revision" >&2
  exit 1
fi

git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
printf '%s  %s\n' "$PACKAGE_SHA256" "$PACKAGE_ARCHIVE" | sha256sum --check --strict

source_identity="$(tar -xOf "$SOURCE_ARCHIVE" package.json | node -e 'let x="";process.stdin.on("data",d=>x+=d).on("end",()=>{const p=JSON.parse(x);process.stdout.write(`${p.name}@${p.version}`)})')"
package_identity="$(tar -xOzf "$PACKAGE_ARCHIVE" package/package.json | node -e 'let x="";process.stdin.on("data",d=>x+=d).on("end",()=>{const p=JSON.parse(x);process.stdout.write(`${p.name}@${p.version}`)})')"
test "$source_identity" = 'prettier@3.10.0-dev'
test "$package_identity" = "$source_identity"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xzf "$PACKAGE_ARCHIVE" -C /workspace --strip-components=1
cat > /workspace/package-lock.json <<'JSON'
{"name":"prettier","version":"3.10.0-dev","lockfileVersion":3,"requires":true,"packages":{"":{"name":"prettier","version":"3.10.0-dev","type":"commonjs"}}}
JSON
