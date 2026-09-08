#!/bin/bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
cd "$WORKSPACE"

# Create a setup.py that will fail installation
cat > setup.py << 'FAILPY'
raise RuntimeError("Intentional installation failure for testing")
FAILPY

echo "Install failure setup created"
