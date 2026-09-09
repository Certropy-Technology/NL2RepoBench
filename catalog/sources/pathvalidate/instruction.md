# pathvalidate

## Natural Language Instruction

Build a Python library called **pathvalidate** that provides comprehensive validation and sanitization of file names and file paths across multiple platforms (Windows, Linux, macOS, POSIX, and universal).

The library should handle platform-specific invalid characters, reserved names, path length limitations, and provide both validation (raising exceptions on invalid input) and sanitization (cleaning invalid input to make it valid).

## Project Description

`pathvalidate` is a Python library that sanitizes and validates strings such as filenames and file paths. It helps ensure that file and path names are valid for specific platforms or universally valid across all platforms.

Key features include:
- Validation and sanitization of filenames and filepaths
- Multi-platform support (Windows, Linux, macOS, POSIX, universal)
- Handling of invalid characters, reserved names, and length constraints
- Support for multibyte characters (Unicode)
- Detailed error reporting with specific error codes and reasons

## Supports

- Python 3.9 or later
- Multi-platform: Linux, Windows, macOS, POSIX, and universal validation
- No external runtime dependencies

## Environment Configuration

- Python version: 3.12
- Operating system: Debian 12 (amd64)
- Package manager: pip
- No external dependencies required

## API Usage Guide

### Core Functions

#### `validate_filename(filename, platform="universal", **kwargs)`

Validates a filename string. Raises an exception if the filename is invalid.

**Parameters:**
- `filename` (str): The filename to validate
- `platform` (str or Platform): Target platform ("universal", "windows", "linux", "macos", "posix", or Platform enum). Default: "universal"
- `min_len` (int): Minimum byte length. Default: 1
- `max_len` (int): Maximum byte length. Platform-specific defaults
- `check_reserved` (bool): Check for reserved names. Default: True

**Returns:** None (raises exception if invalid)

**Raises:**
- `ValidationError`: Base exception for all validation errors
- `NullNameError`: When filename is empty (subclass of ValidationError)
- `InvalidCharError`: When filename contains invalid characters
- `ReservedNameError`: When filename matches a reserved name
- `InvalidLengthError`: When filename length is invalid

**Example:**
```python
from pathvalidate import validate_filename

# Valid filename - no exception
validate_filename("example.txt")

# Invalid - raises InvalidCharError
validate_filename("file:name.txt")  # colon invalid on Windows

# Empty name - raises NullNameError
validate_filename("")
```

#### `sanitize_filename(filename, platform="universal", **kwargs)`

Sanitizes a filename by removing or replacing invalid characters.

**Parameters:**
- `filename` (str): The filename to sanitize
- `platform` (str or Platform): Target platform. Default: "universal"
- `replacement_text` (str): Text to replace invalid characters. Default: ""
- `max_len` (int): Maximum byte length
- `check_reserved` (bool): Check for reserved names. Default: True

**Returns:** str - The sanitized filename

**Example:**
```python
from pathvalidate import sanitize_filename

# Remove invalid characters
result = sanitize_filename("fi:l*e/p\"a?t>h|.t<xt")
# Result: "filepath.txt"

# Custom replacement
result = sanitize_filename("file:name.txt", replacement_text="_")
# Result: "file_name.txt"
```

#### `is_valid_filename(filename, platform="universal", **kwargs)`

Checks if a filename is valid without raising an exception.

**Parameters:** Same as `validate_filename`

**Returns:** bool - True if valid, False otherwise

**Example:**
```python
from pathvalidate import is_valid_filename

is_valid_filename("example.txt")  # True
is_valid_filename("file:name.txt")  # False
```

#### `validate_filepath(filepath, platform="auto", **kwargs)`

Validates a file path string. Raises an exception if invalid.

**Parameters:**
- `filepath` (str): The filepath to validate
- `platform` (str or Platform): Target platform. Default: "auto" (auto-detect from path)
- `check_reserved` (bool): Check for reserved names. Default: True

**Returns:** None (raises exception if invalid)

**Example:**
```python
from pathvalidate import validate_filepath

validate_filepath("path/to/file.txt")
validate_filepath("C:\\path\\to\\file.txt", platform="windows")
```

#### `sanitize_filepath(filepath, platform="auto", **kwargs)`

Sanitizes a file path by removing or replacing invalid characters.

