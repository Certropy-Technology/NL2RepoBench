#!/usr/bin/env bash
set -euo pipefail
readonly CONTROL_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$CONTROL_ROOT/stub.sh"
cat > /workspace/tzdata/__init__.py <<'PY'
import time
time.sleep(300)
PY
