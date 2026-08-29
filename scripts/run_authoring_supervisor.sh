#!/usr/bin/env bash
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_ROOT/.." && pwd)"
export TMPDIR="${TMPDIR:-$REPO_ROOT/.nl2repo/authoring-live/tmp}"
mkdir -p "$TMPDIR"

if [[ -z "${PYTHON_BIN:-}" && -x "$REPO_ROOT/.venv/bin/python3" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
fi
if [[ -n "${PYTHON_BIN:-}" ]]; then
  exec "$PYTHON_BIN" "$SCRIPT_ROOT/authoring_supervisor.py" \
    --repository-root "$REPO_ROOT" "$@"
fi
exec uv run python "$SCRIPT_ROOT/authoring_supervisor.py" \
  --repository-root "$REPO_ROOT" "$@"
