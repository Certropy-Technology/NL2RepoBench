# Project Description

`binaryornot` is a lightweight, zero-dependency Python library that accurately detects whether a file is binary or text. It uses machine learning-derived decision trees to analyze byte patterns, character distributions, encoding validity, and file signatures, providing reliable classification that handles edge cases like UTF-16 text files, multi-byte encodings, and files without null bytes.

Unlike naive null-byte checks, `binaryornot` correctly identifies UTF-16 text files (which contain many null bytes), handles various text encodings (UTF-8, Big5, GB2312, Shift-JIS), and recognizes binary file signatures. The library is used by tools like Cookiecutter to avoid corrupting binary files during template processing.

# Natural Language Instruction

Implement a Python package named `binaryornot` that provides binary vs text file detection capabilities. The package must:

1. Detect whether a file or byte string is binary or text using statistical analysis
2. Recognize known binary file extensions and magic signatures
3. Compute byte-level features including null ratios, control character ratios, encoding validity, Shannon entropy, and BOM detection
4. Use a pre-trained decision tree classifier to make classification decisions
5. Provide both file-based (`is_binary`) and byte string-based (`is_binary_string`) detection
6. Support optional file extension checking to quickly identify known binary formats
7. Handle various text encodings including UTF-8, UTF-16 (LE/BE), UTF-32 (LE/BE), and CJK encodings
8. Provide helper functions for extension checking and chunk reading
9. Include a command-line interface for quick file classification
10. Package with `pyproject.toml` using the Hatch build backend

The package name is `binaryornot`, the import name is `binaryornot`, and it must be installable via pip with zero runtime dependencies.

# Supports (Environment Configuration)

