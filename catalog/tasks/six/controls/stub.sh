#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="six", version="1.17.0", py_modules=["six"])
PY
cat > /workspace/six.py <<'PY'
import sys

__version__ = "1.17.0"
PY2 = False
PY3 = True
PY34 = True
string_types = (str,)
integer_types = (int,)
class_types = (type,)
text_type = str
binary_type = bytes
MAXSIZE = sys.maxsize
__path__ = []
PY
