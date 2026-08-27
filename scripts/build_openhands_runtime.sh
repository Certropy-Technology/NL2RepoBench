#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="nl2repobench/openhands-sdk-fork:930e9b1da"
BOOKWORM_IMAGE="nl2repobench/openhands-sdk-fork:930e9b1da-bookworm"
BOOKWORM_BASE="python@sha256:0f5b26b9518d002b6173fd61daad821fa340635ebfec5bba471013f9ca114579"
CONTEXT="$ROOT/vendor/openhands-software-agent-sdk"
LOG_DIR="$ROOT/.nl2repo/runtime/logs"
LOG_FILE="$LOG_DIR/openhands-fork-runtime-build.log"

mkdir -p "$LOG_DIR"
build_and_verify() {
  local image="$1"
  local expected_id="$2"
  shift 2
  docker build \
    --pull=false \
    --provenance=false \
    --sbom=false \
    --file "$ROOT/runtime/openhands-agent/Dockerfile" \
    --tag "$image" \
    "$@" \
    "$CONTEXT"
  docker run --rm --network none "$image" \
    /opt/openhands-sdk-venv/bin/python -c \
    'from importlib.metadata import version; from openhands.sdk.agent.utils import parse_tool_call_arguments; assert version("openhands-sdk")=="1.43.1"; assert version("openhands-tools")=="1.43.1"; assert version("litellm")=="1.93.0"; assert parse_tool_call_arguments("{}{\"command\":\"pwd\"}")=={"command":"pwd"}; print("OPENHANDS_FORK_OFFLINE_RUNTIME_OK")'
  actual_id="$(docker image inspect "$image" --format '{{.Id}}')"
  test "$actual_id" = "$expected_id"
  docker image inspect "$image" \
    --format '{{json .RepoDigests}} {{.Id}} {{index .Config.Labels "org.nl2repobench.openhands-fork-commit"}} {{index .Config.Labels "org.nl2repobench.litellm-version"}}'
  docker image inspect "$image" \
    --format '{{json .RepoDigests}}' | grep -Fq "@${expected_id}"
}

{
  build_and_verify "$IMAGE" "sha256:70525a5fbee81f4d202b7f7de14857fe78f961ce2ec3995efd1a4850e45c7ea5"
  build_and_verify "$BOOKWORM_IMAGE" "sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f" --build-arg "PYTHON_BASE=$BOOKWORM_BASE"
} 2>&1 | tee "$LOG_FILE"
