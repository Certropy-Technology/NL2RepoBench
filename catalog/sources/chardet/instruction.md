# Character Encoding Detection Library (chardet)

## Project Description

chardet is a universal character encoding detector library for Python. It analyzes byte sequences and determines the most likely character encoding (such as UTF-8, ASCII, ISO-8859-1, Shift-JIS, etc.) along with a confidence score. The library supports detection of a wide range of encodings including ASCII, UTF-8/16/32 with and without BOM, Latin encodings (ISO-8859 series, Windows-125x), Chinese encodings (GB2312, GBK, Big5), Japanese encodings (Shift-JIS, EUC-JP, ISO-2022-JP), Korean encodings (EUC-KR), Cyrillic encodings (KOI8-R, Windows-1251), and many others.

The library provides both a simple one-shot detection API via `chardet.detect()` and `chardet.detect_all()` functions, as well as a streaming API through the `UniversalDetector` class for processing data incrementally.

## Supports

- **Python Version**: 3.10+
- **Package Name**: `chardet`
- **Version**: 7.6.0
- **License**: 0BSD
- **Entry Points**: Module `chardet` with functions `detect()`, `detect_all()` and class `UniversalDetector`

## API Usage Guide

### Core Detection Function

```python
import chardet

# Detect encoding of a byte sequence
result = chardet.detect(b'hello world')
# Returns: {'encoding': 'ascii', 'confidence': 1.0, 'language': 'en', 'mime_type': 'text/plain'}
```

**Function**: `chardet.detect(byte_str, should_rename_legacy=False, encoding_era=EncodingEra.ALL, chunk_size=_DEFAULT_CHUNK_SIZE, max_bytes=DEFAULT_MAX_BYTES, *, prefer_superset=False, compat_names=True, include_encodings=None, exclude_encodings=None, no_match_encoding='cp1252', empty_input_encoding='utf-8')`

- **Parameters**:
  - `byte_str` (bytes | bytearray): The byte sequence to detect encoding for
  - `should_rename_legacy` (bool, optional): Deprecated alias for prefer_superset
  - `encoding_era` (EncodingEra, optional): Restrict candidate encodings to a given era (default: EncodingEra.ALL)
  - `chunk_size` (int, optional): Deprecated parameter, has no effect
  - `max_bytes` (int, optional): Maximum number of bytes to examine (default: DEFAULT_MAX_BYTES)
  - `prefer_superset` (bool, optional): If True, remap subset encodings to their superset equivalents (default: False)
  - `compat_names` (bool, optional): If True, return encoding names compatible with chardet 5.x/6.x (default: True)
  - `include_encodings` (Iterable[str] | None, optional): Restrict detection to these encodings
  - `exclude_encodings` (Iterable[str] | None, optional): Exclude these encodings from detection
  - `no_match_encoding` (str, optional): Encoding to return when no candidate matches (default: 'cp1252')
  - `empty_input_encoding` (str, optional): Encoding to return for empty input (default: 'utf-8')

- **Returns**: `dict` with keys:
  - `'encoding'` (str): The detected encoding name
  - `'confidence'` (float): Confidence score between 0.0 and 1.0
  - `'language'` (str | None): Detected language code (e.g., 'en', 'zh', 'ja', 'ko', 'ru')
  - `'mime_type'` (str): MIME type, typically 'text/plain'

- **Behavior**:
  - Returns a single best-match result
  - For empty input, returns UTF-8 encoding with low confidence (0.1)
  - For pure ASCII, typically returns 'ascii' encoding with confidence 1.0
  - For UTF-8 with BOM, returns 'UTF-8-SIG' with confidence 1.0
  - For UTF-16/32 with BOM, returns 'UTF-16' or 'UTF-32' with confidence 1.0
  - Confidence scores vary based on the clarity of encoding signals in the data

### Detect All Encodings

```python
import chardet

# Get all possible encoding detections
results = chardet.detect_all(b'hello world')
# Returns: list of dicts, sorted by descending confidence
```

