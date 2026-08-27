#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

printf '%s  %s\n' \
  '27a205e827436e03acc87f91d6b1d57e209bf14267c48ed443813ff734113437' \
  "$script_dir/source.tar" | sha256sum --check --strict
printf '%s  %s\n' \
  '58c8063ff052b8443e501d42530c23ec4321a9fac44843bf3d6c38dbdae4229d' \
  "$script_dir/html5lib-tests.tar" | sha256sum --check --strict
printf '%s  %s\n' \
  'e2d2c0a0c64d73b13a179dc448bf15443730d051b7f487a2fb954d588a9f1a63' \
  "$script_dir/html5lib-tests-fork.tar" | sha256sum --check --strict
printf '%s  %s\n' \
  '0e877e3bfb4d4736fffed2743a44a0fc0c97e11ccbfc4f8ca7d5f68ace08fefa' \
  "$script_dir/package.tar" | sha256sum --check --strict

rm -rf /workspace/*
tar -xf "$script_dir/package.tar" -C /workspace

node --input-type=module <<'EOF'
import {readFileSync} from 'node:fs';

const manifest = JSON.parse(readFileSync('/workspace/package.json', 'utf8'));
if (manifest.name !== 'parse5' || manifest.version !== '8.0.1') process.exit(1);
if (manifest.dependencies?.entities !== '8.0.0') process.exit(1);
EOF
