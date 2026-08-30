#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/sse_starlette
printf '%s\n' 'from .event import ServerSentEvent, JSONServerSentEvent' > /workspace/sse_starlette/__init__.py
printf '%s\n' '__version__ = "3.4.8"' >> /workspace/sse_starlette/__init__.py
printf '%s\n' 'class ServerSentEvent: pass' > /workspace/sse_starlette/event.py
printf '%s\n' 'class JSONServerSentEvent: pass' >> /workspace/sse_starlette/event.py
printf '%s\n' 'class EventSourceResponse: pass' > /workspace/sse_starlette/sse.py
touch /workspace/sse_starlette/py.typed
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="sse-starlette", version="3.4.8", packages=["sse_starlette"])
PY
