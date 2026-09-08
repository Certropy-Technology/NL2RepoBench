# wcmatch: Wildcard Match Library

## Project Description

wcmatch is a Python library that provides enhanced wildcard and glob pattern matching capabilities. It extends the functionality of Python's standard `fnmatch` and `glob` modules by adding support for advanced features found in Bash globbing, such as brace expansion, extended glob patterns, case-insensitive matching, and more. The library also provides a `pathlib`-compatible interface for pattern matching.

The library is designed for applications that need file system pattern matching, filtering, and searching with more expressive patterns than the standard library provides. It operates without requiring network access and can work purely with string patterns and paths.

## Natural Language Instruction

You are tasked with implementing the `wcmatch` package (version 11.0.1), a wildcard and glob pattern matching library for Python. The package must be installable via pip and provide the following capabilities:

1. **fnmatch module**: Enhanced filename pattern matching with support for wildcards (`*`, `?`, `[...]`), extended glob patterns (`+(...)`, `*(...)`, `?(...)`, `@(...)`, `!(...)`), brace expansion (`{a,b}`), case-insensitive matching, negation patterns, and pattern splitting.

2. **glob module**: Path-based glob matching with support for recursive patterns (`**`), directory separators, and all fnmatch features adapted for path matching.

3. **pathlib integration**: A `Path` class that extends Python's pathlib with wcmatch pattern matching capabilities.

4. **Pattern compilation**: Support for compiling patterns into reusable matcher objects for improved performance.

5. **Utility functions**: Pattern translation to regex, escaping special characters, detecting magic patterns, and filtering collections.

The package name is `wcmatch`, the import package name is `wcmatch`, and it should be installable using `python -m pip install --no-build-isolation --no-deps --no-index -e .` from the workspace root.

Core modules that must be implemented:
- `wcmatch.fnmatch`: Filename pattern matching
- `wcmatch.glob`: Glob pattern matching for paths
- `wcmatch.pathlib`: Pathlib integration with pattern matching

The library must work without network access during runtime.

## Supports (Environment Configuration)

