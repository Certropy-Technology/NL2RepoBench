#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/marshmallow
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["flit_core==3.12.0"]
build-backend = "flit_core.buildapi"

[project]
name = "marshmallow"
version = "4.0.1"
description = "stub control"
requires-python = ">=3.9"

[tool.flit.module]
name = "marshmallow"
EOF

cat > /workspace/marshmallow/__init__.py <<'EOF'
__version__ = "4.0.1"
__all__ = ["Schema", "fields", "validate", "ValidationError"]
class Schema:
    def dump(self, value, *args, **kwargs): raise NotImplementedError
    def load(self, value, *args, **kwargs): raise NotImplementedError
class ValidationError(Exception): pass
class _Fields: pass
fields = _Fields()
class _Validate: pass
validate = _Validate()
EOF