**Function**: `chardet.detect_all(byte_str, ignore_threshold=False, should_rename_legacy=False, encoding_era=EncodingEra.ALL, chunk_size=_DEFAULT_CHUNK_SIZE, max_bytes=DEFAULT_MAX_BYTES, *, prefer_superset=False, compat_names=True, include_encodings=None, exclude_encodings=None, no_match_encoding='cp1252', empty_input_encoding='utf-8')`

- **Parameters**: Same as `detect()` plus:
  - `ignore_threshold` (bool, optional): If True, return all candidates regardless of confidence (default: False)

- **Returns**: `list[dict]` where each dict has the same structure as `detect()` result, sorted by descending confidence

- **Behavior**:
  - When `ignore_threshold=False`, filters out results with confidence <= 0.20 (MINIMUM_THRESHOLD)
  - If all results are below threshold, returns unfiltered list as fallback
  - Always returns at least one result

### Universal Detector (Streaming API)

```python
import chardet

# Create a detector instance
detector = chardet.UniversalDetector()

# Feed data incrementally
detector.feed(b'Hello ')
detector.feed(b'World')

# Get result
result = detector.close()
# Returns: {'encoding': 'ascii', 'confidence': 1.0, 'language': 'en', 'mime_type': 'text/plain'}

# Reset for reuse
detector.reset()
```

**Class**: `chardet.UniversalDetector(lang_filter=LanguageFilter.ALL, should_rename_legacy=False, encoding_era=EncodingEra.ALL, max_bytes=DEFAULT_MAX_BYTES, *, prefer_superset=False, compat_names=True, include_encodings=None, exclude_encodings=None, no_match_encoding='cp1252', empty_input_encoding='utf-8')`

**Methods**:
- `feed(byte_str)`: Feed a chunk of bytes to the detector
  - Parameters: `byte_str` (bytes | bytearray)
  - Accumulates data in internal buffer
  - Once `max_bytes` reached, sets `done` to True and ignores further data
  - Raises `ValueError` if called after `close()` without `reset()`

- `close()`: Finalize detection and return result
  - Returns: `dict` with same structure as `detect()` result
  - Runs the detection pipeline on buffered data
  - Can be called multiple times (returns cached result)

- `reset()`: Reset the detector to initial state for reuse
  - Clears internal buffer and state
  - Allows detector to be used for new detection

**Properties**:
- `done` (bool): Whether detection is complete and no more data needed
- `result` (dict): Current best detection result (can be accessed before `close()`)

**Class Attributes**:
- `MINIMUM_THRESHOLD` (float): Minimum confidence threshold (0.20)
- `LEGACY_MAP` (MappingProxyType): Mapping of subset to superset encodings

### Constants and Enums

- `chardet.DEFAULT_MAX_BYTES`: Default maximum bytes to examine
- `chardet.MINIMUM_THRESHOLD`: Minimum confidence threshold (0.20)
- `chardet.EncodingEra`: Enum for restricting encoding eras (EncodingEra.ALL, etc.)
- `chardet.LanguageFilter`: Enum for language filtering (LanguageFilter.ALL, etc.)

## Implementation Notes

1. **Package Structure**: The package is named `chardet` and should be importable directly with `import chardet`.

2. **Build System**: Uses `hatchling` as the build backend with `hatch-vcs` for version management. The package uses `pyproject.toml` for configuration.

3. **Entry Point**: Provides a command-line tool `chardetect` for encoding detection from files.

4. **Version Management**: Version is managed by `hatch-vcs` and written to `src/chardet/_version.py` during build. The `__version__` attribute is available in the package.

5. **Type Hints**: The package includes type hints and provides a `py.typed` marker file.

6. **Core Encoding Detection**: The detection pipeline examines byte patterns, byte order marks (BOMs), statistical models, and structural patterns to determine encoding.

7. **Result Determinism**: For the same input bytes and parameters, `chardet.detect()` returns deterministic results. Confidence values are floating-point numbers that may vary slightly across different encoding candidates.

8. **Bytearray Support**: Both `bytes` and `bytearray` inputs are accepted by all detection functions.

9. **Empty Input**: Empty byte sequences return UTF-8 encoding with a confidence of 0.1.

