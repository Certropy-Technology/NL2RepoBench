#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${JAVA_RUNTIME_IMAGE:-nl2repobench/java-runtime:21.0.12-maven3.9.11-local}"
RECEIPT="${JAVA_RUNTIME_RECEIPT:-$ROOT/.nl2repo/runtime/java-runtime-build.json}"

docker build \
  --pull=false \
  --provenance=false \
  --sbom=false \
  --file "$ROOT/runtime/java-maven/Dockerfile" \
  --tag "$IMAGE" \
  "$ROOT/runtime/java-maven"

docker run --rm --network none "$IMAGE" sh -ceu '
  test "$(java -version 2>&1 | awk -F\" '\''/version/{print $2}'\'')" = "21.0.12"
  test "$(mvn -version 2>&1 | awk '\''/^Apache Maven/{print $3}'\'')" = "3.9.11"
'

mkdir -p "$(dirname "$RECEIPT")"
python3 - "$ROOT" "$IMAGE" "$RECEIPT" <<'PY'
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

root = Path(sys.argv[1])
image = sys.argv[2]
receipt = Path(sys.argv[3])

def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

image_id = subprocess.check_output(
    ["docker", "image", "inspect", image, "--format", "{{.Id}}"], text=True
).strip()
payload = {
    "schema_version": "1.0",
    "built_at": datetime.now(UTC).isoformat(),
    "image": image,
    "image_id": image_id,
    "dockerfile": "runtime/java-maven/Dockerfile",
    "dockerfile_sha256": sha256(root / "runtime/java-maven/Dockerfile"),
    "jdk_base": "docker.io/library/eclipse-temurin@sha256:a16bfc04b28f66c1d27218ffeefc8ae6a2621de423e01597156ba813ca5fa668",
    "maven_base": "docker.io/library/maven@sha256:463a1849665463254b2dd56e3a5b316f1596bc93d0571065c06ea05bb48ab8f4",
    "offline_probe": {"jdk": "21.0.12", "maven": "3.9.11", "passed": True},
    "registry_required": False,
}
receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
print(json.dumps(payload, sort_keys=True))
PY
