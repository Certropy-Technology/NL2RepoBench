# Project Description

isort is a Python utility and library designed to automatically sort and organize Python import statements. It alphabetically orders imports, separates them into logical sections (standard library, third-party, local), and can format them according to various style guides. The tool is widely used in Python projects to maintain consistent import organization and improve code readability.

The primary goals are:
- Sort imports alphabetically within each section
- Automatically separate imports into sections (future, stdlib, third-party, first-party, local)
- Support various import formatting styles (single-line, multi-line, hanging indent, etc.)
- Provide both CLI and programmatic API
- Check import order without modifying files
- Find and analyze imports in Python code

This project excludes:
- Runtime code execution or modification beyond import sorting
- Network operations or external service dependencies
- Interactive GUI components
- File system operations outside the defined workspace

# Natural Language Instruction

Build a Python package named `isort` that provides utilities for sorting and organizing Python import statements. The package must be installable via pip and provide both a command-line interface and a programmatic Python API.

Key capabilities that must be implemented:

1. **Import Sorting**: Parse Python source code, identify import statements, and reorder them alphabetically within logical sections
2. **Section Management**: Automatically categorize imports into sections (future imports, standard library, third-party packages, first-party modules, local imports)
3. **Multiple Output Formats**: Support various import formatting styles including single-line, multi-line with parentheses, hanging indents, and vertical hanging indents
4. **File Operations**: Sort imports in files or code strings, with options to check without modification
5. **Configuration System**: Support extensive configuration options via Config class, config files, and command-line arguments
6. **Import Analysis**: Find and extract import information from Python code
7. **Module Placement**: Determine the appropriate section for a given module name
8. **CLI Interface**: Provide `isort` and `isort-identify-imports` command-line tools

The package must:
- Be named `isort` for installation (PyPI package name)
- Use `isort` as the import name in Python code
- Provide entry points for `isort` and `isort-identify-imports` CLI commands
- Include a Config class for configuration management
- Support Python 3.10+ (runtime requirement: `>=3.10.0`)
- Depend on `mypy-extensions>=1.1.0` as the only runtime dependency
- Use hatchling as the build backend with hatch-vcs for version management

All components (agent workspace, candidate code, verifier) must operate without network access during execution.

# Environment Configuration

