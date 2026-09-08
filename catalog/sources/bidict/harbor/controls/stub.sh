#!/bin/bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
cd "$WORKSPACE"

cat > bidict.py << 'STUBPY'
"""Stub bidict implementation."""

class ValueDuplicationError(ValueError):
    """Raised when a duplicate value is encountered."""
    pass

class _BidictInverse:
    def __init__(self, parent):
        raise NotImplementedError("stub inverse")
    
    def __getitem__(self, key):
        raise NotImplementedError("stub inverse __getitem__")
    
    def __contains__(self, key):
        raise NotImplementedError("stub inverse __contains__")
    
    def keys(self):
        raise NotImplementedError("stub inverse keys")
    
    def values(self):
        raise NotImplementedError("stub inverse values")
    
    def items(self):
        raise NotImplementedError("stub inverse items")
    
    def get(self, key, default=None):
        raise NotImplementedError("stub inverse get")
    
    def __len__(self):
        raise NotImplementedError("stub inverse __len__")
    
    def __setitem__(self, key, value):
        raise NotImplementedError("stub inverse __setitem__")

class bidict(dict):
    """Stub bidict class."""
    
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("stub __init__")
    
    @property
    def inverse(self):
        raise NotImplementedError("stub inverse property")
    
    def __setitem__(self, key, value):
        raise NotImplementedError("stub __setitem__")
    
    def setdefault(self, key, default=None):
        raise NotImplementedError("stub setdefault")
    
    def update(self, *args, **kwargs):
        raise NotImplementedError("stub update")
    
    def copy(self):
        raise NotImplementedError("stub copy")
STUBPY

echo "Stub bidict created"