- **Language**: Python 3.12
- **Package Manager**: pip
- **Build System**: hatchling (via pyproject.toml)
- **Installation Command**: `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- **Runtime Dependencies**: `bracex>=3.0` (brace expansion library)
- **Network Access**: No network access during agent execution, candidate installation, or verification
- **Operating System**: Debian 12 (amd64)

## Project Directory Structure

```
workspace/
├── wcmatch/
│   ├── __init__.py          # Package initialization, exports __version__
│   ├── __meta__.py          # Version metadata
│   ├── fnmatch.py           # Filename pattern matching module
│   ├── glob.py              # Glob pattern matching module
│   ├── pathlib.py           # Pathlib integration
│   ├── _wcparse.py          # Pattern parsing internals
│   ├── _wcmatch.py          # Matcher base classes
│   ├── util.py              # Utility functions
│   └── posix.py             # POSIX character classes support (optional)
├── pyproject.toml           # Build configuration with hatchling backend
└── README.md                # Package documentation (optional)
```

## API Usage Guide

### wcmatch.fnmatch Module

The `fnmatch` module provides enhanced filename pattern matching.

#### Functions

**fnmatch(name, pattern, *, flags=0) -> bool**

Match a filename against a pattern.

- `name` (str): The filename to match
- `pattern` (str | list[str]): The pattern(s) to match against
- `flags` (int): Optional flags to modify matching behavior
- Returns: `True` if the name matches the pattern, `False` otherwise

Example:
```python
import wcmatch.fnmatch as fnm
fnm.fnmatch('test.txt', '*.txt')  # True
fnm.fnmatch('test.py', '*.txt')   # False
```

**filter(names, pattern, *, flags=0) -> list**

Filter a list of filenames by a pattern.

- `names` (list[str]): List of filenames to filter
- `pattern` (str | list[str]): The pattern(s) to match against
- `flags` (int): Optional flags
- Returns: List of names that match the pattern

Example:
```python
fnm.filter(['a.txt', 'b.py', 'c.txt'], '*.txt')  # ['a.txt', 'c.txt']
```

**translate(pattern, *, flags=0) -> tuple**

Translate a wildcard pattern to a regular expression.

- `pattern` (str): The wildcard pattern
- `flags` (int): Optional flags
- Returns: Tuple of (list of regex patterns, list of flags)

Example:
```python
patterns, _ = fnm.translate('*.txt')
# patterns is a list containing compiled regex pattern strings
```

**compile(pattern, *, flags=0) -> WcMatcher**

Compile a pattern into a reusable matcher object.

- `pattern` (str | list[str]): The pattern(s) to compile
- `flags` (int): Optional flags
- Returns: WcMatcher object with `match()` and `filter()` methods

Example:
```python
matcher = fnm.compile('*.txt')
matcher.match('test.txt')  # True
matcher.filter(['a.txt', 'b.py'])  # ['a.txt']
```

**escape(pattern) -> str**

Escape special characters in a pattern to match them literally.

- `pattern` (str): Pattern to escape
- Returns: Escaped pattern string

Example:
```python
fnm.escape('*.txt')  # Returns pattern that matches literal '*.txt'
```

**is_magic(pattern, *, flags=0) -> bool**

Check if a pattern contains magic characters.

- `pattern` (str): Pattern to check
- `flags` (int): Optional flags
- Returns: `True` if pattern contains wildcards, `False` otherwise

Example:
```python
fnm.is_magic('*.txt')     # True
fnm.is_magic('file.txt')  # False
```

#### Flags

The following flags modify pattern matching behavior:

- `IGNORECASE` (I): Case-insensitive matching
- `EXTMATCH` (E): Enable extended glob patterns: `+(...)`, `*(...)`, `?(...)`, `@(...)`, `!(...)`
- `BRACE` (B): Enable brace expansion: `{a,b,c}`, `{1..9}`
- `DOTMATCH` (D): Allow `*` and `?` to match leading dots
- `NEGATE` (N): Enable negation patterns with `!pattern`
- `NEGATEALL` (A): Negation patterns match against all files (assumes `*` inclusion)
- `SPLIT` (S): Split patterns on `|` character
- `RAWCHARS` (R): Treat backslashes as literal characters
- `CASE` (C): Force case-sensitive matching (overrides IGNORECASE)
- `FORCEUNIX` (U): Force Unix-style path separators
- `FORCEWIN` (W): Force Windows-style path separators
- `MINUSNEGATE` (M): Use `-` instead of `!` for negation

Flags can be combined with bitwise OR: `fnm.IGNORECASE | fnm.BRACE`

#### WcMatcher Class

Compiled matcher object returned by `compile()`.

Methods:
- `match(name) -> bool`: Match a single name
- `filter(names) -> list`: Filter a list of names

### wcmatch.glob Module

The `glob` module provides path-based glob pattern matching.

#### Functions

**globmatch(path, pattern, *, flags=0) -> bool**

Match a path against a glob pattern.

- `path` (str): The path to match
- `pattern` (str | list[str]): The glob pattern(s)
- `flags` (int): Optional flags
- Returns: `True` if the path matches, `False` otherwise

Example:
```python
import wcmatch.glob as glob
glob.globmatch('dir/file.txt', 'dir/*.txt')  # True
glob.globmatch('a/b/c/file.txt', '**/file.txt', flags=glob.GLOBSTAR)  # True
```

**globfilter(paths, pattern, *, flags=0) -> list**

Filter a list of paths by a glob pattern.

- `paths` (list[str]): List of paths to filter
- `pattern` (str | list[str]): The glob pattern(s)
- `flags` (int): Optional flags
- Returns: List of paths that match the pattern

Example:
```python
glob.globfilter(['a/b.txt', 'c/d.py'], '*/*.txt')  # ['a/b.txt']
```

**translate(pattern, *, flags=0) -> tuple**

Translate a glob pattern to a regular expression.

- `pattern` (str): The glob pattern
- `flags` (int): Optional flags
- Returns: Tuple of (list of regex patterns, list of flags)

**compile(pattern, *, flags=0) -> WcMatcher**

Compile a glob pattern into a reusable matcher.

- `pattern` (str | list[str]): The pattern(s) to compile
- `flags` (int): Optional flags
- Returns: WcMatcher object with `match()` and `filter()` methods

**escape(pattern, unix=None) -> str**

Escape special characters in a glob pattern.

- `pattern` (str): Pattern to escape
- `unix` (bool | None): Force Unix or Windows escaping
- Returns: Escaped pattern string

**is_magic(pattern, *, flags=0) -> bool**

Check if a glob pattern contains magic characters.

- `pattern` (str): Pattern to check
- `flags` (int): Optional flags
- Returns: `True` if pattern contains wildcards, `False` otherwise

#### Flags

The glob module supports the same flags as fnmatch, plus:

- `GLOBSTAR`: Enable `**` for recursive directory matching

Without `GLOBSTAR`, `**` is treated as `*`.

### wcmatch.pathlib Module

The `pathlib` module provides a `Path` class with pattern matching support.

#### Path Class

A subclass of `pathlib.PurePath` with wcmatch pattern matching.

**Path(path)**

Create a Path object.

- `path` (str): The path string

**match(pattern, *, flags=0) -> bool**

Match the path against a pattern.

- `pattern` (str): The pattern to match
- `flags` (int): Optional flags (same as glob module)
- Returns: `True` if the path matches, `False` otherwise

Example:
```python
import wcmatch.pathlib as wcp
p = wcp.Path('file.txt')
p.match('*.txt')  # True
p.match('*.py')   # False
```

#### Flags

The pathlib module supports the same flags as the glob module, including:
- `IGNORECASE`
- `EXTMATCH`
- `BRACE`
- `GLOBSTAR`

## Implementation Notes

### Pattern Syntax

**Basic Wildcards:**
- `*`: Matches any sequence of characters (excluding `/` in glob patterns)
- `?`: Matches exactly one character
- `[abc]`: Character class, matches any character in the set
- `[a-z]`: Character range
- `[!abc]`: Negated character class, matches any character NOT in the set

**Extended Patterns (with EXTMATCH flag):**
- `+(pattern)`: Matches one or more occurrences
- `*(pattern)`: Matches zero or more occurrences
- `?(pattern)`: Matches zero or one occurrence
- `@(pattern)`: Matches exactly one occurrence
- `!(pattern)`: Matches anything except the pattern
- Pattern lists use `|` as separator: `@(a|b|c)`

**Brace Expansion (with BRACE flag):**
- `{a,b,c}`: Expands to multiple patterns: `a`, `b`, `c`
- `{1..9}`: Numeric range expansion
- Can be nested: `{a,b}{1,2}` expands to `a1`, `a2`, `b1`, `b2`

**Negation (with NEGATE flag):**
- `!pattern`: Excludes matches of the pattern
- Must be combined with inclusion patterns or NEGATEALL flag
- Example: `['*.txt', '!avoid.txt']` matches all .txt files except avoid.txt

### Path Handling

- Glob patterns treat `/` as a path separator (normalized on Windows to match both `/` and `\`)
- `**` requires the `GLOBSTAR` flag to match across multiple directory levels
- Without GLOBSTAR, `**` behaves like `*`
- Leading dots (hidden files) are not matched by `*`, `?`, or `[]` unless `DOTMATCH` flag is set

### Case Sensitivity

- By default, matching is case-sensitive on case-sensitive file systems
- Use `IGNORECASE` flag for case-insensitive matching
- `CASE` flag can override and force case-sensitive matching

### Pattern List Handling

Functions accept patterns as:
- Single string: `'*.txt'`
- List of strings: `['*.txt', '*.py']`
- Pipe-separated string with SPLIT flag: `'*.txt|*.py'` with `fnm.SPLIT`

### Version Information

The package must export `__version__` from the `wcmatch` module:
```python
import wcmatch
print(wcmatch.__version__)  # Should print '11.0.1'
```

### Build Configuration

The `pyproject.toml` must specify:
- Build backend: `hatchling`
- Package name: `wcmatch`
- Version: `11.0.1`
- Dependency: `bracex>=3.0`

Example minimal `pyproject.toml`:
```toml
[build-system]
requires = ["hatchling>=0.21.1"]
build-backend = "hatchling.build"

