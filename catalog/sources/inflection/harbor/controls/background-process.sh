#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Create package that spawns background processes on import
mkdir -p inflection

cat > inflection/__init__.py << 'EOFPYTHON'
"""Background process control - spawns processes on import"""
import subprocess
import sys

# Spawn 5 background sleep processes
for i in range(5):
    subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(300)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

__version__ = '0.5.1'


def camelize(string: str, uppercase_first_letter: bool = True) -> str:
    return string


def underscore(word: str) -> str:
    return word


def dasherize(word: str) -> str:
    return word


def humanize(word: str) -> str:
    return word


def titleize(word: str) -> str:
    return word


def pluralize(word: str) -> str:
    return word


def singularize(word: str) -> str:
    return word


def ordinal(number: int) -> str:
    return "th"


def ordinalize(number: int) -> str:
    return f"{number}th"


def parameterize(string: str, separator: str = '-') -> str:
    return string


def transliterate(string: str) -> str:
    return string


def tableize(word: str) -> str:
    return word
EOFPYTHON

cat > inflection/py.typed << 'EOFTYPED'
EOFTYPED

cat > setup.py << 'EOFSETUP'
from setuptools import setup

setup(
    name='inflection',
    version='0.5.1',
    packages=['inflection'],
    package_data={'inflection': ['py.typed']},
    zip_safe=False,
    python_requires='>=3.5',
)
EOFSETUP

cat > LICENSE << 'EOFLICENSE'
MIT License
EOFLICENSE

python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Background-process control installed"
