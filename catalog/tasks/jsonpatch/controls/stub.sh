#!/bin/bash
set -euo pipefail

# Stub control - minimal installable package with empty implementations
# Expected: collects frozen_total tests, very low reward (<=0.20)

echo "=== Stub Control ==="

# Create minimal package structure
cat > /workspace/jsonpatch.py << 'PYEOF'
# -*- coding: utf-8 -*-
"""Stub implementation of jsonpatch"""

__author__ = 'Stub <stub@example.com>'
__version__ = '1.33'
__website__ = 'https://example.com'
__license__ = 'BSD'


class JsonPatchException(Exception):
    """Base Json Patch exception"""
    pass


class InvalidJsonPatch(JsonPatchException):
    """Raised if an invalid JSON Patch is created"""
    pass


class JsonPatchConflict(JsonPatchException):
    """Raised if patch could not be applied"""
    pass


class JsonPatchTestFailed(JsonPatchException, AssertionError):
    """A Test operation failed"""
    pass


def apply_patch(doc, patch, in_place=False, pointer_cls=None):
    """Stub apply_patch - always returns empty dict"""
    return 


def make_patch(src, dst, pointer_cls=None):
    """Stub make_patch - returns empty JsonPatch"""
    return JsonPatch([])


class JsonPatch(object):
    """Stub JsonPatch class"""
    
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

# Create setup.py
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

# Create bin directory and stub scripts
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

# Create minimal files
touch /workspace/README.md
touch /workspace/LICENSE
touch /workspace/requirements.txt

echo "Stub package created with empty implementations"
echo "Expected: tests collect but fail (reward <= 0.20)"

ls -la /workspace/
exit 0
