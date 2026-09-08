# Project Description

dateparser is a Python library for parsing human-readable dates and times from strings in natural language. It supports multiple languages, various date formats, and relative date expressions (e.g., "tomorrow", "3 days ago"). The library is designed to extract datetime objects from HTML pages and user input where date formats are not standardized.

The project provides a simple API centered around a `parse()` function that accepts date strings and optional configuration settings. It handles diverse formats including ISO dates, natural language expressions, locale-specific formats, and timestamps. The library does not require network access for parsing operations.

# Natural Language Instruction

Implement the **dateparser** Python package, a library for parsing dates and times from natural language strings. The package must:

1. Provide a top-level `parse()` function that accepts date strings and returns `datetime` objects
2. Support parsing of ISO dates, natural language expressions, and relative dates
3. Handle configurable settings including timezone, date order (DMY/MDY/YMD), and relative base dates
4. Support parsing timestamps (Unix epoch seconds)
5. Return `None` for unparseable input rather than raising exceptions
6. Provide a `DateDataParser` class for reusable parser instances with fixed configuration

The package name is `dateparser`, the import name is `dateparser`, and installation uses standard Python packaging (setuptools). The package must include:
- Core parsing functionality accessible via `dateparser.parse()`
- Configuration through a settings dictionary
- Support for relative date parsing with a configurable base date
- Timezone handling

# Supports

- **Language**: Python 3.12
- **Package manager**: pip
- **Installation command**: `pip install -e .` (editable mode)
- **Runtime dependencies**:
  - `python-dateutil>=2.7.0` (for date manipulation and parsing)
  - `pytz>=2024.2` (for timezone support)
  - `regex>=2024.9.11` (for pattern matching)
  - `tzlocal>=0.2` (for local timezone detection)
- **Build system**: setuptools (>=77.0)
- **Network access**: None required for parsing operations

All dependencies must be declared in `pyproject.toml`. The package runs entirely offline after installation.

# Project Directory Structure

```
workspace/
├── pyproject.toml                 # Project metadata and dependencies
├── LICENSE                        # BSD-3-Clause license
├── README.md                      # Package documentation
├── dateparser/                    # Main package directory
│   ├── __init__.py                # Package exports: parse, DateDataParser
│   ├── conf.py                    # Settings configuration
│   ├── date.py                    # DateDataParser class
│   ├── date_parser.py             # Core date parsing logic
│   ├── parser.py                  # Date format parsing utilities
│   ├── timezone_parser.py         # Timezone extraction
│   └── utils/                     # Utility modules
│       └── __init__.py
```

The package must be installable via `pip install -e .` and expose its API through `import dateparser`.

# API Usage Guide

## Main Parsing Function

### `dateparser.parse(date_string, date_formats=None, languages=None, locales=None, region=None, settings=None, detect_languages_function=None)`

Parse a date/time string and return a `datetime` object.

**Parameters**:
- `date_string` (str): The date string to parse
- `date_formats` (list, optional): List of format strings (strptime directives)
- `languages` (list, optional): List of language codes (e.g., `['en', 'es']`)
- `locales` (list, optional): List of locale codes (e.g., `['en-US', 'fr-FR']`)
- `region` (str, optional): Region code (e.g., `'US'`, `'EU'`)
- `settings` (dict, optional): Configuration dictionary (see Settings below)
- `detect_languages_function` (callable, optional): Custom language detection function

**Returns**: `datetime.datetime` object if parsing succeeds, `None` if parsing fails

**Raises**:
- `ValueError`: For invalid language codes or configuration
- `TypeError`: For invalid argument types
- `SettingValidationError`: For invalid settings values

**Behavior**:
- Returns `None` for unparseable strings (not an exception)
- Supports ISO 8601 dates: `'2024-01-15'`, `'2024-01-15T14:30:00'`
- Supports natural language: `'tomorrow'`, `'yesterday'`, `'next Monday'`
- Supports relative expressions: `'3 days ago'`, `'in 2 weeks'`
- Supports timestamps: `'1705334400'` (Unix epoch seconds)
- Default timezone is the system local timezone
- Returns `datetime` objects with timezone information when configured

**Examples**:
```python
import dateparser

# ISO date
dt = dateparser.parse('2024-01-15')  # datetime(2024, 1, 15, 0, 0)

# Natural language
dt = dateparser.parse('tomorrow')  # Returns tomorrow's date

# Relative dates require RELATIVE_BASE for deterministic behavior
from datetime import datetime
dt = dateparser.parse('tomorrow', settings={'RELATIVE_BASE': datetime(2024, 1, 15)})
# Returns datetime(2024, 1, 16, 0, 0)

# Date order configuration
dt = dateparser.parse('15/01/2024', settings={'DATE_ORDER': 'DMY'})
# Returns datetime(2024, 1, 15, 0, 0)

# Unparseable input
dt = dateparser.parse('not a date')  # Returns None
```

## DateDataParser Class

### `dateparser.DateDataParser(languages=None, locales=None, region=None, settings=None, detect_languages_function=None)`

A reusable parser instance with fixed configuration.

