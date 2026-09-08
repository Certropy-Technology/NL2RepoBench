#!/bin/bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
cd "$WORKSPACE"

cat > bidict.py << 'OVERSIZEDPY'
"""Oversized output control."""

class ValueDuplicationError(ValueError):
    pass

class bidict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Print massive output
        for i in range(100000):
            print(f"OVERSIZED_OUTPUT_LINE_{i}_" + "X" * 100)
    
    @property
    def inverse(self):
        return bidict({v: k for k, v in self.items()})
OVERSIZEDPY

echo "Oversized output bidict created"