[project]
name = "wcmatch"
version = "11.0.1"
dependencies = ["bracex>=3.0"]
```

### Determinism and Behavior

- Pattern matching must be deterministic for the same inputs
- Empty pattern `''` matches only empty string `''`
- Empty list input to filter functions returns empty list
- Compiled matchers should maintain state and be reusable
- `translate()` returns a tuple: (list of regex pattern strings, list of flags)

## Examples

### Basic Filename Matching

```python
import wcmatch.fnmatch as fnm

# Simple wildcard matching
fnm.fnmatch('readme.txt', '*.txt')      # True
fnm.fnmatch('readme.md', '*.txt')       # False

# Question mark matches single character
fnm.fnmatch('file1.txt', 'file?.txt')   # True
fnm.fnmatch('file10.txt', 'file?.txt')  # False

# Character classes
fnm.fnmatch('file5.txt', 'file[0-9].txt')   # True
fnm.fnmatch('fileA.txt', 'file[A-Z].txt')   # True
```

### Case-Insensitive Matching

```python
# Case-sensitive by default
fnm.fnmatch('FILE.TXT', 'file.txt')                      # False

# Case-insensitive with flag
fnm.fnmatch('FILE.TXT', 'file.txt', flags=fnm.IGNORECASE)  # True
```

### Extended Patterns

```python
# Extended glob patterns require EXTMATCH flag
fnm.fnmatch('test.txt', '+(test).txt', flags=fnm.EXTMATCH)  # True
fnm.fnmatch('', '*(test)', flags=fnm.EXTMATCH)              # True (zero occurrences)
fnm.fnmatch('test', '@(test|other)', flags=fnm.EXTMATCH)    # True (one of alternatives)
fnm.fnmatch('other', '!(test)', flags=fnm.EXTMATCH)         # True (not test)
```

### Brace Expansion

```python
# Brace expansion creates multiple patterns
fnm.fnmatch('file1.txt', 'file{1,2,3}.txt', flags=fnm.BRACE)  # True
fnm.fnmatch('file4.txt', 'file{1,2,3}.txt', flags=fnm.BRACE)  # False

