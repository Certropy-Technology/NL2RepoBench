#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/aiohappyeyeballs
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="aiohappyeyeballs", version="2.7.1", packages=["aiohappyeyeballs"])
PY
cat > /workspace/aiohappyeyeballs/__init__.py <<'PY'
__version__ = "2.7.1"
def addr_to_addr_infos(addr): return None
def pop_addr_infos_interleave(addr_infos, interleave=None): return None
def remove_addr_infos(addr_infos, addr): return None
async def start_connection(*args, **kwargs): return None
AddrInfoType = tuple
SocketFactoryType = object
__all__ = ("AddrInfoType", "SocketFactoryType", "addr_to_addr_infos", "pop_addr_infos_interleave", "remove_addr_infos", "start_connection")
PY
touch /workspace/aiohappyeyeballs/py.typed
