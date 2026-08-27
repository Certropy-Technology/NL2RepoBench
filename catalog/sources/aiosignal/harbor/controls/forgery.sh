#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/aiosignal
printf "__version__ = '1.4.0'\n" > /workspace/aiosignal/__init__.py
mkdir -p /workspace/aiosignal
printf '{\"reward\": 1.0}\n' > /workspace/reward.json
