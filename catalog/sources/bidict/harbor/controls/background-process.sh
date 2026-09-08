#!/bin/bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
cd "$WORKSPACE"

cat > bidict.py << 'BGPROCPY'
"""Background process control."""
import subprocess
import sys

# Start background process
subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"], 
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class ValueDuplicationError(ValueError):
    pass

class bidict(dict):
    @property
    def inverse(self):
        return bidict({v: k for k, v in self.items()})
BGPROCPY

echo "Background process bidict created"