**Parameters:**
- `filepath` (str): The filepath to sanitize
- `platform` (str or Platform): Target platform. Default: "auto"
- `replacement_text` (str): Replacement for invalid characters. Default: ""

**Returns:** str - The sanitized filepath

**Example:**
```python
from pathvalidate import sanitize_filepath

result = sanitize_filepath("path/to/fi:le.txt")
# Result: "path/to/file.txt"
```

#### `is_valid_filepath(filepath, platform="auto", **kwargs)`

Checks if a filepath is valid without raising an exception.

**Returns:** bool - True if valid, False otherwise

### Platform Enum

```python
from pathvalidate import Platform

# Available platforms:
Platform.UNIVERSAL  # Valid across all platforms (most restrictive)
Platform.WINDOWS    # Windows-specific validation
Platform.LINUX      # Linux-specific validation
Platform.MACOS      # macOS-specific validation
Platform.POSIX      # POSIX-compliant systems
```

### Exception Classes

All exceptions inherit from `ValidationError`, which has these properties:

- `reason`: ErrorReason enum value
- `platform`: Platform enum value (if applicable)
- `description`: Human-readable error description
- `reserved_name`: The reserved name that was matched (for ReservedNameError)

#### Error Reasons

```python
from pathvalidate import ErrorReason

ErrorReason.NULL_NAME          # Empty string
ErrorReason.RESERVED_NAME      # Platform reserved name
ErrorReason.INVALID_CHARACTER  # Invalid characters
ErrorReason.INVALID_LENGTH     # Invalid string length
```

### Reserved Names

Windows has reserved device names that cannot be used as filenames:
- `CON`, `PRN`, `AUX`, `NUL`
- `COM1` through `COM9`
- `LPT1` through `LPT9`
- `CLOCK$`

These are case-insensitive and apply with or without extensions (e.g., `CON.txt` is also reserved).

### Invalid Characters

Platform-specific invalid characters:
- **Universal**: `/`, null byte (`\0`), and all characters invalid on any platform
- **Windows**: `<`, `>`, `:`, `"`, `/`, `\\`, `|`, `?`, `*`, null byte, control characters (ASCII 1-31)
- **Linux/POSIX**: `/`, null byte
- **macOS**: `:`, `/`, null byte

## Implementation Notes

### Directory Structure

```
workspace/
├── pathvalidate/
│   ├── __init__.py
│   ├── __version__.py
│   ├── _base.py
│   ├── _common.py
│   ├── _const.py
│   ├── _filename.py
│   ├── _filepath.py
│   ├── _symbol.py
│   ├── _types.py
│   ├── error.py
│   └── handler.py
├── setup.py
├── pyproject.toml
├── README.rst
└── LICENSE
```

### Key Implementation Requirements

1. **Platform Detection**: Support `"auto"` platform detection for filepaths (determines platform from path structure)

2. **Character Validation**: 
   - Null bytes must always be invalid
   - Platform-specific character sets
   - Universal platform uses the most restrictive set

3. **Reserved Name Handling**:
   - Case-insensitive matching for Windows reserved names
   - Reserved names apply with or without file extensions
   - `check_reserved` parameter controls this behavior

4. **Sanitization Strategy**:
   - Remove or replace invalid characters based on `replacement_text`
   - Handle reserved names by adding suffix or prefix
   - Preserve file extensions where possible
   - Handle multibyte/Unicode characters correctly

5. **Length Validation**:
   - Default max length: 255 bytes for filenames on most platforms
   - Windows path max: typically 260 characters (but can be longer with extended paths)
   - Check byte length, not character count

6. **Error Context**:
   - All exceptions should provide detailed context (platform, invalid characters, etc.)
   - Use error codes (PV1001, PV1002, PV1100, etc.)
   - Include the invalid value in error messages

### Testing Approach

Your implementation should handle:
- Valid filenames across all platforms
- Invalid characters for each platform
- Reserved names (especially Windows device names)
- Empty strings and null names
- Unicode and multibyte characters
- Path separators in filenames vs filepaths
- Length constraints
- Edge cases like filenames that are just extensions (`.txt`)

### Package Metadata

- Package name: `pathvalidate`
- Version: 3.3.1
- License: MIT
- Author: Tsuyoshi Hombashi
- Python requires: >=3.9

The package should be installable via pip and importable as shown in the examples.
