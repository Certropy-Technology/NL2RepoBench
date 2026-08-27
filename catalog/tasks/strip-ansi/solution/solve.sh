#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_archive="$script_dir/source.tar"
source_archive_sha256=fd02f8851dfbe8b499d8847da63563d587d070a7324e61b3a2243d577eab07f3

printf '%s  %s\n' "$source_archive_sha256" "$source_archive" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$source_archive" -C /workspace

# Freeze the otherwise ranged runtime dependency to the task's offline closure.
node -e '
const fs = require("node:fs");
const path = "/workspace/package.json";
const value = JSON.parse(fs.readFileSync(path, "utf8"));
value.dependencies = {"ansi-regex": "6.3.0"};
delete value.devDependencies;
delete value.scripts;
fs.writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
'
cat > /workspace/package-lock.json <<'EOF'
{
  "name": "strip-ansi",
  "version": "7.2.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "strip-ansi",
      "version": "7.2.0",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "6.3.0"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/ansi-regex": {
      "version": "6.3.0",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-6.3.0.tgz",
      "integrity": "sha512-WpDfL7NO6j7tH88IDBNVdUJxDh9nmCteAVW9dsep846XdwF4naCBK+/tGLX3KJgcpgMRXCFlTM2hKGoK9FsdrQ==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      }
    }
  }
}
EOF
rm -f /workspace/.npmrc
