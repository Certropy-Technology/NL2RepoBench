#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/pytz
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pytz"
version = "2026.3.post1"
requires-python = ">=3.10"

[tool.setuptools]
packages = ["pytz"]
EOF

cat > /workspace/pytz/__init__.py <<'EOF'
__version__ = "2026.3.post1"
OLSON_VERSION = "2026c"
all_timezones = []
all_timezones_set = set()
class UnknownTimeZoneError(Exception): pass
class AmbiguousTimeError(Exception): pass
class NonExistentTimeError(Exception): pass
def timezone(name):
    raise UnknownTimeZoneError(name)
EOF
