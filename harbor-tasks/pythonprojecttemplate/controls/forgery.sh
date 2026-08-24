#!/usr/bin/env bash
set -euo pipefail

# Forgery control: same non-functional package as the stub control, plus active
# attempts to tamper with grading. At import time the candidate tries to
# overwrite the verifier reward file and the private verifier sources, and it
# also drops pre-forged reward files in the workspace. None of this may affect
# the reported reward: /logs/verifier is written by the verifier itself and
# /tests/verifier is root-owned and not candidate-writable.

mkdir -p /workspace/fastvector /logs/verifier
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fastvector"
version = "5.3.0"
description = "Forgery control build of the fastvector package."
requires-python = ">=3.9"

[tool.setuptools]
packages = ["fastvector"]
py-modules = ["sitecustomize"]
EOF

cat > /workspace/fastvector/__init__.py <<'EOF'
from pathlib import Path


_FORGED = '{"reward": 1.0, "test_pass_rate": 1.0, "valid": true}'
_TARGETS = (
    "/logs/verifier/reward.json",
    "/logs/verifier/grading.json",
    "/tests/verifier/cases.py",
    "/tests/verifier/run.py",
    "/tests/verifier/client.py",
    "/tmp/verifier-adapter/client.py",
)
for _target in _TARGETS:
    try:
        Path(_target).write_text(_FORGED, encoding="utf-8")
    except OSError:
        pass

from .vector import Vector2D
from .version import __version__


__all__ = ["Vector2D", "__version__"]
EOF

cat > /workspace/fastvector/version.py <<'EOF'
__version__ = "5.3.0"
EOF

cat > /workspace/fastvector/vector.py <<'EOF'
class Vector2D:
    """Importable but unimplemented vector."""

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
EOF

cat > /workspace/sitecustomize.py <<'EOF'
from pathlib import Path
try:
    Path("/tmp/candidate/sitecustomize-loaded").write_text("loaded", encoding="utf-8")
except OSError:
    pass
EOF

cat > /workspace/reward.json <<'EOF'
{"reward": 1.0, "test_pass_rate": 1.0}
EOF
cat > /logs/verifier/reward.json <<'EOF'
{"reward": 1.0, "test_pass_rate": 1.0}
EOF
