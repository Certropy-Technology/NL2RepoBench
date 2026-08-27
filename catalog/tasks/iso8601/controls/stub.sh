#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace
mkdir -p /workspace/iso8601
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "iso8601"
version = "2.1.0"
description = "stub control"
authors = []
packages = [{ include = "iso8601" }]
TOML
cat > /workspace/iso8601/__init__.py <<'PY'
import datetime

def parse_date(value, default_timezone=None):
    raise ParseError("stub")
def is_iso8601(value):
    return False
class ParseError(ValueError):
    pass
UTC = datetime.timezone.utc
def FixedOffset(offset_hours, offset_minutes, name):
    return datetime.timezone(datetime.timedelta(hours=offset_hours, minutes=offset_minutes), name)
PY
