#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package that floods output"

cd /workspace

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
build-backend = "setuptools.build_meta"
requires = ["setuptools >= 77.0"]

[project]
name = "dateparser"
version = "1.4.3"
description = "Date parsing library designed to parse dates from HTML pages"
authors = [{ name = "Oversized", email = "oversized@example.com" }]
license = "BSD-3-Clause"
requires-python = ">=3.10"
dependencies = [
    "python-dateutil>=2.7.0",
    "pytz>=2024.2",
    "regex>=2024.9.11",
    "tzlocal>=0.2",
]
PYPROJECT

# Create package directory
mkdir -p dateparser

# Create __init__.py that floods stderr on import
cat > dateparser/__init__.py << 'INIT'
"""Oversized-output implementation that floods stderr."""

__version__ = "1.4.3"

import sys

# Flood stderr with large output
for i in range(100000):
    sys.stderr.write(f"Oversized output line {i}: " + "x" * 1000 + "\n")
    sys.stderr.flush()

from datetime import datetime

def parse(
    date_string,
    date_formats=None,
    languages=None,
    locales=None,
    region=None,
    settings=None,
    detect_languages_function=None,
):
    return None

class DateDataParser:
    def __init__(
        self,
        languages=None,
        locales=None,
        region=None,
        settings=None,
        detect_languages_function=None,
    ):
        pass
    
    def get_date_data(self, date_string, date_formats=None):
        return None
INIT

echo "[control:oversized-output] Package that floods stderr created"
