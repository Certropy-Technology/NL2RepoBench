#!/bin/bash
set -e

mkdir -p /workspace/faker

cat > /workspace/faker/__init__.py << 'PYEOF'
# Valid Python module
PYEOF

# Invalid TOML in setup.py will cause installation failure
cat > /workspace/setup.py << 'PYEOF'
from setuptools import setup

setup(
    name="Faker"
    version="40.38.0",  # Missing comma - syntax error
    packages=["faker"],
)
PYEOF

exit 0
