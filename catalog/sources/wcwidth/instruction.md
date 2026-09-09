# wcwidth

## Project Description

`wcwidth` is a Python library that measures the displayed width of unicode strings in a terminal. It provides accurate character width calculations for various Unicode categories including ASCII, control characters, zero-width combining marks, wide CJK (Chinese, Japanese, Korean) characters, and emoji. The library is essential for terminal applications that need to properly align text, handle line wrapping, or calculate string display lengths across different character sets.

## Natural Language Instruction

Your task is to implement the `wcwidth` Python package from scratch. The package must provide:

1. **Character width measurement**: Function `wcwidth(wc, unicode_version='auto', ambiguous_width=1)` that returns the display width of a single Unicode character (0 for combining, 1 for normal, 2 for wide, -1 for control characters).

2. **String width measurement**: Function `wcswidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1)` that calculates the total display width of a Unicode string, optionally limiting to the first `n` characters.

3. **Terminal-aware width measurement**: Function `wcstwidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1, term_program=True)` that provides terminal-specific width calculations with grapheme clustering support.

4. **Unicode category handling**: Proper classification and width assignment for ASCII (width 1), control characters (width -1), zero-width combining characters (width 0), wide East Asian characters (width 2), and ambiguous characters (configurable width 1 or 2).

**Package requirements**:
- **Package name**: `wcwidth` (importable as `import wcwidth`)
- **Installation**: Standard `pip install` from the workspace directory
- **Public API**: Must export `wcwidth`, `wcswidth`, and `wcstwidth` functions from the top-level module
- **Version**: `__version__` attribute must be set to `"0.8.3"`
- **No external runtime dependencies**: The package must work without any third-party dependencies

## Supports

- **Language**: Python 3.12
- **Package Manager**: pip
- **Installation Command**: `pip install -e .` (editable install from workspace)
- **Build Backend**: Any standard Python build backend (setuptools, hatchling, flit, etc.)
- **Runtime Dependencies**: None
- **Build Dependencies**: Standard build backends only
- **Network**: NoNetwork - All operations must work without network access
- **Platform**: Linux (Debian 12 amd64)

## Project Directory Structure

```
workspace/
├── wcwidth/
│   └── __init__.py          # Main module with wcwidth, wcswidth, wcstwidth functions
├── pyproject.toml           # Project metadata and build configuration
└── README.md                # Optional project documentation
```

The package must be installable and importable as `wcwidth`. The core functionality should be implemented in `wcwidth/__init__.py` or split across multiple files within the `wcwidth/` directory.

## API Usage Guide

### Module: `wcwidth`

Import: `import wcwidth`

#### Function: `wcwidth(wc, unicode_version='auto', ambiguous_width=1)`

**Purpose**: Determine the display width of a single Unicode character.

**Parameters**:
- `wc` (str): A single Unicode character (length 1 string)
- `unicode_version` (str, optional): Unicode version selector. Default `'auto'` uses the latest version. Deprecated parameter, can be ignored in implementation.
- `ambiguous_width` (int, optional): Width to use for East Asian Ambiguous category characters. Default `1` (narrow). Set to `2` for CJK contexts where ambiguous characters display as double-width.

**Returns**: `int`
- `0`: Zero-width characters (combining marks, zero-width joiner, etc.)
- `1`: Normal width characters (ASCII printable, most Latin/Cyrillic/Greek, halfwidth katakana, etc.)
- `2`: Wide characters (CJK ideographs, fullwidth forms, wide emoji, etc.)
- `-1`: Control characters (C0/C1 control codes) or characters with indeterminate terminal effect

**Return value rules**:
- Empty string (`""`) returns `0`
- ASCII printable characters (0x20-0x7E) return `1`
- Control characters (0x00-0x1F, 0x7F-0x9F) return `-1`
- Zero-width combining marks and joiners return `0`
- East Asian Wide (W) and Fullwidth (F) characters return `2`
- East Asian Ambiguous (A) characters return `ambiguous_width` (default `1`)
- All other characters return `1`

**Examples**:
```python
wcwidth.wcwidth('a')      # 1 - ASCII letter
wcwidth.wcwidth('中')     # 2 - Chinese character (wide)
wcwidth.wcwidth('\u0301') # 0 - Combining acute accent
wcwidth.wcwidth('\t')     # -1 - Tab (control character)
wcwidth.wcwidth('α')      # 1 - Greek alpha (ambiguous, default narrow)
wcwidth.wcwidth('α', ambiguous_width=2)  # 2 - Greek alpha in CJK context
```

#### Function: `wcswidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1)`

