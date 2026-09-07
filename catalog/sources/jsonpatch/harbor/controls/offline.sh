#!/bin/bash
set -euo pipefail

# Offline control - attempts network access (should fail under no-network policy)
# Expected: network access blocked, package creation may fail or succeed without network

echo "=== Offline Control ==="
echo "Testing network isolation by attempting external access..."

# Try to access network (should fail)
echo "Attempting to ping google.com..."
if ping -c 1 google.com 2>/dev/null; then
    echo "WARNING: Network access succeeded (should be blocked!)"
else
    echo "✓ Network access blocked as expected"
fi

echo "Attempting to curl example.com..."
if curl -s --max-time 5 http://example.com 2>/dev/null; then
    echo "WARNING: HTTP access succeeded (should be blocked!)"
else
    echo "✓ HTTP access blocked as expected"
fi

# Create minimal package (should succeed even without network)
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

echo "Minimal package created offline"
echo "Expected: network blocked, package creation succeeds"
exit 0
