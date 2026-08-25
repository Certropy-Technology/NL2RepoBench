#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/dotenv
printf '%s\n' \
  'from setuptools import setup' \
  'setup(name="python-dotenv", version="1.1.1", packages=["dotenv"])' \
  > /workspace/setup.py
printf '%s\n' \
  'def dotenv_values(*args, **kwargs): return {}' \
  'def load_dotenv(*args, **kwargs): return False' \
  'def find_dotenv(*args, **kwargs): return ""' \
  'def get_key(*args, **kwargs): return None' \
  'def set_key(*args, **kwargs): return (None, "", "")' \
  'def unset_key(*args, **kwargs): return (None, "")' \
  'def get_cli_string(*args, **kwargs): return "dotenv"' \
  > /workspace/dotenv/__init__.py
printf '%s\n' 'raise SystemExit(1)' > /workspace/dotenv/__main__.py
