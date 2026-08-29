#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/shellingham
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
[project]
name = "shellingham"
version = "1.5.4"
EOF
cat > /workspace/shellingham/__init__.py <<'EOF'
__version__ = "1.5.4"
def detect_shell(pid=None, max_depth=10):
    return ("bash", "/bin/bash")
class ShellDetectionFailure(EnvironmentError):
    pass
EOF