# Numeric ranges
fnm.fnmatch('file5.txt', 'file{1..9}.txt', flags=fnm.BRACE)   # True
```

### Glob Path Matching

```python
import wcmatch.glob as glob

# Path matching with directory separators
glob.globmatch('src/main.py', 'src/*.py')           # True
glob.globmatch('src/lib/util.py', 'src/*.py')       # False

# Recursive matching requires GLOBSTAR flag
glob.globmatch('a/b/c/file.txt', '**/file.txt', flags=glob.GLOBSTAR)  # True
glob.globmatch('a/b/c/file.txt', '**/file.txt')                       # False (no GLOBSTAR)
```

### Filtering Collections

```python
files = ['readme.txt', 'main.py', 'test.py', 'notes.txt']

# Filter by pattern
fnm.filter(files, '*.txt')      # ['readme.txt', 'notes.txt']
fnm.filter(files, '*.py')       # ['main.py', 'test.py']

# Empty result if no matches
fnm.filter(files, '*.md')       # []
```

### Pattern Compilation

```python
# Compile pattern for reuse
matcher = fnm.compile('*.txt')

# Use compiled matcher
matcher.match('file.txt')                   # True
matcher.match('file.py')                    # False
matcher.filter(['a.txt', 'b.py', 'c.txt'])  # ['a.txt', 'c.txt']
```

### Pathlib Integration

```python
import wcmatch.pathlib as wcp

p = wcp.Path('documents/report.txt')
p.match('**/*.txt', flags=wcp.GLOBSTAR)     # True
p.match('*.py')                             # False

# With flags
p2 = wcp.Path('FILE.TXT')
p2.match('*.txt', flags=wcp.IGNORECASE)     # True
```

## Error Handling and Boundary Conditions

### Empty Inputs

- Empty string `''` with empty pattern `''` matches: `fnmatch('', '') -> True`
- Empty string with non-empty pattern does not match: `fnmatch('', 'test') -> False`
- Empty pattern list: An empty list of patterns should match nothing
- Empty input list: `filter([], pattern)` returns `[]`

### Special Characters

- Use `escape()` to match literal special characters:
  ```python
  fnm.fnmatch('*.txt', fnm.escape('*.txt'))  # True (matches literal '*.txt')
  fnm.fnmatch('file.txt', fnm.escape('*.txt'))  # False
  ```

### Unicode Support

- Patterns and filenames should support Unicode characters:
  ```python
  fnm.fnmatch('文件.txt', '*.txt')  # True
  glob.globmatch('文档/文件.txt', '*/文件.txt')  # True
  ```

### Hidden Files (Dotfiles)

- By default, wildcards do not match leading dots:
  ```python
  fnm.fnmatch('.hidden', '*')                        # False
  fnm.fnmatch('.hidden', '*', flags=fnm.DOTMATCH)    # True
  ```

### Multiple Flag Combinations

- Flags can be combined with bitwise OR:
  ```python
  flags = fnm.IGNORECASE | fnm.BRACE
  fnm.fnmatch('FILE1', '{file,test}{1,2}', flags=flags)  # True
  ```

### Invalid Patterns

- Invalid brace syntax or unmatched brackets should be handled gracefully
- Pattern matching should not raise exceptions for malformed patterns (treat as literals or fail to match)

## Security Considerations

- Pattern matching operates on strings and does not access the file system directly
- No network access is required or should be performed
- Regular expression DoS (ReDoS) risk exists with complex nested patterns—avoid extremely deep nesting
- All operations should complete within reasonable time bounds

## Testing and Validation

The implementation will be validated against 90 test scenarios covering:

1. Basic wildcard matching (`*`, `?`, `[...]`)
2. Flag combinations (IGNORECASE, EXTMATCH, BRACE, GLOBSTAR, etc.)
3. Extended glob patterns (`+()`, `*()`, `?()`, `@()`, `!()`)
4. Brace expansion and ranges
5. Path separators and recursive matching
6. Case sensitivity variations
7. Filter and compile functionality
8. Pathlib integration
9. Escape and is_magic utilities
10. Edge cases (empty inputs, Unicode, negation patterns)

The verifier will test scenarios without filesystem access, using string-based pattern matching only.