- **Language**: Python 3.12
- **Package Manager**: pip
- **Build Backend**: hatchling (with hatch-vcs, hatch-mypyc)
- **Installation Command**: `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- **Runtime Dependencies**: 
  - mypy-extensions>=1.1.0 (required)
- **Build Dependencies**:
  - hatchling (build backend)
  - hatch-vcs (version management from VCS)
  - hatch-mypyc (optional compilation hook, disabled by default)
- **Python Version Requirement**: `>=3.10.0`
- **Operating System**: Debian 12 (amd64)
- **Base Image**: python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

**Network Policy**: No network access during agent execution, candidate installation, or verification. All dependencies must be preinstalled in the Docker image from a hash-locked requirements file during the build phase.

**Version Management**: The project uses hatch-vcs for dynamic version detection from VCS. Since the source archive does not contain .git metadata, the version must be statically configured in pyproject.toml as `version = "9.0.1"` (removing `dynamic = ["version"]` and `[tool.hatch.version]` sections).

# Project Directory Structure

```
workspace/
├── pyproject.toml          # Package metadata and build configuration
├── isort/                  # Main package directory
│   ├── __init__.py        # Package initialization and public API exports
│   ├── __main__.py        # Module entry point for `python -m isort`
│   ├── _version.py        # Version information
│   ├── api.py             # Core API functions (sort, check, find imports)
│   ├── comments.py        # Comment handling utilities
│   ├── core.py            # Core sorting logic
│   ├── exceptions.py      # Custom exception classes
│   ├── files.py           # File operations and discovery
│   ├── format.py          # Output formatting utilities
│   ├── hooks.py           # Git hooks integration
│   ├── identify.py        # Import identification and parsing
│   ├── io.py              # I/O operations and File class
│   ├── literal.py         # Literal value handling
│   ├── logo.py            # ASCII art logo
│   ├── main.py            # CLI entry points
│   ├── output.py          # Import output formatting
│   ├── parse.py           # Import statement parsing
│   ├── place.py           # Module placement logic
│   ├── profiles.py        # Predefined configuration profiles
│   ├── sections.py        # Import section definitions
│   ├── settings.py        # Configuration and Config class
│   ├── sorting.py         # Sorting algorithms
│   ├── utils.py           # Utility functions
│   ├── wrap.py            # Import wrapping logic
│   ├── wrap_modes.py      # Wrap mode implementations
│   └── _vendored/         # Vendored dependencies (tomli parser)
│       └── tomli/
│           ├── __init__.py
│           ├── _parser.py
│           ├── _re.py
│           └── _types.py
└── LICENSE                # MIT License file
```

# API Usage Guide

## Core Module: `isort`

The `isort` package exports the following public API from `isort.__init__`:

### Public Exports

**Available via `from isort import ...` or `import isort; isort.<name>`:**

- `Config`: Configuration class
- `ImportKey`: Enum for import deduplication keys
- `__version__`: Package version string
- `check_code`: Check code string for correct import order
- `check_file`: Check file for correct import order
- `check_stream`: Check stream for correct import order
- `code`: Sort imports in code string (alias for sort_code_string)
- `file`: Sort imports in file (alias for sort_file)
- `stream`: Sort imports in stream (alias for sort_stream)
- `find_imports_in_code`: Find imports in code string
- `find_imports_in_file`: Find imports in file
- `find_imports_in_paths`: Find imports in multiple paths
- `find_imports_in_stream`: Find imports in stream
- `place_module`: Determine section for a module name
- `place_module_with_reason`: Determine section with reasoning
- `settings`: Settings module

## Function: `isort.code` (alias for `sort_code_string`)

```python
def code(
    code: str,
    extension: str | None = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Path | None = None,
    disregard_skip: bool = False,
    show_diff: bool | TextIO = False,
    **config_kwargs: Any,
) -> str
```

**Purpose**: Sorts any imports within the provided code string, returning a new string with them sorted.

**Parameters**:
- `code` (str): The string of code with imports that need to be sorted
- `extension` (str | None): The file extension. Defaults to filename extension or 'py'
- `config` (Config): The config object to use. Defaults to DEFAULT_CONFIG
- `file_path` (Path | None): The disk location where the code string was pulled from
- `disregard_skip` (bool): Set to True to ignore skip configuration for this file
- `show_diff` (bool | TextIO): If True, print diff to stdout; if TextIO, write to that stream
- `**config_kwargs`: Additional config modifications

**Returns**: str - The sorted code string

**Example**:
```python
import isort

unsorted = "import os\nimport sys\nimport numpy\n"
sorted_code = isort.code(unsorted)
# Returns imports sorted by section and alphabetically
```

## Function: `isort.check_code` (alias for `check_code_string`)

```python
def check_code(
    code: str,
    show_diff: bool | TextIO = False,
    extension: str | None = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Path | None = None,
    disregard_skip: bool = False,
    **config_kwargs: Any,
) -> bool
```

**Purpose**: Checks the order, format, and categorization of imports within the provided code string. Returns True if everything is correct, otherwise False.

**Parameters**: Same as `code()` but with `show_diff` first

**Returns**: bool - True if imports are correctly sorted, False otherwise

**Example**:
```python
import isort

