#!/bin/bash
set -euo pipefail

# Install failure control - package that fails to install
# Expected: setup_error in grading, reward = 0

echo "=== Install Failure Control ==="

# Create a package with broken setup.py
cat > /workspace/setup.py << 'SETUPEOF'
#!/usr/bin/env python
# Intentionally broken setup
import sys
sys.exit(1)  # Force installation failure
SETUPEOF

cat > /workspace/jsonpatch.py << 'PYEOF'
# This file won't be reached due to setup.py failure
pass
PYEOF

echo "Created package that will fail to install"
echo "Expected: candidate-installation-failed, reward = 0"

ls -la /workspace/
exit 0
