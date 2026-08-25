#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="nl2repobench/openhands-sdk-fork:930e9b1da"
CONTEXT="$ROOT/vendor/openhands-software-agent-sdk"
LOG_DIR="$ROOT/.nl2repo/runtime/logs"
LOG_FILE="$LOG_DIR/openhands-fork-runtime-build.log"

mkdir -p "$LOG_DIR"
docker build \
  --file "$ROOT/runtime/openhands-agent/Dockerfile" \
  --tag "$IMAGE" \
  "$CONTEXT" \
  2>&1 | tee "$LOG_FILE"
docker run --rm --network none "$IMAGE" \
  /opt/openhands-sdk-venv/bin/python -c \
  'from importlib.metadata import version; from openhands.sdk.agent.utils import parse_tool_call_arguments; assert version("openhands-sdk")=="1.43.1"; assert version("openhands-tools")=="1.43.1"; assert version("litellm")=="1.93.0"; assert parse_tool_call_arguments("{}{\"command\":\"pwd\"}")=={"command":"pwd"}; print("OPENHANDS_FORK_OFFLINE_RUNTIME_OK")'
docker image inspect "$IMAGE" --format '{{json .RepoDigests}} {{.Id}}'
