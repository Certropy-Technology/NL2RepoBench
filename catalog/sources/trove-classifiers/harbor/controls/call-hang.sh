#!/usr/bin/env bash
set -euo pipefail

readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$BUNDLE_ROOT/write_stub.sh"
cat > /workspace/src/trove_classifiers/__init__.py <<'PY'
import time
time.sleep(300)

sorted_classifiers = []
classifiers = set()
deprecated_classifiers = {}
all_classifiers = []
__all__ = ["all_classifiers", "classifiers", "deprecated_classifiers", "sorted_classifiers"]
PY