code = "import sys\nimport os\n"
is_sorted = isort.check_code(code)  # Returns False (os should come before sys)
```

## Function: `isort.file` (alias for `sort_file`)

```python
def file(
    filename: str | Path,
    config: Config = DEFAULT_CONFIG,
    **config_kwargs: Any,
) -> bool
```

**Purpose**: Sorts imports in a file in-place. Returns True if the file was modified, False otherwise.

**Parameters**:
- `filename` (str | Path): Path to the file to sort
- `config` (Config): Configuration object
- `**config_kwargs`: Additional config modifications

**Returns**: bool - True if file was modified, False if already sorted

**Raises**:
- `FileSkipSetting`: If file is configured to be skipped
- `ExistingSyntaxErrors`: If file has syntax errors (when atomic=True)

## Function: `isort.check_file`

```python
def check_file(
    filename: str | Path,
    config: Config = DEFAULT_CONFIG,
    **config_kwargs: Any,
) -> bool
```

**Purpose**: Checks if imports in a file are correctly sorted without modifying the file.

**Parameters**: Same as `file()`

**Returns**: bool - True if correctly sorted, False otherwise

## Function: `isort.stream` (alias for `sort_stream`)

```python
def stream(
    input_stream: TextIO,
    output_stream: TextIO,
    extension: str | None = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Path | None = None,
    disregard_skip: bool = False,
    show_diff: bool | TextIO = False,
    raise_on_skip: bool = True,
    **config_kwargs: Any,
) -> bool
```

**Purpose**: Sorts any imports within the provided input stream, writing results to the output stream. Returns True if anything is modified, otherwise False.

**Parameters**:
- `input_stream` (TextIO): Stream with code containing imports
- `output_stream` (TextIO): Stream where sorted imports should be written
- Other parameters similar to `code()`

**Returns**: bool - True if modified, False otherwise

## Class: `isort.Config`

```python
class Config:
    def __init__(
        self,
        settings_file: str = "",
        settings_path: str | Path = "",
        config: Config | None = None,
        **config_overrides: Any
    )
```

**Purpose**: Configuration class for customizing isort behavior.

**Key Configuration Options** (subset of commonly used options):
- `line_length` (int): Maximum line length for imports. Default: 79
- `wrap_length` (int): Line length to wrap imports at. Default: 0 (use line_length)
- `sections` (list): Section order. Default: ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
- `known_third_party` (list): Modules known to be third-party
- `known_first_party` (list): Modules known to be first-party
- `skip` (list): Files or directories to skip
- `skip_gitignore` (bool): Skip files in .gitignore. Default: False
- `profile` (str): Predefined configuration profile (e.g., "black", "google", "django")
- `force_single_line` (bool): Force all imports to separate lines
- `multi_line_output` (int): Multi-line import formatting mode (0-11)
- `atomic` (bool): Check for syntax errors before applying changes
- `show_diff` (bool): Show diff when sorting
- `check` (bool): Check only, don't modify files

**Methods**:
- `is_skipped(file_path: Path) -> bool`: Check if file should be skipped

**Example**:
```python
from isort import Config, code

config = Config(line_length=100, profile="black")
sorted_code = code("import os\nimport sys", config=config)
```

## Enum: `isort.ImportKey`

```python
class ImportKey(Enum):
    PACKAGE = 1      # Top-level package: from x.y import z -> x
    MODULE = 2       # Module: from x.y import z -> y
    ATTRIBUTE = 3    # Attribute: from x.y import z -> z
    ALIAS = 4        # Alias: from x.y import z as a -> a
```

**Purpose**: Defines how to key an individual import for deduplication purposes.

## Function: `isort.find_imports_in_code`

```python
def find_imports_in_code(
    code: str,
    config: Config = DEFAULT_CONFIG,
    file_path: Path | None = None,
    **config_kwargs: Any,
) -> Iterator[dict]
```

**Purpose**: Yields dictionaries with information about each import found in the code string.

**Returns**: Iterator of dicts containing import information (module name, line numbers, type, etc.)

## Function: `isort.find_imports_in_file`

```python
def find_imports_in_file(
    filename: str | Path,
    config: Config = DEFAULT_CONFIG,
    **config_kwargs: Any,
) -> Iterator[dict]
```

**Purpose**: Yields import information for imports found in a file.

## Function: `isort.find_imports_in_paths`

```python
def find_imports_in_paths(
    paths: Iterable[str | Path],
    config: Config = DEFAULT_CONFIG,
    **config_kwargs: Any,
) -> Iterator[dict]
```

**Purpose**: Yields import information for imports found in multiple paths.

## Function: `isort.find_imports_in_stream`

```python
def find_imports_in_stream(
    input_stream: TextIO,
    config: Config = DEFAULT_CONFIG,
    file_path: Path | None = None,
    **config_kwargs: Any,
) -> Iterator[dict]
```

**Purpose**: Yields import information for imports found in a stream.

## Function: `isort.place_module`

```python
def place_module(
    module_name: str,
    config: Config = DEFAULT_CONFIG,
    **config_kwargs: Any,
) -> str
```

**Purpose**: Determines which import section a module belongs to.

**Parameters**:
- `module_name` (str): Name of the module to place

**Returns**: str - Section name (e.g., "FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER")

**Example**:
```python
import isort

