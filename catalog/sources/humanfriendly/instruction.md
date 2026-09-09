# Humanfriendly Package

Build a Python package `humanfriendly` (version 10.0) that provides human-friendly input and output for text interfaces.

## Project Description

The `humanfriendly` package provides functions to format and parse human-readable representations of file sizes, time spans, numbers, and lengths. It helps create more user-friendly command-line interfaces and text output by converting between machine values and human-readable strings.

## Supports

- Python 3.12
- No runtime dependencies required
- Standard library only

## Natural Language Instruction

Implement a Python library that converts between machine-readable values and human-friendly text representations:

1. **File Size Formatting and Parsing**
   - Format byte counts as human-readable file sizes (bytes, KB, MB, GB, TB, etc.)
   - Support both decimal (base-10) and binary (base-2) multiples
   - Parse human-readable size strings back to byte counts
   - Raise `InvalidSize` exception for invalid size strings

2. **Timespan Formatting and Parsing**
   - Format seconds as human-readable time spans (seconds, minutes, hours, days, weeks)
   - Support detailed mode with multiple units
   - Support limiting the number of units displayed
   - Parse human-readable timespan strings back to seconds
   - Support abbreviations (s, m, h, d, w)
   - Raise `InvalidTimespan` exception for invalid timespan strings

3. **Number Formatting**
   - Format numbers with thousands separators (commas)
   - Support configurable decimal places
   - Handle both integers and floating-point numbers

4. **Length Formatting and Parsing**
   - Format lengths in metres to human-readable strings (mm, cm, m, km)
   - Parse human-readable length strings back to metres
   - Raise `InvalidLength` exception for invalid length strings

5. **Text Utilities**
   - Pluralize words based on counts
   - Concatenate lists with proper English grammar
   - Coerce values to boolean with support for common string representations
   - Round numbers to appropriate precision

6. **Table Formatting**
   - Format 2D lists as pretty-printed tables with borders

## Environment Configuration

