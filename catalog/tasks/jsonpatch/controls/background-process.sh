#!/bin/bash
set -euo pipefail

# Background process control - spawns lingering background processes
# Expected: proper cleanup of process group

echo "=== Background Process Control ==="
echo "Creating package with background processes..."

# Create minimal package
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

# Spawn background processes that won't terminate on their own
echo "Spawning background processes to test cleanup..."
(sleep 3600 &)
(sleep 7200 &)

echo "Background processes spawned"
echo "Expected: Harbor properly cleans up process group"
exit 0