section = isort.place_module("os")  # Returns "STDLIB"
section = isort.place_module("numpy")  # Returns "THIRDPARTY" (if not configured otherwise)
```

## Function: `isort.place_module_with_reason`

```python
def place_module_with_reason(
    module_name: str,
    config: Config = DEFAULT_CONFIG,
    **config_kwargs: Any,
) -> tuple[str, str]
```

**Purpose**: Determines which section a module belongs to along with reasoning.

**Returns**: tuple[str, str] - (section_name, reason)

## CLI Entry Points

The package provides two command-line entry points configured in `pyproject.toml`:

### Command: `isort`

**Entry Point**: `isort.main:main`

**Purpose**: Main CLI for sorting imports in Python files.

**Basic Usage**:
- `isort file.py` - Sort imports in a file
- `isort .` - Sort imports recursively in directory
- `isort --check file.py` - Check without modifying
- `isort --diff file.py` - Show diff without modifying

### Command: `isort-identify-imports`

**Entry Point**: `isort.main:identify_imports_main`

**Purpose**: CLI for identifying and analyzing imports in Python files.

## Exception Classes

The package defines several exception classes in `isort.exceptions`:

- `ExistingSyntaxErrors`: Raised when input code has syntax errors (in atomic mode)
- `FileSkipComment`: Raised when file contains skip comment
- `FileSkipSetting`: Raised when file is skipped by configuration
- `IntroducedSyntaxErrors`: Raised when sorting would introduce syntax errors

# Implementation Notes

## Import Section Logic

Imports are categorized into these sections in order:
1. **FUTURE**: `from __future__ import ...` statements
2. **STDLIB**: Standard library modules
3. **THIRDPARTY**: Third-party packages
4. **FIRSTPARTY**: First-party/project modules
5. **LOCALFOLDER**: Local folder imports (relative imports)

The Config class allows customization of which modules belong to which sections via `known_first_party`, `known_third_party`, and `known_stdlib` lists.

## Sorting Algorithm

Within each section, imports are sorted:
1. `import` statements before `from ... import` statements
2. Alphabetically by module name
3. Alphabetically by imported names within a `from` import

## Configuration Priority

Configuration is loaded in this order (later sources override earlier):
1. Default configuration
2. Config file (pyproject.toml, setup.cfg, .isort.cfg, etc.)
3. Explicitly passed Config object
4. Keyword arguments (**config_kwargs)

## File Modification Behavior

- `file()` and `stream()` modify content and return True if changed
- `check_file()` and `check_code()` only verify and return True if already sorted
- All functions support a `show_diff` parameter to preview changes

## Atomic Mode

When `atomic=True` in Config:
- isort compiles the code to check for syntax errors before applying changes
- If syntax errors exist, raises `ExistingSyntaxErrors`
- If sorting would introduce errors, raises `IntroducedSyntaxErrors`
- Disabled by default as it prevents working with different Python versions

## Version Management

The package version is dynamically determined using hatch-vcs from VCS tags. When building from a source archive without .git metadata, the version should be statically configured in pyproject.toml.

## Type Annotations

The package uses type hints extensively and requires `mypy-extensions>=1.1.0` for extended typing support.

## No External Network Dependencies

All functionality operates entirely offline once installed. The tool does not:
- Make network requests
- Access external APIs or services
- Download configuration or data from the internet
- Require internet connectivity for any operation

# Examples

## Basic Import Sorting

```python
import isort

code = """
import os
import sys
from typing import List
import numpy
from myproject import utils
from . import local_module
"""

sorted_code = isort.code(code)
# Output will have imports grouped and sorted:
# - Standard library (os, sys)
# - Third party (typing, numpy)
# - First party (myproject)
# - Local (.)
```

## Checking Import Order

```python
import isort

# Code with incorrectly ordered imports
bad_code = "import sys\nimport os\n"  # os should come before sys

# Check returns False
is_correct = isort.check_code(bad_code)  # False

