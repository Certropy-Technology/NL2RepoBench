#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/requests_cache
printf '%s\n' 'from setuptools import setup' 'setup(name="requests-cache",version="1.3.4")' > /workspace/setup.py
printf '%s\n' 'class CachedSession:' '    def get(self, *args, **kwargs):' '        while True: pass' > /workspace/requests_cache/__init__.py
