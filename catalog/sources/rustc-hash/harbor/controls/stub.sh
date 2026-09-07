#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/src
printf '[package]\nname="rustc-hash"\nversion="0.0.0"\nedition="2021"\n[lib]\npath="src/lib.rs"\n' > /workspace/Cargo.toml
printf 'pub struct Stub;\n' > /workspace/src/lib.rs
