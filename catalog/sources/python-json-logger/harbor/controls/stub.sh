#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/pythonjsonlogger
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "python-json-logger"
version = "4.2.0"
[tool.setuptools]
packages = ["pythonjsonlogger"]
EOF
cat > /workspace/pythonjsonlogger/__init__.py <<'EOF'
ORJSON_AVAILABLE = False
MSGSPEC_AVAILABLE = False
from . import core, defaults, exception, json, utils
EOF
cat > /workspace/pythonjsonlogger/core.py <<'EOF'
import logging
RESERVED_ATTRS = sorted(vars(logging.LogRecord("x", 1, "", 1, "", (), None, "")))
def merge_record_extra(record, target, reserved, rename_fields=None):
    return target
class BaseJsonFormatter(logging.Formatter):
    def jsonify_log_record(self, log_data): raise NotImplementedError()
EOF
cat > /workspace/pythonjsonlogger/json.py <<'EOF'
import json as _json
from .core import BaseJsonFormatter
class JsonFormatter(BaseJsonFormatter):
    def format(self, record): return _json.dumps({"message": ""})
EOF
cat > /workspace/pythonjsonlogger/defaults.py <<'EOF'
def unknown_default(obj): return str(obj)
EOF
cat > /workspace/pythonjsonlogger/exception.py <<'EOF'
class MissingPackageError(ImportError):
    def __init__(self, msg): self.msg = msg; super().__init__(msg)
EOF
cat > /workspace/pythonjsonlogger/utils.py <<'EOF'
def package_is_available(name, throw_error=False, extras_name=None):
    if throw_error: raise __import__('pythonjsonlogger.exception', fromlist=['MissingPackageError']).MissingPackageError(name)
    return name == 'json'
EOF
