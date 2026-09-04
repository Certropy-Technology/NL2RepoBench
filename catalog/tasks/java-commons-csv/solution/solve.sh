#!/usr/bin/env bash
set -euo pipefail
bundle_dir="$(CDPATH= cd -- "$(dirname -- "$0")/oracle-bundle" && pwd)"
if [ ! -x "$bundle_dir/solve.sh" ]; then
  echo "oracle bundle is not materialized; run nl2repo harbor prepare-run" >&2
  exit 125
fi
exec "$bundle_dir/solve.sh" "$@"
