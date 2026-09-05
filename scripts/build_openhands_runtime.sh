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
  actual_id="$(docker image inspect "$image" --format '{{.Id}}')"
  docker image inspect "$image" \
    --format '{{json .RepoDigests}} {{.Id}} {{index .Config.Labels "org.nl2repobench.openhands-fork-commit"}} {{index .Config.Labels "org.nl2repobench.litellm-version"}}'
  python3 - "$ROOT" "$image" "$actual_id" "$runtime_metadata" <<'PY'
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

root = Path(sys.argv[1])
image = sys.argv[2]
image_id = sys.argv[3]
metadata = Path(sys.argv[4])
receipt = root / ".nl2repo/runtime" / f"{metadata.stem}-build.json"
receipt.parent.mkdir(parents=True, exist_ok=True)
payload = {
    "schema_version": "1.0",
    "built_at": datetime.now(UTC).isoformat(),
    "image": image,
    "image_id": image_id,
    "dockerfile_sha256": "sha256:" + hashlib.sha256(
        (root / "runtime/openhands-agent/Dockerfile").read_bytes()
    ).hexdigest(),
    "source_commit": "930e9b1daee0f5d2c7f3b261f045527a0ddae87d",
    "offline_probe": True,
    "registry_required": False,
}
receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
print(json.dumps(payload, sort_keys=True))
PY
}

{
  build_and_verify "$IMAGE" "$ROOT/runtime/openhands-agent/runtime.json"
  build_and_verify "$BOOKWORM_IMAGE" "$ROOT/runtime/openhands-agent/runtime.bookworm.json" --build-arg "PYTHON_BASE=$BOOKWORM_BASE"
} 2>&1 | tee "$LOG_FILE"
