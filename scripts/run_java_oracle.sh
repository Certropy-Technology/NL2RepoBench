#!/usr/bin/env bash
# Run one Java Oracle with a role-scoped private CAS and explicit source host.
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_ROOT/.." && pwd)"

: "${JAVA_TASK:?set JAVA_TASK to a compiled Java Harbor task}"
: "${JAVA_ORACLE_HOST:?set JAVA_ORACLE_HOST to the exact Oracle source hostname}"
: "${JAVA_RUN_ROOT:?set JAVA_RUN_ROOT to a new run directory}"

ARTIFACT_ROOT="${JAVA_ARTIFACT_ROOT:-$REPO_ROOT/.nl2repo/artifacts}"
TOOLCHAIN="${JAVA_TOOLCHAIN:-$REPO_ROOT/toolchain.java.lock.toml}"
if [[ "$JAVA_TASK" == *$'\n'* || "$JAVA_TASK" == *$'\r'* ]]; then
  echo "JAVA_TASK contains a newline" >&2
  exit 2
fi
if [[ -e "$JAVA_RUN_ROOT" ]]; then
  echo "JAVA_RUN_ROOT already exists: $JAVA_RUN_ROOT" >&2
  exit 2
fi

prepared_root="$JAVA_RUN_ROOT/prepared"
mkdir -p "$JAVA_RUN_ROOT"
prepared_json="$JAVA_RUN_ROOT/prepare.json"
PYTHONPATH="$REPO_ROOT/src" uv run nl2repo harbor prepare-run \
  "$JAVA_TASK" oracle \
  --output "$prepared_root" \
  --private-cas-output "$JAVA_RUN_ROOT/private-cas" \
  --toolchain "$TOOLCHAIN" \
  --artifact-root "$ARTIFACT_ROOT" \
  >"$prepared_json"
prepared_task="$(python3 - "$prepared_json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle)["output"])
PY
)"

cd "$REPO_ROOT"
env PYTHONPATH=src:. uv run --frozen --project harbor-runner harbor run \
  -p "$prepared_task" \
  -e nl2repobench.harbor_docker:StdinSecretDockerEnvironment \
  -a nl2repobench.harbor_java_oracle:JavaOracleAgent \
  --ae "NL2REPO_TASK_DIR=$prepared_task" \
  --ae "NL2REPO_ORACLE_CAS=$ARTIFACT_ROOT" \
  --allow-agent-host "$JAVA_ORACLE_HOST" \
  --jobs-dir "$JAVA_RUN_ROOT/harbor" \
  --yes
