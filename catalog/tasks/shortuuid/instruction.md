# Project Description

`shortuuid` is a Python library that generates concise, unambiguous, URL-safe UUIDs. It addresses the need for non-sequential IDs that are short, easy to use, and avoid ambiguous characters. The library generates UUIDs using Python's built-in `uuid` module and translates them to base57 using a carefully selected alphabet that excludes similar-looking characters (l, 1, I, O, 0).

The library provides both module-level convenience functions and a class-based API for thread-local alphabet customization. It supports standard UUID generation, namespace-based UUID5 generation, cryptographically secure random strings, and bidirectional encoding/decoding of standard UUIDs.

# Natural Language Instruction

Implement a Python package named `shortuuid` that provides concise, URL-safe UUID generation and encoding capabilities. The package must:

1. Generate short UUIDs using a base57 alphabet (default: `23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`)
2. Support both random UUID4 generation and namespace-based UUID5 generation
3. Provide bidirectional encoding/decoding between standard UUIDs and short string representations
4. Allow custom alphabet configuration with automatic sorting and deduplication
5. Generate cryptographically secure random strings
6. Support both module-level convenience functions and class-based per-instance alphabet management
7. Provide a command-line interface for UUID generation and encoding/decoding operations
8. Include proper packaging with `pyproject.toml` for Poetry-based builds

The package name is `shortuuid`, the import name is `shortuuid`, and it must be installable via pip/Poetry with entry point `shortuuid` for the CLI.

# Supports (Environment Configuration)