**Parameters**: Same as `parse()` function

**Methods**:
- `get_date_data(date_string, date_formats=None)` → dict or None
  - Returns a dictionary with keys: `'date_obj'` (datetime), `'period'` (str)
  - Returns `None` for unparseable strings

**Example**:
```python
from dateparser import DateDataParser

parser = DateDataParser(settings={'DATE_ORDER': 'DMY'})
data = parser.get_date_data('15/01/2024')
# data = {'date_obj': datetime(2024, 1, 15, 0, 0), 'period': 'day'}

dt = data['date_obj'] if data else None
```

## Settings Configuration

Settings are passed as a dictionary to control parsing behavior:

### Key Settings:

- **`DATE_ORDER`** (str): Date component order
  - Values: `'DMY'` (day-month-year), `'MDY'` (month-day-year), `'YMD'` (year-month-day)
  - Example: `{'DATE_ORDER': 'DMY'}` interprets `'15/01/2024'` as January 15

- **`PREFER_DATES_FROM`** (str): Bias for ambiguous relative dates
  - Values: `'past'`, `'future'`, `'current_period'`
  - Example: `{'PREFER_DATES_FROM': 'future'}` interprets "Monday" as next Monday

- **`RELATIVE_BASE`** (datetime): Base date for relative date calculations
  - Must be a `datetime` object
  - Example: `{'RELATIVE_BASE': datetime(2024, 1, 15)}` calculates "tomorrow" from Jan 15

- **`TIMEZONE`** (str): Parse dates as if in this timezone
  - Example: `{'TIMEZONE': 'UTC'}`, `{'TIMEZONE': 'US/Eastern'}`

- **`RETURN_AS_TIMEZONE_AWARE`** (bool): Return timezone-aware datetimes
  - Default: `False` (returns naive datetime)
  - Example: `{'RETURN_AS_TIMEZONE_AWARE': True, 'TIMEZONE': 'UTC'}`

- **`STRICT_PARSING`** (bool): Enable strict parsing mode
  - Default: `False`
  - When `True`, requires exact format matches

- **`REQUIRE_PARTS`** (list): Require specific date components
  - Values: `['day']`, `['month']`, `['year']`, or combinations
  - Example: `{'REQUIRE_PARTS': ['day', 'month', 'year']}` rejects incomplete dates

- **`PARSERS`** (list): Enable/disable specific parsers
  - Values: `['timestamp']`, `['relative-time']`, `['absolute-time']`, etc.
  - Example: `{'PARSERS': ['timestamp', 'absolute-time']}` disables relative parsing

### Settings Examples:

```python
# Date order
dateparser.parse('01/02/2024', settings={'DATE_ORDER': 'MDY'})  # Feb 1, 2024
dateparser.parse('01/02/2024', settings={'DATE_ORDER': 'DMY'})  # Feb 1, 2024 (but day=1)

# Relative base
from datetime import datetime
base = datetime(2024, 1, 15, 12, 0)
dateparser.parse('tomorrow', settings={'RELATIVE_BASE': base})  # Jan 16, 2024

# Timezone
dateparser.parse('2024-01-15 14:30', settings={'TIMEZONE': 'US/Eastern'})

# Strict parsing
dateparser.parse('15th January', settings={'STRICT_PARSING': True})  # May return None

# Require components
dateparser.parse('January', settings={'REQUIRE_PARTS': ['day', 'month', 'year']})  # None
```

# Implementation Notes

## Core Behavior

1. **Return values**: `parse()` returns `datetime` objects on success, `None` on failure. It does not raise exceptions for unparseable input.

2. **Relative date determinism**: For deterministic behavior with relative dates (`'tomorrow'`, `'3 days ago'`), always provide `RELATIVE_BASE` in settings. Without it, relative dates use the current system time.

3. **Date component extraction**: Use `.date()` method on returned `datetime` to get `date` object, `.isoformat()` for ISO string representation.

4. **Timestamp parsing**: Integer or string timestamps are interpreted as Unix epoch seconds. Millisecond and microsecond timestamps are also supported.

5. **Timezone handling**: By default, returned `datetime` objects are naive (no timezone info). Use `RETURN_AS_TIMEZONE_AWARE=True` with `TIMEZONE` to get timezone-aware objects.

6. **Date order ambiguity**: For ambiguous dates like `'01/02/2024'`, use `DATE_ORDER` to specify interpretation. Default depends on locale.

## Parsing Capabilities

The library supports:
- **ISO 8601**: `'2024-01-15'`, `'2024-01-15T14:30:00Z'`
- **Common formats**: `'January 15, 2024'`, `'15 Jan 2024'`, `'01/15/2024'`
- **Relative expressions**: `'today'`, `'tomorrow'`, `'yesterday'`, `'now'`
- **Relative offsets**: `'3 days ago'`, `'in 2 weeks'`, `'2 hours ago'`
- **Weekdays**: `'Monday'`, `'next Friday'`, `'last Tuesday'`
- **Timestamps**: `'1705334400'` (seconds since epoch), `'1705334400000'` (milliseconds)
- **Natural language**: `'two days ago'`, `'next month'`