**Purpose**: Calculate the total display width of a Unicode string.

**Parameters**:
- `pwcs` (str): Unicode string to measure
- `n` (int or None, optional): If not None, measure only the first `n` characters. If None (default), measure the entire string.
- `unicode_version` (str, optional): Unicode version selector (deprecated, can be ignored)
- `ambiguous_width` (int, optional): Width for ambiguous characters, default `1`

**Returns**: `int`
- Non-negative integer: Total display width in terminal cells
- `-1`: String contains control characters (C0/C1)

**Behavior**:
- Empty string returns `0`
- If string contains any control character, returns `-1` immediately
- Combining characters contribute 0 width and attach to preceding base character
- The width is the sum of individual character widths from `wcwidth()`
- If `n` is specified and less than string length, only first `n` characters are measured
- If `n` is greater than string length, measures the entire string

**Examples**:
```python
wcwidth.wcswidth('hello')           # 5 - Five ASCII characters
wcwidth.wcswidth('中文')            # 4 - Two wide Chinese characters
wcwidth.wcswidth('hello中文')       # 9 - Mixed ASCII and Chinese
wcwidth.wcswidth('hello\nworld')    # -1 - Contains control character
wcwidth.wcswidth('e\u0301')         # 1 - e + combining accent = 1 cell
wcwidth.wcswidth('hello world', 5)  # 5 - First 5 characters only
```

#### Function: `wcstwidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1, term_program=True)`

**Purpose**: Calculate display width with terminal-specific grapheme handling.

**Parameters**:
- `pwcs` (str): Unicode string to measure
- `n` (int or None, optional): Measure only first `n` characters if specified
- `unicode_version` (str, optional): Unicode version (deprecated)
- `ambiguous_width` (int, optional): Width for ambiguous characters, default `1`
- `term_program` (bool or str, optional): Terminal identifier for override tables. `True` (default) auto-detects from environment, `False` disables overrides. Can accept specific terminal names.

**Returns**: `int`
- Display width considering grapheme clusters and terminal-specific behavior
- Similar to `wcswidth()` but with enhanced grapheme cluster handling

**Note**: For the basic implementation required by this task, `wcstwidth()` can be implemented as a wrapper around `wcswidth()` that provides the same functionality. Full terminal-specific grapheme override support is optional for passing tests.

**Examples**:
```python
wcwidth.wcstwidth('hello')     # 5
wcwidth.wcstwidth('こんにちは')  # 10 - Japanese hiragana
```

## Implementation Notes

### Unicode Character Categories

The implementation must correctly handle these Unicode categories:

1. **ASCII Printable** (0x20-0x7E): Always width 1
2. **Control Characters** (C0: 0x00-0x1F, 0x7F; C1: 0x80-0x9F): Always width -1
3. **Zero-Width Characters**: Combining marks (category Mn), zero-width joiner (U+200D), zero-width non-joiner (U+200C), etc. - width 0
4. **Wide Characters**: East Asian Wide (W) and Fullwidth (F) characters including:
   - CJK ideographs (Chinese, Japanese, Korean characters)
   - Fullwidth ASCII variants (e.g., "Ａ" fullwidth A)
   - Wide emoji
   - Katakana and Hiragana
5. **East Asian Ambiguous**: Characters like Greek letters, box drawing - width depends on `ambiguous_width` parameter

### Width Calculation Algorithm

For `wcswidth()`:
1. If string is empty, return 0
2. Iterate through each character
3. Call `wcwidth()` for each character
4. If any character returns -1, immediately return -1
5. Sum all non-negative widths
6. Respect the `n` parameter to limit character count

### Combining Characters

Combining characters (category Mn) have zero width and visually overlay the preceding base character:
- `'e' + '\u0301'` (combining acute accent) displays as `'é'` in 1 cell
- Implementation should return 0 for combining characters from `wcwidth()`
- String measurement correctly sums to base character width

### Ambiguous Width Handling

East Asian Ambiguous characters appear differently in CJK vs Western contexts:
- Default: `ambiguous_width=1` (narrow, for Western/terminal default)
- CJK context: `ambiguous_width=2` (wide, for CJK-configured terminals)
- Examples: Greek letters (α, β, γ), box drawing (─, │), degree sign (°)

### Error Handling

- Empty string to `wcwidth()`: return 0
- String longer than 1 character to `wcwidth()`: implementation-defined (typically measure first character)
- Control characters: always return -1 from `wcwidth()`, cause -1 from `wcswidth()`
- `n=0` to `wcswidth()`: return 0
- `n > len(string)` to `wcswidth()`: measure entire string

