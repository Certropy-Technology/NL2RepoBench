#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/dateutil
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "python-dateutil"
version = "2.9.0"
[tool.setuptools]
package-dir = {"" = "src"}
[tool.setuptools.packages.find]
where = ["src"]
EOF
cat > /workspace/src/dateutil/__init__.py <<'EOF'
__all__ = ["easter", "parser", "relativedelta", "rrule", "tz", "utils", "zoneinfo"]
EOF
cat > /workspace/src/dateutil/parser.py <<'EOF'
class ParserError(ValueError): pass
def parse(*args, **kwargs): raise ParserError("stub")
def isoparse(*args, **kwargs): raise ParserError("stub")
class parser: pass
EOF
cat > /workspace/src/dateutil/relativedelta.py <<'EOF'
class relativedelta:
    def __init__(self, *args, **kwargs): pass
MO = TU = WE = TH = FR = SA = SU = object()
EOF
cat > /workspace/src/dateutil/easter.py <<'EOF'
def easter(*args, **kwargs): raise ValueError("stub")
EOF
cat > /workspace/src/dateutil/rrule.py <<'EOF'
DAILY = WEEKLY = MONTHLY = 0
class rrule: pass
class rruleset: pass
def rrulestr(*args, **kwargs): raise ValueError("stub")
EOF
cat > /workspace/src/dateutil/tz.py <<'EOF'
def gettz(*args, **kwargs): return None
def tzoffset(*args, **kwargs): return None
def datetime_ambiguous(*args, **kwargs): return False
def datetime_exists(*args, **kwargs): return False
EOF