## Error Handling

- **Unparseable input**: Returns `None` (e.g., `parse('invalid')` → `None`)
- **Invalid language**: Raises `ValueError`
- **Invalid settings**: Raises `SettingValidationError` (subclass of `ValueError`)
- **Invalid types**: Raises `TypeError` (e.g., passing integer instead of string)

## Settings Validation

The library validates settings and raises `SettingValidationError` for:
- Invalid values in `REQUIRE_PARTS` (must be `'day'`, `'month'`, or `'year'`)
- Invalid values in `PARSERS` list
- Invalid types for settings (e.g., `settings` must be dict or `Settings` object)

## Package Version

The package must define `__version__` attribute accessible as `dateparser.__version__` with the value `'1.4.3'`.

# Examples

## Basic Parsing

```python
import dateparser

# ISO dates
dt = dateparser.parse('2024-01-15')
assert dt.year == 2024
assert dt.month == 1
assert dt.day == 15

# ISO with time
dt = dateparser.parse('2024-01-15T14:30:00')
assert dt.hour == 14
assert dt.minute == 30

# Natural language (requires RELATIVE_BASE for determinism)
from datetime import datetime
dt = dateparser.parse('yesterday', settings={'RELATIVE_BASE': datetime(2024, 1, 15)})
assert dt.date() == datetime(2024, 1, 14).date()
```

## Date Order Handling

```python
# Ambiguous date formats
dt1 = dateparser.parse('01/02/2024', settings={'DATE_ORDER': 'MDY'})
assert dt1.month == 1 and dt1.day == 2

dt2 = dateparser.parse('01/02/2024', settings={'DATE_ORDER': 'DMY'})
assert dt2.day == 1 and dt2.month == 2
```

## Relative Date Parsing

```python
from datetime import datetime

base = datetime(2024, 1, 15, 12, 0, 0)

# Tomorrow
dt = dateparser.parse('tomorrow', settings={'RELATIVE_BASE': base})
assert dt.date() == datetime(2024, 1, 16).date()

# Days ago
dt = dateparser.parse('3 days ago', settings={'RELATIVE_BASE': base})
assert dt.date() == datetime(2024, 1, 12).date()

# Today
dt = dateparser.parse('today', settings={'RELATIVE_BASE': base})
assert dt.date() == base.date()
```

## Timestamp Parsing

```python
# Unix epoch seconds
dt = dateparser.parse('1705334400')  # 2024-01-15 12:00:00 UTC
assert dt is not None

# Extract date components
print(dt.year, dt.month, dt.day)
```

## Error Handling and Boundary Conditions

```python
# Unparseable input returns None
assert dateparser.parse('not a date') is None
assert dateparser.parse('') is None
assert dateparser.parse('xyz123') is None

# Empty or whitespace strings
assert dateparser.parse('   ') is None

# Invalid settings raise exceptions
from dateparser.conf import SettingValidationError
try:
    dateparser.parse('2024-01-15', settings={'REQUIRE_PARTS': ['invalid']})
except SettingValidationError:
    pass  # Expected
```

## DateDataParser Reuse

```python
from dateparser import DateDataParser

# Create parser with fixed settings
parser = DateDataParser(settings={'DATE_ORDER': 'DMY'})

# Parse multiple dates with same configuration
data1 = parser.get_date_data('15/01/2024')
data2 = parser.get_date_data('20/01/2024')

dt1 = data1['date_obj'] if data1 else None
dt2 = data2['date_obj'] if data2 else None

assert dt1.day == 15
assert dt2.day == 20
```

## Timezone-Aware Parsing

```python
# Parse as timezone-aware
dt = dateparser.parse(
    '2024-01-15 14:30',
    settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
)
assert dt.tzinfo is not None
```

# Security

The library performs string parsing only and does not:
- Execute arbitrary code from parsed strings
- Make network requests during parsing
- Access the filesystem during parsing (after installation)
- Require elevated privileges

All input is treated as untrusted text. The library is designed for parsing user input and web-scraped content safely.

# Error Handling and Boundary Conditions

## Null and Empty Input
- `parse(None)` may raise `AttributeError` or `TypeError`
- `parse('')` returns `None`
- `parse('   ')` (whitespace) returns `None`

## Ambiguous Dates
- Dates like `'01/02/2024'` require `DATE_ORDER` setting for consistent interpretation
- Relative dates like `'Monday'` require `PREFER_DATES_FROM` or `RELATIVE_BASE` for deterministic results

## Invalid Configuration
- Invalid `REQUIRE_PARTS` values raise `SettingValidationError`
- Invalid `PARSERS` values raise `SettingValidationError`
- `settings` parameter must be dict or `Settings` instance, otherwise raises `TypeError`

## Partial Dates
- `'January 2024'` (missing day) parses to first day of month by default
- Use `REQUIRE_PARTS` to reject incomplete dates
- `'2024'` (year only) may parse to January 1st

## Timezone Edge Cases
- Without timezone settings, naive `datetime` objects are returned
- System local timezone is used by default for interpretation
- Use explicit `TIMEZONE` setting for consistent behavior across systems