# Sort and check
fixed_code = isort.code(bad_code)
is_correct = isort.check_code(fixed_code)  # True
```

## Custom Configuration

```python
from isort import Config, code

# Use black profile for compatibility
config = Config(
    profile="black",
    line_length=88,
    known_first_party=["myproject"],
    force_single_line=False
)

code_to_sort = "from myproject import a, b, c\nimport sys\n"
sorted_code = code(code_to_sort, config=config)
```

## Finding Imports

```python
import isort

code = """
import os
from typing import List, Dict
from mypackage.module import func
"""

# Find all imports
for import_info in isort.find_imports_in_code(code):
    print(import_info)
    # Each dict contains: module, line_number, import_type, etc.
```

## Module Placement

```python
import isort

# Determine which section a module belongs to
section = isort.place_module("os")  # "STDLIB"
section = isort.place_module("django")  # "THIRDPARTY"

# With reasoning
section, reason = isort.place_module_with_reason("os")
# ("STDLIB", "known standard library")
```

# Error Handling and Boundary Conditions

## Syntax Errors

When `atomic=True`, isort checks for syntax errors:

```python
import isort
from isort import Config
from isort.exceptions import ExistingSyntaxErrors

config = Config(atomic=True)

# Code with syntax error
bad_syntax = "import os\ndef bad syntax here"

try:
    sorted_code = isort.code(bad_syntax, config=config)
except ExistingSyntaxErrors as e:
    print(f"Code has syntax errors: {e}")
```

## File Skip Handling

Files can be skipped via configuration or skip comments:

```python
import isort
from isort import Config
from isort.exceptions import FileSkipSetting
from pathlib import Path

config = Config(skip=["migrations", "test_*.py"])

try:
    isort.file("test_example.py", config=config)
except FileSkipSetting as e:
    print(f"File was skipped: {e}")
```

## Empty or No-Import Code

isort safely handles code with no imports:

```python
import isort

code = "# Just a comment\nprint('hello')"
sorted_code = isort.code(code)
# Returns the same code unchanged

is_sorted = isort.check_code(code)  # True (no imports to check)
```

## Unicode and Special Characters

isort handles Unicode properly in both import statements and surrounding code:

```python
import isort

code = """
# -*- coding: utf-8 -*-
import sys
import os
# Comment with 中文
"""

sorted_code = isort.code(code)
# Properly handles encoding and special characters
```

## File Path Edge Cases

Functions accepting file paths handle both string and Path objects:

```python
import isort
from pathlib import Path

# Both work identically
isort.check_file("myfile.py")
isort.check_file(Path("myfile.py"))
```

## Config Keyword Override

Configuration can be overridden inline:

```python
import isort
from isort import Config

# Base config
config = Config(line_length=79)

# Override specific options
sorted_code = isort.code(
    "import os\nimport sys",
    config=config,
    line_length=100  # Override just this option
)
```

## Stream Position

Stream functions respect and manage stream positions:

```python
import isort
from io import StringIO

input_stream = StringIO("import sys\nimport os")
output_stream = StringIO()

isort.stream(input_stream, output_stream)

# Output stream is ready to read
output_stream.seek(0)
result = output_stream.read()
```

## Import Iterator Completion

Import-finding functions return iterators that must be consumed:

```python
import isort

code = "import os\nimport sys"

# Iterator can be empty
imports = list(isort.find_imports_in_code("print('no imports')"))
# Returns empty list

# Must consume iterator to get all results
imports = list(isort.find_imports_in_code(code))
# Returns list with import information
```

# Security

## No Code Execution Beyond Parsing

isort only parses and analyzes Python code structure. It does not:
- Execute user code
- Evaluate expressions
- Import or load user modules
- Execute shell commands

## Safe File Operations

When operating on files:
- Only reads and writes text content
- Does not follow symbolic links by default
- Respects file permissions
- Does not delete or move files (only modifies content)

## Atomic Operations

The `atomic` configuration option provides safety:
- Validates syntax before modifying
- Ensures changes don't break code structure
- Rolls back on error (when used with file operations)

## Input Validation

- File paths are validated before operations
- Invalid configurations raise appropriate errors
- Malformed import statements are handled gracefully without crashes
