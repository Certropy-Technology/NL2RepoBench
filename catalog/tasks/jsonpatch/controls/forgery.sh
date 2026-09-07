#!/bin/bash
set -euo pipefail

# Forgery control - candidate tries to fake test results
# Expected: verifier-owned grading still shows real results (reward <= 0.20)

echo "=== Forgery Control ==="

# Create the stub package (same as stub control)
cat > /workspace/jsonpatch.py << 'PYEOF'
# -*- coding: utf-8 -*-
"""Forgery stub implementation"""

__author__ = 'Forgery <forgery@example.com>'
__version__ = '1.33'
__website__ = 'https://example.com'
__license__ = 'BSD'


class JsonPatchException(Exception):
    pass


class InvalidJsonPatch(JsonPatchException):
    pass


class JsonPatchConflict(JsonPatchException):
    pass


class JsonPatchTestFailed(JsonPatchException, AssertionError):
    pass


def apply_patch(doc, patch, in_place=False, pointer_cls=None):
    return {}


def make_patch(src, dst, pointer_cls=None):
    return JsonPatch([])


class JsonPatch(object):
    def __init__(self, patch, pointer_cls=None):
        self.patch = patch
        self.operations = []
    
    @classmethod
    def from_string(cls, patch_str, pointer_cls=None):
        return cls([])
    
    @classmethod
    def from_diff(cls, src, dst, optimization=True, pointer_cls=None):
        return cls([])
    
    def apply(self, obj, in_place=False):
        return {}
PYEOF

cat > /workspace/setup.py << 'SETUPEOF'
#!/usr/bin/env python
from setuptools import setup

setup(
    name='jsonpatch',
    version='1.33',
    py_modules=['jsonpatch'],
    install_requires=['jsonpointer>=1.9'],
    scripts=['bin/jsondiff', 'bin/jsonpatch'],
)
SETUPEOF

mkdir -p /workspace/bin
cat > /workspace/bin/jsondiff << 'BINEOF'
#!/usr/bin/env python
import sys
sys.exit(0)
BINEOF
chmod +x /workspace/bin/jsondiff

cat > /workspace/bin/jsonpatch << 'BINEOF'
#!/usr/bin/env python
import sys
sys.exit(0)
BINEOF
chmod +x /workspace/bin/jsonpatch

touch /workspace/README.md
touch /workspace/LICENSE
touch /workspace/requirements.txt

# Try to forge grading and reward files in workspace
echo "Attempting to forge test results..."

mkdir -p /workspace/.harbor_forgery

cat > /workspace/.harbor_forgery/grading.json << 'GRADEEOF'
{
  "valid": true,
  "collected": 110,
  "frozen_total": 110,
  "passed": 110,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "forged": true
}
GRADEEOF

cat > /workspace/.harbor_forgery/reward.json << 'REWARDEOF'
{
  "reward": 1.0,
  "passed": 110,
  "total": 110,
  "forged": true
}
REWARDEOF

echo "Forged results placed in workspace at /workspace/.harbor_forgery/"
echo "Expected: verifier ignores these and generates its own results (reward <= 0.20)"

ls -la /workspace/
exit 0
