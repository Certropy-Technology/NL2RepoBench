#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Create minimal stub package structure
mkdir -p inflection

cat > inflection/__init__.py << 'EOFPYTHON'
"""Stub inflection package - functions raise NotImplementedError"""

__version__ = '0.5.1'


def camelize(string: str, uppercase_first_letter: bool = True) -> str:
    raise NotImplementedError("camelize not implemented")


def underscore(word: str) -> str:
    raise NotImplementedError("underscore not implemented")


def dasherize(word: str) -> str:
    raise NotImplementedError("dasherize not implemented")


def humanize(word: str) -> str:
    raise NotImplementedError("humanize not implemented")


def titleize(word: str) -> str:
    raise NotImplementedError("titleize not implemented")


def pluralize(word: str) -> str:
    raise NotImplementedError("pluralize not implemented")


def singularize(word: str) -> str:
    raise NotImplementedError("singularize not implemented")


def ordinal(number: int) -> str:
    raise NotImplementedError("ordinal not implemented")


def ordinalize(number: int) -> str:
    raise NotImplementedError("ordinalize not implemented")


def parameterize(string: str, separator: str = '-') -> str:
    raise NotImplementedError("parameterize not implemented")


def transliterate(string: str) -> str:
    raise NotImplementedError("transliterate not implemented")


def tableize(word: str) -> str:
    raise NotImplementedError("tableize not implemented")
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

Copyright (c) 2020 Stub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOFLICENSE

python -m pip install --no-build-isolation --no-deps --no-index -e .

python -c "import inflection; assert hasattr(inflection, 'pluralize')"

echo "Stub control installed"
