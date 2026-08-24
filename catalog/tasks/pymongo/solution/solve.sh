#!/usr/bin/env bash
set -euo pipefail
tar -xzf "$(dirname "$0")/pymongo-source.tar.gz" -C /workspace --strip-components=1
