#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xf "$SCRIPT_DIR/source.tar" -C /workspace
# Koa's upstream development package has a prepare hook used only to generate
# an optional ESM wrapper. The scored CommonJS entrypoint does not need it, and
# the candidate contract forbids lifecycle execution, so the trusted Oracle
# removes that build-only hook before producing its workspace.
node -e 'const fs=require("fs"); const p=JSON.parse(fs.readFileSync("/workspace/package.json")); if (p.scripts) delete p.scripts.prepare; fs.writeFileSync("/workspace/package.json", JSON.stringify(p,null,2)+"\n")'

# All source bytes and npm package bytes come from private, content-addressed
# Oracle materials. The model Agent never receives this bundle.
if [[ -d "$SCRIPT_DIR/npm-cache" ]]; then
  ORACLE_ROOT=/tmp/koa-install
  rm -rf "$ORACLE_ROOT"
  mkdir -p "$ORACLE_ROOT"
  cp /workspace/package.json /workspace/package-lock.json "$ORACLE_ROOT/"
  npm ci --prefix "$ORACLE_ROOT" --offline --ignore-scripts --no-audit --no-fund --cache="$SCRIPT_DIR/npm-cache"
  rm -rf /workspace/node_modules
else
  echo 'Oracle npm cache is missing' >&2
  exit 71
fi