### Determinism

All functions must be deterministic - same input always produces same output. No randomness, no system state dependencies (except terminal detection in `wcstwidth()` when requested).

## Examples

### Basic Character Width Measurement

```python
import wcwidth

# ASCII characters
assert wcwidth.wcwidth('A') == 1
assert wcwidth.wcwidth('5') == 1
assert wcwidth.wcwidth(' ') == 1

# Control characters
assert wcwidth.wcwidth('\n') == -1
assert wcwidth.wcwidth('\t') == -1
assert wcwidth.wcwidth('\x00') == 0  # NULL is special case

# Wide CJK characters
assert wcwidth.wcwidth('中') == 2  # Chinese
assert wcwidth.wcwidth('あ') == 2  # Japanese hiragana
assert wcwidth.wcwidth('한') == 2  # Korean hangul

# Zero-width combining
assert wcwidth.wcwidth('\u0301') == 0  # Combining acute accent
```

### String Width Measurement

```python
import wcwidth

# Pure ASCII
assert wcwidth.wcswidth('hello') == 5
assert wcwidth.wcswidth('hello world') == 11

# CJK strings
assert wcwidth.wcswidth('中文') == 4      # Two Chinese chars
assert wcwidth.wcswidth('こんにちは') == 10  # Japanese

# Mixed content
assert wcwidth.wcswidth('hello中文') == 9  # 5 + 4

# Combining characters
assert wcwidth.wcswidth('café') == 4  # c + a + f + é(composed)
```

### Limited String Measurement

```python
import wcwidth

# Measure first n characters
assert wcwidth.wcswidth('hello world', 5) == 5
assert wcwidth.wcswidth('中文日本', 2) == 4  # First 2 chars = 2*2
assert wcwidth.wcswidth('hello', 0) == 0
assert wcwidth.wcswidth('hi', 100) == 2  # n > length is ok
```

### Control Character Handling

```python
import wcwidth

# Strings with control characters return -1
assert wcwidth.wcswidth('hello\nworld') == -1
assert wcwidth.wcswidth('test\tstring') == -1
```

## Error Handling and Boundary Conditions

### Empty Strings

```python
import wcwidth

# Empty string has zero width
assert wcwidth.wcwidth('') == 0
assert wcwidth.wcswidth('') == 0
assert wcwidth.wcswidth('hello', 0) == 0
```

### Ambiguous Character Context

```python
import wcwidth

# Greek alpha - ambiguous category
assert wcwidth.wcwidth('α') == 1  # Default narrow
assert wcwidth.wcwidth('α', ambiguous_width=1) == 1
assert wcwidth.wcwidth('α', ambiguous_width=2) == 2  # CJK context

# Degree sign - ambiguous
assert wcwidth.wcwidth('°') == 1  # Default
```

### Fullwidth vs Halfwidth

```python
import wcwidth

# Fullwidth characters (F category) are wide
assert wcwidth.wcwidth('Ａ') == 2  # Fullwidth A
assert wcwidth.wcwidth('０') == 2  # Fullwidth digit 0

# Halfwidth katakana are narrow
assert wcwidth.wcwidth('ｱ') == 1   # Halfwidth katakana
```

### Edge Cases

```python
import wcwidth

# NULL character is special - width 0 not -1
assert wcwidth.wcwidth('\x00') == 0

# Other C0 controls are -1
assert wcwidth.wcwidth('\x01') == -1
assert wcwidth.wcwidth('\x1f') == -1

# DEL and C1 controls are -1
assert wcwidth.wcwidth('\x7f') == -1
assert wcwidth.wcwidth('\x80') == -1
```

## Security

The implementation must be safe for all Unicode input:
- No buffer overflows or memory issues
- Handle all valid Unicode codepoints gracefully
- Do not crash on any string input
- Combining character sequences should not cause issues
- Very long strings should be handled efficiently

## Testing

The implementation will be tested against a comprehensive test suite covering:
- All ASCII printable characters (width 1)
- Control characters (C0/C1, width -1 or 0)
- Zero-width combining marks (width 0)
- Wide CJK characters from Chinese, Japanese, Korean (width 2)
- Fullwidth variants (width 2)
- Emoji characters (various widths)
- Ambiguous characters with both width settings
- String measurements with `wcswidth()`
- Limited string measurements with `n` parameter
- Mixed scripts and character categories
- Edge cases and boundary conditions

All test scenarios use deterministic, public Unicode behavior. The implementation should follow Unicode Standard Annex #11 (East Asian Width) and related standards for character width classification.
