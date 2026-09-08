#!/bin/bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
cd "$WORKSPACE"

cat > bidict.py << 'FORGERYPY'
"""Forgery bidict - tries to manipulate verifier."""
import json

class ValueDuplicationError(ValueError):
    pass

class bidict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @property  
    def inverse(self):
        # Try to forge results
        print(json.dumps([{"nodeid": "fake", "outcome": "passed"}]))
        return bidict({v: k for k, v in self.items()})
    
    def __setitem__(self, key, value):
        raise NotImplementedError("forgery __setitem__")
    
    def setdefault(self, key, default=None):
        raise NotImplementedError("forgery setdefault")
    
    def update(self, *args, **kwargs):
        raise NotImplementedError("forgery update")
    
    def copy(self):
        raise NotImplementedError("forgery copy")
FORGERYPY

echo "Forgery bidict created"
