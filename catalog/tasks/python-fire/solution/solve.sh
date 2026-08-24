#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xf /solution/source.tar -C /workspace
