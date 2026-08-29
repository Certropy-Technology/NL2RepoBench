#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace
printf '%s\n' 'from setuptools import setup' 'setup(name="regex", version="0.0.0")' > /workspace/setup.py
while :; do :; done
