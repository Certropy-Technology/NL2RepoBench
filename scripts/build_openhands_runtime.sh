#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="nl2repobench/openhands-sdk-fork:930e9b1da"
BOOKWORM_IMAGE="nl2repobench/openhands-sdk-fork:930e9b1da-bookworm"
BOOKWORM_BASE="python@sha256:0f5b26b9518d002b6173fd61daad821fa340635ebfec5bba471013f9ca114579"
CONTEXT="$ROOT/openhands"
LOG_DIR="$ROOT/.nl2repo/runtime/logs"
LOG_FILE="$LOG_DIR/openhands-fork-runtime-build.log"

mkdir -p "$LOG_DIR"
build_and_verify() {
  local image="$1"
  local runtime_metadata="$2"
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
  local expected_id
  expected_id="$(python3 - "$runtime_metadata" <<'PY'
import json
import sys
from pathlib import Path

print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["image_id"])
PY
)"
  actual_id="$(docker image inspect "$image" --format '{{.Id}}')"
  test "$actual_id" = "$expected_id"
  docker image inspect "$image" \
    --format '{{json .RepoDigests}} {{.Id}} {{index .Config.Labels "org.nl2repobench.openhands-fork-commit"}} {{index .Config.Labels "org.nl2repobench.litellm-version"}}'
  docker image inspect "$image" \
    --format '{{json .RepoDigests}}' | grep -Fq "@${expected_id}"
}

{
  build_and_verify "$IMAGE" "$ROOT/runtime/openhands-agent/runtime.json"
  build_and_verify "$BOOKWORM_IMAGE" "$ROOT/runtime/openhands-agent/runtime.bookworm.json" --build-arg "PYTHON_BASE=$BOOKWORM_BASE"
} 2>&1 | tee "$LOG_FILE"
