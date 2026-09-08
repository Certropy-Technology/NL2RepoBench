#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct structure but non-functional code"

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
authors = [{ name = "Stub", email = "stub@example.com" }]
license = "BSD-3-Clause"
requires-python = ">=3.10"
dependencies = [
    "python-dateutil>=2.7.0",
    "pytz>=2024.2",
    "regex>=2024.9.11",
    "tzlocal>=0.2",
]

[project.scripts]
dateparser-download = "dateparser_cli.cli:entrance"
PYPROJECT

# Create README
cat > README.md << 'README'
# dateparser stub

This is a stub implementation.
README

# Create main package directory
mkdir -p dateparser

# Create __init__.py with stub implementations
cat > dateparser/__init__.py << 'INIT'
"""Stub implementation of dateparser."""

__version__ = "1.4.3"

def parse(
    date_string,
    date_formats=None,
    languages=None,
    locales=None,
    region=None,
    settings=None,
    detect_languages_function=None,
):
    raise NotImplementedError("Stub implementation")

class DateDataParser:
    def __init__(
        self,
        languages=None,
        locales=None,
        region=None,
        settings=None,
        detect_languages_function=None,
    ):
        raise NotImplementedError("Stub implementation")
    
    def get_date_data(self, date_string, date_formats=None):
        raise NotImplementedError("Stub implementation")
INIT

# Create conf.py
cat > dateparser/conf.py << 'CONF'
"""Stub conf module."""

class SettingValidationError(ValueError):
    pass

class Settings:
    _default = True
    
    def __init__(self, settings=None):
        raise NotImplementedError("Stub implementation")

def apply_settings(f):
    raise NotImplementedError("Stub implementation")
CONF

# Create date.py
cat > dateparser/date.py << 'DATE'
"""Stub date module."""

class DateDataParser:
    def __init__(
        self,
        languages=None,
        locales=None,
        region=None,
        settings=None,
        detect_languages_function=None,
    ):
        raise NotImplementedError("Stub implementation")
    
    def get_date_data(self, date_string, date_formats=None):
        raise NotImplementedError("Stub implementation")
DATE

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