- Python: 3.6+
- Package Manager: pip (Poetry build backend)
- Build System: `poetry-core`
- Runtime Dependencies: None (uses only Python standard library: uuid, math, secrets)
- Installation: `pip install .` or `poetry install`
- Testing: pytest
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── pyproject.toml
├── shortuuid/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   └── py.typed
```

# API Usage Guide

## Module: `shortuuid`

The root module exports convenience functions that use a global `ShortUUID` instance:

### `uuid(name=None, pad_length=None) -> str`

Generate and return a short UUID string.

- **Parameters:**
  - `name` (Optional[str]): If provided and starts with "http://" or "https://", generates UUID5 with NAMESPACE_URL. Otherwise uses NAMESPACE_DNS. If None, generates random UUID4.
  - `pad_length` (Optional[int]): Padding length for the output string. Defaults to the minimum length needed for the current alphabet.
- **Returns:** Short UUID string (typically 22 characters with default alphabet)
- **Example:**
  ```python
  import shortuuid
  shortuuid.uuid()  # Random: 'vytxeTZskVKR7C7WgdSP3d'
  shortuuid.uuid(name="example.com")  # Deterministic
  shortuuid.uuid(name="http://example.com")  # Uses URL namespace
  ```

### `encode(uuid, pad_length=None) -> str`

Encode a standard UUID object into a short string.

- **Parameters:**
  - `uuid` (uuid.UUID): A UUID object to encode
  - `pad_length` (Optional[int]): Padding length. Defaults to alphabet-specific minimum.
- **Returns:** Short string representation
- **Raises:** `ValueError` if input is not a UUID object
- **Example:**
  ```python
  import uuid, shortuuid
  u = uuid.UUID('3b1f8b40-222c-4a6e-b77e-779d5a94e21c')
  s = shortuuid.encode(u)  # 'CXc85b4rqinB7s5J52TRYb'
  ```

### `decode(string, legacy=False) -> uuid.UUID`

Decode a short string into a standard UUID object.

- **Parameters:**
  - `string` (str): Short UUID string to decode
  - `legacy` (bool): Set to True for strings encoded with ShortUUID < 1.0.0 (MSB-last format)
- **Returns:** uuid.UUID object
- **Raises:** 
  - `ValueError` if input is not a string
  - `ValueError` if string contains illegal characters or is too long
- **Example:**
  ```python
  import shortuuid
  u = shortuuid.decode('CXc85b4rqinB7s5J52TRYb')
  # UUID('3b1f8b40-222c-4a6e-b77e-779d5a94e21c')
  ```

### `random(length=None) -> str`

Generate a cryptographically secure random string.

- **Parameters:**
  - `length` (Optional[int]): Length of the random string. Defaults to 22 for default alphabet.
- **Returns:** Random string using current alphabet
- **Security:** Uses `secrets.choice()` internally (cryptographically secure)
- **Example:**
  ```python
  import shortuuid
  shortuuid.random()  # 'RaF56o2r58hTKT7AYS9doj'
  shortuuid.random(length=10)  # 10 characters
  ```

### `get_alphabet() -> str`

Return the current alphabet used for UUID generation.

- **Returns:** String containing all alphabet characters in sorted order
- **Example:**
  ```python
  import shortuuid
  shortuuid.get_alphabet()
  # '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
  ```

### `set_alphabet(alphabet) -> None`

Set the alphabet to be used for new UUID operations.

- **Parameters:**
  - `alphabet` (str): String containing desired alphabet characters
- **Behavior:** 
  - Automatically sorts characters and removes duplicates
  - Requires at least 2 unique characters
- **Raises:** `ValueError` if alphabet has only 1 or 0 unique characters
- **Side Effect:** Modifies global alphabet state for all subsequent operations
- **Example:**
  ```python
  import shortuuid
  shortuuid.set_alphabet("0123456789")
  shortuuid.get_alphabet()  # '0123456789' (sorted, deduped)
  ```

## Class: `ShortUUID`

Thread-safe class for managing UUID operations with custom alphabets.

### `__init__(alphabet=None)`

Create a new ShortUUID instance with its own alphabet.

- **Parameters:**
  - `alphabet` (Optional[str]): Custom alphabet string. Defaults to standard base57 alphabet.
- **Raises:** `ValueError` if provided alphabet has fewer than 2 unique characters
- **Example:**
  ```python
  from shortuuid import ShortUUID
  su = ShortUUID()
  su_binary = ShortUUID(alphabet="01")
  ```

### Instance Methods

All instance methods mirror the module-level functions but operate on the instance's alphabet:

- `uuid(name=None, pad_length=None) -> str`
- `encode(uuid, pad_length=None) -> str`
- `decode(string, legacy=False) -> uuid.UUID`
- `random(length=None) -> str`
- `get_alphabet() -> str`
- `set_alphabet(alphabet) -> None`

### `encoded_length(num_bytes=16) -> int`

Calculate the string length for a given number of bytes using the current alphabet.

- **Parameters:**
  - `num_bytes` (int): Number of bytes to encode (default 16 for standard UUID)
- **Returns:** Integer length of the encoded string
- **Example:**
  ```python
  su = ShortUUID()
  su.encoded_length()  # 22 for default alphabet
  su.encoded_length(num_bytes=8)  # 11
  ```

## Module: `shortuuid.cli`

Provides command-line interface functionality.

### `cli(args) -> None`

Main CLI entry point (normally called via `shortuuid` command).

- **Commands:**
  - `shortuuid` (no args): Generate and print a random short UUID
  - `shortuuid encode <uuid>`: Encode a standard UUID to short format
  - `shortuuid decode <short-uuid>`: Decode a short UUID to standard format
- **Example:**
  ```bash
  $ shortuuid
  fZpeF6gcskHbSpTgpQCkcJ
  $ shortuuid encode 3b1f8b40-222c-4a6e-b77e-779d5a94e21c
  CXc85b4rqinB7s5J52TRYb
  $ shortuuid decode CXc85b4rqinB7s5J52TRYb
  3b1f8b40-222c-4a6e-b77e-779d5a94e21c
  ```

# Implementation Notes

## Alphabet Management

- Default alphabet: `23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz` (57 characters)
- Excludes ambiguous characters: l, 1, I, O, 0
- Custom alphabets are automatically sorted and deduplicated
- Minimum 2 unique characters required
- The alphabet affects encoded length: smaller alphabet = longer strings

## Encoding/Decoding Algorithm

- UUIDs (128-bit integers) are encoded using positional numeral system with the alphabet as the base
- Most significant digit appears first in the output string
- Padding ensures consistent length regardless of UUID value (prevents leading zeros from disappearing)
- Default padding length is calculated from alphabet size: `ceil(log(2^128) / log(len(alphabet)))`

## Determinism and Consistency

- Same UUID always encodes to the same short string (for given alphabet)
- Same short string always decodes to the same UUID (for given alphabet)
- Namespace-based UUID5 generation is deterministic: same name always produces same UUID
- Random UUID4 generation and `random()` are non-deterministic but cryptographically secure

## Padding Behavior

- `encode()` with `pad_length=None` uses alphabet-specific default (typically 22)
- Padding fills with the first character of the alphabet (index 0)
- Consistent padding ensures all encoded UUIDs have the same length
- Small UUID values (e.g., UUID(int=0)) still produce full-length strings

## Legacy Compatibility

- ShortUUID < 1.0.0 stored UUIDs with MSB last (reversed)
- Use `decode(string, legacy=True)` to decode old-format strings
- New encoding always uses MSB-first format
- Migration: `new_str = encode(decode(old_str, legacy=True))`

## Type Validation

- `encode()` requires `uuid.UUID` object, not string
- `decode()` requires string input
- Passing wrong types (int, float, list, dict, tuple) raises `ValueError`
- Decoding illegal characters raises `ValueError`

## UUID Generation Namespace Selection

- `name=None`: Random UUID4
- `name` starting with `http://` or `https://` (case-insensitive): UUID5 with `uuid.NAMESPACE_URL`
- Any other `name`: UUID5 with `uuid.NAMESPACE_DNS`
- UUID5 is deterministic and reproducible

