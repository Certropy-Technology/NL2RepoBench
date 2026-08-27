#!/usr/bin/env bash
set -euo pipefail
root=/workspace
rm -rf "$root"/* "$root"/.[!.]* "$root"/..?*
mkdir -p "$root"
