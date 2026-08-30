#!/usr/bin/env bash
set -euo pipefail

readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec "$BUNDLE_ROOT/write_stub.sh"
