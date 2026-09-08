#!/bin/bash
# install-failure control - invalid package that fails to install
set -euo pipefail

mkdir -p /workspace/deepdiff
cat > /workspace/deepdiff/__init__.py << 'INIT_EOF'
print("Module content")
INIT_EOF

cat > /workspace/pyproject.toml << 'INVALID_EOF'
[project
name = "deepdiff"
# Invalid TOML - missing closing bracket
INVALID_EOF

cd /workspace
python3 -m pip install --no-build-isolation --no-deps --no-index -e . 2>&1 || true
echo "Install failure simulated"