10. **BOM Detection**: Byte Order Marks are reliably detected:
    - UTF-8 BOM (`\xef\xbb\xbf`) → 'UTF-8-SIG' with confidence 1.0
    - UTF-16 LE BOM (`\xff\xfe`) → 'UTF-16' with confidence 1.0
    - UTF-16 BE BOM (`\xfe\xff`) → 'UTF-16' with confidence 1.0
    - UTF-32 LE BOM (`\xff\xfe\x00\x00`) → 'UTF-32' with confidence 1.0
    - UTF-32 BE BOM (`\x00\x00\xfe\xff`) → 'UTF-32' with confidence 1.0

11. **ASCII Detection**: Pure ASCII text (bytes < 128) is detected as 'ascii' with confidence 1.0.

12. **Multi-byte Encodings**: The library has strong support for detecting:
    - Chinese: UTF-8, GB2312, GBK, GB18030, Big5
    - Japanese: UTF-8, Shift-JIS/CP932, EUC-JP, ISO-2022-JP
    - Korean: UTF-8, EUC-KR, CP949
    - Cyrillic: UTF-8, KOI8-R, Windows-1251, ISO-8859-5
    - Arabic: UTF-8, ISO-8859-6, Windows-1256
    - Greek: UTF-8, ISO-8859-7, Windows-1253
    - Hebrew: UTF-8, ISO-8859-8, Windows-1255

13. **Thread Safety**: `UniversalDetector` is NOT thread-safe. Each thread should create its own instance.

## Environment Configuration

- **Python Version**: Requires Python >= 3.10
- **Dependencies**: No runtime dependencies (self-contained)
- **Build Dependencies**: `hatchling`, `hatch-vcs` (for building from source)
- **Optional Dependencies**: `Cython`, `setuptools`, `mypy` (for compiled optimizations, not required for core functionality)

## Project Directory Structure

```
workspace/
├── pyproject.toml           # Project metadata and build configuration
├── README.md                # Package documentation
├── LICENSE                  # 0BSD license text
├── src/
│   └── chardet/
│       ├── __init__.py      # Main API exports: detect, detect_all, UniversalDetector
│       ├── _version.py      # Version information (generated by hatch-vcs)
│       ├── detector.py      # UniversalDetector class implementation
│       ├── cli.py           # Command-line interface
│       ├── __main__.py      # Module entry point
│       ├── enums.py         # EncodingEra, LanguageFilter enums
│       ├── _utils.py        # Utility functions and constants
│       ├── registry.py      # Encoding registry and normalization
│       ├── output_names.py  # Encoding name mapping and compatibility
│       ├── equivalences.py  # Encoding equivalence rules
│       ├── evaluation.py    # Detection evaluation utilities
│       ├── universaldetector.py  # Legacy compatibility module
│       ├── py.typed         # Type hints marker
│       ├── _kernel.py       # Core detection kernel
│       ├── _kernel.pxd      # Cython type declarations (build-time only)
│       ├── models/          # Statistical models for encoding detection
│       │   └── __init__.py
│       └── pipeline/        # Detection pipeline modules
│           ├── __init__.py
│           ├── orchestrator.py    # Main pipeline orchestration
│           ├── structural.py      # Structural pattern detection
│           ├── validity.py        # Validity checking
│           ├── statistical.py     # Statistical analysis
│           ├── utf1632.py         # UTF-16/32 detection
│           ├── utf8.py            # UTF-8 detection
│           ├── escape.py          # Escape sequence detection
│           ├── language.py        # Language detection
│           ├── magic.py           # Magic byte detection (BOM)
│           ├── ascii.py           # ASCII detection
│           ├── postprocess.py     # Post-processing
│           └── confusion.py       # Confusion resolution
└── tests/                   # Test suite (not part of installed package)
```

**Import Paths**:
- `import chardet` - Main package
- `chardet.detect(bytes)` - One-shot detection
- `chardet.detect_all(bytes)` - Multiple results
- `chardet.UniversalDetector()` - Streaming detector
- `chardet.__version__` - Version string
- `chardet.EncodingEra` - Encoding era enum
- `chardet.LanguageFilter` - Language filter enum