## Thread Safety

- Module-level functions share a global `ShortUUID` instance
- Not thread-safe if mixing `set_alphabet()` calls with encoding/decoding
- Use separate `ShortUUID()` instances for thread-local alphabets

# Examples

## Basic Usage

```python
import shortuuid

# Generate random short UUID
short_id = shortuuid.uuid()
print(short_id)  # e.g., 'vytxeTZskVKR7C7WgdSP3d'

# Encode existing UUID
import uuid
u = uuid.uuid4()
short = shortuuid.encode(u)
assert shortuuid.decode(short) == u
```

## Namespace-Based UUIDs

```python
import shortuuid

# DNS namespace
id1 = shortuuid.uuid(name="example.com")
id2 = shortuuid.uuid(name="example.com")
assert id1 == id2  # Deterministic

# URL namespace
id3 = shortuuid.uuid(name="http://example.com")
id4 = shortuuid.uuid(name="https://example.com")
assert id3 != id4  # Different URLs produce different UUIDs
```

## Custom Alphabet

```python
import shortuuid

# Binary alphabet
shortuuid.set_alphabet("01")
binary_uuid = shortuuid.uuid()
print(len(binary_uuid))  # ~128 characters
assert set(binary_uuid) == {'0', '1'}

# Hexadecimal alphabet
shortuuid.set_alphabet("0123456789abcdef")
hex_uuid = shortuuid.uuid()
print(len(hex_uuid))  # 32 characters
```

## Class-Based Usage

```python
from shortuuid import ShortUUID

# Separate instances with different alphabets
su_default = ShortUUID()
su_binary = ShortUUID(alphabet="01")

uuid1 = su_default.uuid()  # ~22 chars
uuid2 = su_binary.uuid()   # ~128 chars

# No interference between instances
assert su_default.get_alphabet() != su_binary.get_alphabet()
```

# Error Handling and Boundary Conditions

## Invalid Alphabet

```python
from shortuuid import ShortUUID

# Single character - raises ValueError
try:
    ShortUUID(alphabet="a")
except ValueError:
    print("Alphabet must have at least 2 unique characters")

# Empty alphabet - raises ValueError
try:
    ShortUUID(alphabet="")
except ValueError:
    print("Alphabet must have at least 2 unique characters")
```

## Type Errors

```python
import shortuuid

# encode() requires UUID object
try:
    shortuuid.encode("not-a-uuid")
except ValueError:
    print("Must pass uuid.UUID object")

# decode() requires string
try:
    shortuuid.decode(123)
except ValueError:
    print("Must pass string")
```

## Padding Edge Cases

```python
import uuid
import shortuuid

# Zero UUID should still produce full-length string
zero_uuid = uuid.UUID(int=0)
encoded = shortuuid.encode(zero_uuid)
assert len(encoded) == 22

# Decode should recover original
decoded = shortuuid.decode(encoded)
assert decoded == zero_uuid
```

## Legacy Decoding

```python
import shortuuid

# Old format (pre-1.0.0) had MSB last
old_format_string = "legacy-encoded-string"

# Decode with legacy flag
try:
    uuid_obj = shortuuid.decode(old_format_string, legacy=True)
    # Re-encode with new format
    new_format_string = shortuuid.encode(uuid_obj)
except ValueError:
    print("Invalid legacy format")
```

## Alphabet Deduplication

```python
import shortuuid

# Duplicates are removed, characters are sorted
shortuuid.set_alphabet("aabbccddee")
alphabet = shortuuid.get_alphabet()
assert alphabet == "abcde"
assert len(alphabet) == 5
```
