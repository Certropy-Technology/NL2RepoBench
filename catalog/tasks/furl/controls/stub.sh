#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/furl
printf '%s\n' 'from .furl import furl' '__all__ = ["furl"]' > /workspace/furl/__init__.py
printf '%s\n' 'class furl:' '    def __init__(self, url=""):' '        self.url = url' > /workspace/furl/furl.py
printf '%s\n' 'class omdict1D(dict): pass' > /workspace/furl/omdict1D.py
printf '%s\n' 'from collections import OrderedDict' 'string_types = (str, bytes)' > /workspace/furl/compat.py
printf '%s\n' 'from setuptools import setup' 'setup(name="furl", version="0.0.0", packages=["furl"])' > /workspace/setup.py
