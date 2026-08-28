#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
mkdir -p /workspace/email_validator
cat > /workspace/setup.py <<'EOF'
from setuptools import setup
setup(name="email-validator", version="2.3.0", packages=["email_validator"])
EOF
cat > /workspace/email_validator/__init__.py <<'EOF'
__version__ = "2.3.0"
__all__ = []
def validate_email(*args, **kwargs):
    raise NotImplementedError("stub")
EOF