- Python: 3.10+
- Package Manager: pip (Hatch build backend)
- Build System: `hatchling`
- Runtime Dependencies: None (uses only Python standard library: csv, logging, math, os, pathlib, argparse, importlib.resources)
- Installation: `pip install .`
- Testing: pytest, hypothesis
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── pyproject.toml
├── src/
│   └── binaryornot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── check.py
│       ├── helpers.py
│       ├── tree.py
│       └── data/
│           ├── __init__.py
│           ├── binary_extensions.csv
│           └── binary_formats.csv
```

# API Usage Guide

## Module: `binaryornot.check`

### `is_binary(filename, *, check_extensions=True) -> bool`

Determine if a file is binary or text.

- **Parameters:**
  - `filename` (str | bytes | Path): Path to the file to check
  - `check_extensions` (bool, keyword-only): If True (default), check file extension against known binary types before reading file contents. Set to False to classify purely by file contents.
- **Returns:** `True` if the file appears to be binary, `False` if it appears to be text
- **Behavior:**
  - If `check_extensions=True` and the file has a known binary extension, immediately returns `True`
  - Otherwise reads the first 512 bytes (starting chunk) and analyzes them
  - Empty files return `False` (treated as text)
- **Example:**
  ```python
  from binaryornot.check import is_binary
  
  is_binary('image.png')        # True (by extension)
  is_binary('README.md')         # False (text file)
  is_binary('data.sqlite')       # True (binary content)
  is_binary('report.csv')        # False (text content)
  
  # Ignore extension, analyze content only
  is_binary('image.png', check_extensions=False)  # May return False if content is text
  ```

### `main() -> None`

Command-line interface entry point. Parses arguments and prints boolean result.

- **CLI Usage:**
  ```bash
  binaryornot <filename>
  binaryornot image.png    # Prints: True
  binaryornot README.md    # Prints: False
  ```

## Module: `binaryornot.helpers`

### `is_binary_string(bytes_to_check: bytes) -> bool`

Determine if a byte chunk appears to be binary or text.

- **Parameters:**
  - `bytes_to_check` (bytes): Byte sequence to analyze
- **Returns:** `True` if appears to be binary, `False` if appears to be text
- **Behavior:**
  - Empty bytes return `False`
  - Checks for known binary file signatures (magic bytes)
  - Computes 24 features including:
    - Byte class ratios (null, control, printable ASCII, high bytes)
    - Encoding validity (UTF-8, UTF-16 LE/BE, UTF-32 LE/BE, CJK encodings)
    - BOM detection (UTF-8, UTF-16, UTF-32)
    - Shannon entropy
    - Even/odd null byte ratios
    - Longest printable ASCII run
  - Passes features to decision tree classifier
- **Example:**
  ```python
  from binaryornot.helpers import is_binary_string
  
  is_binary_string(b'Hello, World!')           # False (ASCII text)
  is_binary_string(b'\x00' * 100)              # True (pure null bytes)
  is_binary_string('你好世界'.encode('utf-8'))  # False (valid UTF-8)
  is_binary_string(b'\x89PNG\r\n\x1a\n')       # True (PNG signature)
  is_binary_string(b'')                        # False (empty)
  ```

### `has_binary_extension(filename: str | bytes | Path) -> bool`

Check if a filename has a known binary file extension.

- **Parameters:**
  - `filename` (str | bytes | Path): Filename or path to check
- **Returns:** `True` if extension is in the known binary list, `False` otherwise
- **Behavior:**
  - Extracts file extension and checks against preloaded list from `binary_extensions.csv`
  - Comparison is case-insensitive
  - Handles bytes filenames (for CJK locales) by decoding with filesystem encoding
  - Extensions include: png, jpg, jpeg, gif, pdf, exe, zip, tar, gz, woff, pyc, so, dll, bin, and many more
- **Example:**
  ```python
  from binaryornot.helpers import has_binary_extension
  
  has_binary_extension('image.png')     # True
  has_binary_extension('script.py')     # False
  has_binary_extension('data.bin')      # True
  has_binary_extension('README.md')     # False
  has_binary_extension('IMAGE.PNG')     # True (case-insensitive)
  ```

### `get_starting_chunk(filename: str | bytes | Path, length: int = 512) -> bytes`

Read the first chunk of bytes from a file.

- **Parameters:**
  - `filename` (str | bytes | Path): File to read
  - `length` (int): Number of bytes to read (default: 512, defined as `CHUNK_SIZE`)
- **Returns:** Byte string containing the first `length` bytes (or fewer if file is shorter)
- **Behavior:**
  - Opens file in binary read mode
  - Reads up to `length` bytes from the beginning
  - Returns actual bytes read (may be less than `length` for short files)
- **Example:**
  ```python
  from binaryornot.helpers import get_starting_chunk
  
  chunk = get_starting_chunk('file.txt')         # First 512 bytes
  chunk = get_starting_chunk('file.txt', 100)    # First 100 bytes
  len(get_starting_chunk('short.txt'))           # May be < 512 for short files
  ```

### `print_as_hex(s: str) -> None`

Print a string as colon-separated hex values. Utility function for debugging.

- **Parameters:**
  - `s` (str): String to print as hex
- **Returns:** None (prints to stdout)
- **Example:**
  ```python
  from binaryornot.helpers import print_as_hex
  
  print_as_hex('ABC')  # Prints: 41:42:43
  ```

### Constants and Data Loading

- **`CHUNK_SIZE = 512`**: Default number of bytes to read for classification
- **`BINARY_EXTENSIONS`**: Frozen set of known binary file extensions loaded from CSV
- **`_BINARY_SIGNATURES`**: Tuple of known binary file magic byte signatures loaded from CSV

The module also includes private helper functions:
- `_load_binary_extensions()`: Loads extensions from `data/binary_extensions.csv`
- `_load_binary_signatures()`: Loads magic bytes from `data/binary_formats.csv`
- `_has_known_binary_signature(chunk: bytes) -> bool`: Checks for magic signatures
- `_compute_features(chunk: bytes) -> list[float]`: Computes 24 classification features

## Module: `binaryornot.tree`

### `is_binary(features: list[float]) -> bool`

Classify a byte chunk as binary or text using a trained decision tree.

- **Parameters:**
  - `features` (list[float]): List of 24 numeric features computed by `helpers._compute_features()`
- **Returns:** `True` for binary, `False` for text
- **Feature Indices:**
  - 0: null_ratio
  - 1: control_ratio
  - 2: printable_ascii_ratio
  - 3: high_byte_ratio (0x80-0xFF)
  - 4: utf8_valid
  - 5: even_null_ratio
  - 6: odd_null_ratio
  - 7: byte_entropy (Shannon)
  - 8-12: BOM flags (UTF-32 LE/BE, UTF-16 LE/BE, UTF-8)
  - 13-16: Encoding validity (UTF-16 LE/BE, UTF-32 LE/BE)
  - 17: longest_printable_run
  - 18-22: CJK encoding validity (GB2312, Big5, Shift-JIS, EUC-JP, EUC-KR)
  - 23: has_magic_signature
- **Note:** This is an auto-generated decision tree. Do not edit by hand. The tree contains nested if-else conditionals based on feature thresholds.

## Data Files

### `data/binary_extensions.csv`

CSV file containing known binary file extensions. Format:
```csv
extension
png
jpg
jpeg
...
```

Must include common binary formats: png, jpg, jpeg, gif, pdf, exe, zip, tar, gz, bin, so, dll, pyc, woff, woff2, ttf, otf, eot, mp3, mp4, avi, mov, wav, ico, bmp, tiff, psd, ai, eps, svg (if rendered), wasm, and more.

### `data/binary_formats.csv`

CSV file containing known binary file magic signatures. Format:
```csv
format,magic_hex,description
PNG,89504e470d0a1a0a,PNG image signature
JPEG,ffd8ffe0,JPEG/JFIF image
PDF,255044462d,PDF document (%PDF-)
ZIP,504b0304,ZIP archive
...
```

The `magic_hex` column contains hexadecimal strings (without 0x prefix) that represent the byte sequence at the start of binary files.

# Implementation Notes

## Decision Tree Classifier

The `tree.py` module contains a hard-coded decision tree that was trained on a dataset of text and binary files. The tree uses 24 features to make classification decisions. The tree structure is a series of nested if-else statements checking feature values against learned thresholds.

## Byte Analysis

The `_compute_features` function in `helpers.py` performs comprehensive byte analysis:

1. **Basic ratios:** Null bytes, control chars (0x01-0x08, 0x0E-0x1F), printable ASCII (0x20-0x7E), high bytes (0x80-0xFF)
2. **Encoding validity:** Attempts to decode as UTF-8, UTF-16 LE/BE, UTF-32 LE/BE, and CJK encodings
3. **BOM detection:** Checks for UTF-8, UTF-16, and UTF-32 byte order marks
4. **Entropy:** Shannon entropy of byte distribution (0 to 8 bits)
5. **Null distribution:** Separate ratios for even and odd positions (helps detect UTF-16)
6. **Printable runs:** Longest consecutive sequence of printable characters
7. **Magic signatures:** Presence of known binary file headers

## Extension Checking

When `check_extensions=True` (the default), `is_binary()` first checks the file extension. This provides fast classification for files with obvious binary extensions like `.png`, `.exe`, `.zip`, etc., without reading file contents.

## Empty Files

Empty files (zero bytes) are classified as text (return `False`). Empty byte strings also return `False`.

## Path Handling

Functions accept `str`, `bytes`, or `pathlib.Path` objects for file paths. Bytes paths are decoded using the filesystem encoding to handle non-UTF-8 filenames in CJK locales.

## Logging

The module uses Python's `logging` module. Debug messages include feature values and classification results for troubleshooting.

## Command-Line Interface

The package provides a `binaryornot` command via entry point:
```bash
python -m binaryornot <filename>
# or after installation:
binaryornot <filename>
```

The CLI prints `True` or `False` to stdout based on the classification result.

## No External Dependencies

The package has zero runtime dependencies. All functionality is implemented using Python's standard library. This makes it suitable for inclusion in tools that need to minimize dependency chains.

## Build System

Uses Hatch (`hatchling`) as the build backend. Installation command:
```bash
pip install .
```

The package uses the `src/` layout with the package code in `src/binaryornot/`.
