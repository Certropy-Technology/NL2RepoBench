#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/sympy_slice
cat > /workspace/setup.py <<'PY'
from setuptools import find_packages, setup

setup(name="sympy-bounded", version="0.1.0", package_dir={"": "src"}, packages=find_packages("src"))
PY
cat > /workspace/src/sympy_slice/__init__.py <<'PY'
def _stub(*args, **kwargs):
    raise NotImplementedError("stub control")

parse_expression = _stub
expand_expression = _stub
factor_expression = _stub
simplify_expression = _stub
solve_expression = _stub
differentiate_expression = _stub
integrate_expression = _stub
limit_expression = _stub
matrix_determinant = _stub
PY
