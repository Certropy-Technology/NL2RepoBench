#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/aiohappyeyeballs
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="aiohappyeyeballs", version="2.7.1", packages=["aiohappyeyeballs"])
PY
cat > /workspace/aiohappyeyeballs/__init__.py <<'PY'
import time
__version__ = "2.7.1"
def addr_to_addr_infos(addr): time.sleep(600)
def pop_addr_infos_interleave(addr_infos, interleave=None): time.sleep(600)
def remove_addr_infos(addr_infos, addr): time.sleep(600)
async def start_connection(*args, **kwargs):
    time.sleep(600)
AddrInfoType = tuple
SocketFactoryType = object
__all__ = ("AddrInfoType", "SocketFactoryType", "addr_to_addr_infos", "pop_addr_infos_interleave", "remove_addr_infos", "start_connection")
PY
touch /workspace/aiohappyeyeballs/py.typed
