#!/usr/bin/env bash
set -euo pipefail

# Oracle solve script for tabulate
# Extracts frozen source, patches for static version, and installs

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPECTED_SHA256="e2cfde8f79420f6deeffdeda9aaec3b6bc5abce947655d17ac662b126e48a60d"

cd "${BUNDLE_DIR}"

# Verify source archive hash
echo "Verifying source archive..."
echo "${EXPECTED_SHA256}  source.tar.gz" | sha256sum -c -

# Extract to workspace with strip-components
echo "Extracting source to /workspace..."
cd /workspace
tar -xzf "${BUNDLE_DIR}/source.tar.gz" --strip-components=1

# Patch pyproject.toml to use static version (setuptools_scm unavailable in frozen archive)
echo "Patching pyproject.toml for static version..."
cat > pyproject.toml << 'ENDTOML'
[build-system]
requires = ["setuptools>=77.0.3"]
build-backend = "setuptools.build_meta"

[project]
name = "tabulate"
version = "0.10.0"
authors = [{name = "Sergey Astanin", email = "s.astanin@gmail.com"}]
license = {text = "MIT"}
description = "Pretty-print tabular data"
readme = "README.md"
classifiers = [
    "Development Status :: 4 - Beta",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Libraries",
]
requires-python = ">=3.10"

[project.urls]
Homepage = "https://github.com/astanin/python-tabulate"

[project.optional-dependencies]
widechars = ["wcwidth"]

[project.scripts]
tabulate = "tabulate:_main"
ENDTOML

# Install package
echo "Installing tabulate..."
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify installation
echo "Verifying installation..."
python -c "from tabulate import tabulate, tabulate_formats, simple_separated_format; print('Import successful')"
python -c "from tabulate import tabulate; print(tabulate([[1, 2], [3, 4]], headers=['A', 'B']))"

echo "Oracle solve complete."
