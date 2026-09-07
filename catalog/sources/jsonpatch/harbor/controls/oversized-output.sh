#!/bin/bash
set -euo pipefail

# Oversized output control - generates excessive output
# Expected: output truncation/handling, potential timeout

echo "=== Oversized Output Control ==="
echo "Generating minimal package plus excessive output..."

# Create minimal working package first
cat > /workspace/jsonpatch.py << 'PYEOF'
class JsonPatchException(Exception):
    pass

class InvalidJsonPatch(JsonPatchException):
    pass

class JsonPatchConflict(JsonPatchException):
    pass

class JsonPatchTestFailed(JsonPatchException):
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
from setuptools import setup
setup(name='jsonpatch', version='1.33', py_modules=['jsonpatch'])
SETUPEOF

# Generate oversized output to stdout
echo "Generating excessive output to test output limits..."
for i in {1..10000}; do
    echo "Line $i: This is oversized output to test Harbor's handling of excessive stdout/stderr..."
done

echo "Package created with oversized output"
exit 0
