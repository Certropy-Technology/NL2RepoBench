#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

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
authors = [{ name = "Background", email = "background@example.com" }]
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

# Create __init__.py that spawns background processes on import
cat > dateparser/__init__.py << 'INIT'
"""Background-process implementation that spawns background processes."""

__version__ = "1.4.3"

import subprocess
import sys

# Spawn 5 background processes that sleep
for i in range(5):
    subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(3600)'])

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

echo "[control:background-process] Package that spawns background processes created"
