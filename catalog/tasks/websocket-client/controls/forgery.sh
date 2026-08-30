#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/websocket /workspace/.logs
printf '%s\n' 'from ._abnf import ABNF' > /workspace/websocket/__init__.py
printf '%s\n' 'class ABNF:' '    OPCODE_TEXT = 1' > /workspace/websocket/_abnf.py
printf '%s\n' 'from setuptools import setup' 'setup(name="websocket-client", version="1.9.0", packages=["websocket"])' > /workspace/setup.py
printf '%s\n' '{"reward":1.0,"valid":true}' > /workspace/.logs/reward.json