- Python version: 3.12
- Package manager: pip
- Installation method: `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- No external dependencies required

## Project Directory Structure

```
workspace/
├── humanfriendly/
│   ├── __init__.py          # Main module with core functions
│   ├── text.py              # Text utilities (pluralize, concatenate)
│   └── tables.py            # Table formatting
└── setup.py                 # Package setup script
```

## API Usage Guide

### File Size Functions

**`format_size(num_bytes, keep_width=False, binary=False)`**

Format a byte count as a human-readable file size.

- **Parameters:**
  - `num_bytes` (int): The size to format in bytes
  - `keep_width` (bool): If True, trailing zeros are not stripped (default: False)
  - `binary` (bool): If True, use binary multiples (base-2), otherwise use decimal (base-10) (default: False)
- **Returns:** str - The formatted file size (e.g., "1 KB", "1.5 GB", "1 KiB")
- **Examples:**
  - `format_size(0)` → `"0 bytes"`
  - `format_size(1)` → `"1 byte"`
  - `format_size(1000)` → `"1 KB"`
  - `format_size(1024, binary=True)` → `"1 KiB"`
  - `format_size(1500, keep_width=True)` → `"1.50 KB"`

**`parse_size(size, binary=False)`**

Parse a human-readable data size string and return the number of bytes.

- **Parameters:**
  - `size` (str): The size string to parse (e.g., "5 KB", "1.5 GB")
  - `binary` (bool): If True, interpret as binary multiples (default: False)
- **Returns:** int - The size in bytes
- **Raises:** `InvalidSize` - If the size string cannot be parsed
- **Examples:**
  - `parse_size("1 KB")` → `1000`
  - `parse_size("1 KiB", binary=True)` → `1024`
  - `parse_size("1.5 MB")` → `1500000`

### Timespan Functions

**`format_timespan(num_seconds, detailed=False, max_units=3)`**

Format a number of seconds as a human-readable timespan.

- **Parameters:**
  - `num_seconds` (float): The time to format in seconds
  - `detailed` (bool): If True, include all non-zero units (default: False)
  - `max_units` (int): Maximum number of units to display (default: 3)
- **Returns:** str - The formatted timespan (e.g., "1 hour", "1 hour and 30 minutes")
- **Examples:**
  - `format_timespan(60)` → `"1 minute"`
  - `format_timespan(3600)` → `"1 hour"`
  - `format_timespan(90)` → `"1 minute and 30 seconds"`
  - `format_timespan(3661)` → `"1 hour, 1 minute and 1 second"`
  - `format_timespan(90061, max_units=2)` → `"1 day and 1 hour"`

**`parse_timespan(timespan)`**

Parse a human-readable timespan string and return the number of seconds.

- **Parameters:**
  - `timespan` (str): The timespan string to parse (e.g., "5 minutes", "1h", "1 hour and 30 minutes")
- **Returns:** float - The timespan in seconds
- **Raises:** `InvalidTimespan` - If the timespan string cannot be parsed
- **Examples:**
  - `parse_timespan("1 hour")` → `3600.0`
  - `parse_timespan("5 minutes")` → `300.0`
  - `parse_timespan("5m")` → `300.0`
  - `parse_timespan("1 hour and 30 minutes")` → `5400.0`

### Number Functions

**`format_number(number, num_decimals=2)`**

Format a number with thousands separators.

- **Parameters:**
  - `number` (float): The number to format
  - `num_decimals` (int): Number of decimal places (default: 2)
- **Returns:** str - The formatted number with commas (e.g., "1,234", "1,234.56")
- **Examples:**
  - `format_number(1234)` → `"1,234"`
  - `format_number(1234567)` → `"1,234,567"`
  - `format_number(1234.56)` → `"1,234.56"`

**`round_number(count, keep_width=False)`**

Round a number to an appropriate precision for display.

- **Parameters:**
  - `count` (float): The number to round
  - `keep_width` (bool): If True, trailing zeros are not stripped (default: False)
- **Returns:** str - The rounded number as a string
- **Examples:**
  - `round_number(1234)` → `"1234"`
  - `round_number(1234.56)` → `"1234.56"`
  - `round_number(0.1234)` → `"0.12"`
  - `round_number(1.5, keep_width=True)` → `"1.50"`

### Length Functions

**`format_length(num_metres, keep_width=False)`**

Format a length in metres as a human-readable string.

- **Parameters:**
  - `num_metres` (float): The length in metres
  - `keep_width` (bool): If True, trailing zeros are not stripped (default: False)
- **Returns:** str - The formatted length (e.g., "1 metre", "5 km", "50 cm")
- **Examples:**
  - `format_length(0)` → `"0 metres"`
  - `format_length(1)` → `"1 metre"`
  - `format_length(0.5)` → `"50 cm"`
  - `format_length(1000)` → `"1 km"`

**`parse_length(length)`**

Parse a human-readable length string and return the value in metres.

- **Parameters:**
  - `length` (str): The length string to parse (e.g., "5 km", "100 cm")
- **Returns:** float - The length in metres
- **Raises:** `InvalidLength` - If the length string cannot be parsed
- **Examples:**
  - `parse_length("1 metre")` → `1.0`
  - `parse_length("5 km")` → `5000.0`
  - `parse_length("100 cm")` → `1.0`

### Text Utilities (humanfriendly.text module)

**`pluralize(count, singular, plural=None)`**

Pluralize a word based on a count.

- **Parameters:**
  - `count` (float): The count to determine singular or plural
  - `singular` (str): The singular form of the word
  - `plural` (str, optional): The plural form (default: add "s" to singular)
- **Returns:** str - The count followed by the appropriate word form
- **Examples:**
  - `pluralize(1, 'item')` → `"1 item"`
  - `pluralize(2, 'item')` → `"2 items"`
  - `pluralize(2, 'box', 'boxes')` → `"2 boxes"`

**`concatenate(items)`**

Concatenate a list of items with proper English grammar.

- **Parameters:**
  - `items` (list): The items to concatenate
- **Returns:** str - The grammatically correct concatenation
- **Examples:**
  - `concatenate([])` → `""`
  - `concatenate(['apple'])` → `"apple"`
  - `concatenate(['apple', 'banana'])` → `"apple and banana"`
  - `concatenate(['apple', 'banana', 'cherry'])` → `"apple, banana and cherry"`

### Boolean Coercion

**`coerce_boolean(value)`**

Coerce any value to a boolean.

- **Parameters:**
  - `value`: Any Python value. For strings, specific values are recognized:
    - True values: "1", "yes", "true", "on" (case-insensitive)
    - False values: "0", "no", "false", "off", "" (case-insensitive)
- **Returns:** bool - The coerced boolean value
- **Raises:** `ValueError` - If a string cannot be coerced with certainty
- **Examples:**
  - `coerce_boolean('yes')` → `True`
  - `coerce_boolean('no')` → `False`
  - `coerce_boolean(1)` → `True`
  - `coerce_boolean('')` → `False`

### Table Formatting (humanfriendly.tables module)

**`format_table(data)` or `format_pretty_table(data)`**

Format a 2D list as a pretty-printed table with borders.

- **Parameters:**
  - `data` (list): A 2D list representing table rows
- **Returns:** str - The formatted table with borders
- **Examples:**
  ```python
  format_table([['Name', 'Age'], ['Alice', '30'], ['Bob', '25']])
  # Returns:
  # ---------------
  # | Name  | Age |
  # | Alice | 30  |
  # | Bob   | 25  |
  # ---------------
  ```

### Exception Classes

**`InvalidSize`** - Exception raised when a size string cannot be parsed

**`InvalidTimespan`** - Exception raised when a timespan string cannot be parsed

**`InvalidLength`** - Exception raised when a length string cannot be parsed

## Implementation Notes

1. **Size Units**: Support both decimal (KB, MB, GB) and binary (KiB, MiB, GiB) units
   - Decimal: powers of 1000 (1 KB = 1000 bytes)
   - Binary: powers of 1024 (1 KiB = 1024 bytes)

2. **Timespan Units**: Support nanoseconds, microseconds, milliseconds, seconds, minutes, hours, days, weeks, years
   - Accept both full names and abbreviations
   - Handle compound timespans (e.g., "1 hour and 30 minutes")

3. **Number Formatting**: Use commas as thousands separators
   - Round appropriately based on magnitude
   - Handle both integers and floats

4. **Length Units**: Support nm, mm, cm, m, km
   - Automatically choose appropriate unit for display
   - Convert all units to/from metres

5. **Pluralization**: Count of 1 (or 1.0) should use singular form, all others use plural

6. **Boolean Coercion**: Handle common string representations case-insensitively with whitespace trimming

7. **Package Structure**: Organize functions into appropriate modules
   - Main functions in `humanfriendly/__init__.py`
   - Text utilities in `humanfriendly/text.py`
   - Table formatting in `humanfriendly/tables.py`

8. **Setup Script**: Create a standard setuptools setup.py with package metadata
