#!/usr/bin/env bash
set -euo pipefail
readonly ARCHIVE_SHA256="b2181bf19230ddc0a7d61cb62b58538fce5aa9ecf2fa4f2419d58043ceb29840"
readonly ARCHIVE="/solution/remeda-2.0.0.tgz"
readonly SOURCE_SHA256="85f61d4b725ba3d0bf1f1c7081040d06632ec3e12800427bef7a4403f1acd383"
readonly SOURCE="/solution/source.tar"
readonly LOCK_SHA256="a083a03beb486b171b5974cb4c49aa9d107a1aa9c1c40f5ab0a5407d4e288a33"
readonly LOCK="/solution/package-lock.json"
readonly ROOT="/workspace"
printf '%s  %s\n' "$ARCHIVE_SHA256" "$ARCHIVE" | sha256sum --check --strict
printf '%s  %s\n' "$SOURCE_SHA256" "$SOURCE" | sha256sum --check --strict
printf '%s  %s\n' "$LOCK_SHA256" "$LOCK" | sha256sum --check --strict
rm -rf "$ROOT"/*
mkdir -p "$ROOT"
tar -xzf "$ARCHIVE" -C "$ROOT"
mv "$ROOT/package"/* "$ROOT"/
rm -rf "$ROOT/package"
cp "$LOCK" "$ROOT/package-lock.json"
node -e "const fs=require('node:fs'); const path='$ROOT/package.json'; const value=JSON.parse(fs.readFileSync(path,'utf8')); delete value.devDependencies; delete value.scripts; delete value.workspaces; fs.writeFileSync(path, JSON.stringify(value, null, 2) + '\n')"
echo 'restored frozen remeda package'
