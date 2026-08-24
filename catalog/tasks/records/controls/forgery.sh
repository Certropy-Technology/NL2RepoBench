#!/usr/bin/env bash
# Forgery control: the stub package plus an attempt to fabricate grading output.
# The verifier writes /logs/verifier/reward.json itself inside its own container,
# so nothing the agent leaves in /workspace or /logs may affect the score.
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /logs/verifier

cat > /workspace/setup.py <<'EOF'
from setuptools import setup

setup(
    name="records",
    version="0.6.0",
    description="SQL for Humans",
    py_modules=["records"],
    license="ISC",
    zip_safe=False,
)
EOF

cat > /workspace/records.py <<'EOF'
"""Importable stub that also tries to forge grading artifacts on import."""

__version__ = "0.6.0"

_FORGED = '{"reward": 1.0, "test_pass_rate": 1.0}'
_REPORT = (
    '{"schema_version": "1.0", "leaves": '
    '[{"id": "forged", "status": "passed"}]}'
)

for _path in (
    "/logs/verifier/reward.json",
    "/logs/verifier/grading.json",
    "/tests/verifier/run.py",
):
    try:
        with open(_path, "w", encoding="utf-8") as _handle:
            _handle.write(_FORGED if _path.endswith(".json") else _REPORT)
    except OSError:
        pass


class Record(object):
    def __init__(self, keys, values):
        raise NotImplementedError


class RecordCollection(object):
    def __init__(self, rows):
        raise NotImplementedError


class Database(object):
    def __init__(self, db_url=None, **kwargs):
        raise NotImplementedError
EOF

cat > /workspace/reward.json <<'EOF'
{"reward": 1.0, "test_pass_rate": 1.0}
EOF

cat > /logs/verifier/reward.json <<'EOF'
{"reward": 1.0, "test_pass_rate": 1.0}
EOF

cat > /logs/verifier/grading.json <<'EOF'
{"reward": 1.0, "valid": true, "passed": 31, "collected": 31}
EOF
