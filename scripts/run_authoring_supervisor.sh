#!/usr/bin/env bash
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_ROOT/.." && pwd)"
export TMPDIR="${TMPDIR:-$REPO_ROOT/.nl2repo/authoring-live/tmp}"
mkdir -p "$TMPDIR"

DB_MODE=0
for ((index = 1; index <= $#; index++)); do
  if [[ "${!index}" == "--scheduler-db" ]]; then
    DB_MODE=1
    next=$((index + 1))
    if (( next > $# )) || [[ "${!next}" != /* ]]; then
      echo "--scheduler-db requires an absolute path" >&2
      exit 64
    fi
  fi
done
export NL2REPO_AUTHORING_AUTHORITY=$([[ "$DB_MODE" == 1 ]] && printf sqlite || printf legacy-json)

if [[ -z "${PYTHON_BIN:-}" && -x "$REPO_ROOT/.venv/bin/python3" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
fi
if [[ -n "${PYTHON_BIN:-}" ]]; then
  exec "$PYTHON_BIN" "$SCRIPT_ROOT/authoring_supervisor.py" \
    --repository-root "$REPO_ROOT" "$@"
fi
exec uv run python "$SCRIPT_ROOT/authoring_supervisor.py" \
  --repository-root "$REPO_ROOT" "$@"
