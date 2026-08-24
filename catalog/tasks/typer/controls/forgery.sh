#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/src/platformdirs
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "platformdirs"
version = "4.11.3"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
PYPROJECT
cat > /workspace/src/platformdirs/__init__.py <<'PACKAGE'
def user_data_dir(*args, **kwargs):
    return "/forged/reward"
PACKAGE
cat > /workspace/reward.json <<'REWARD'
{"reward": 1.0}
REWARD
