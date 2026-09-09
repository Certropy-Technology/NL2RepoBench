# Natural Language Instruction

Build the `arrow` package (version 1.4.0), a Python library that offers a sensible and human-friendly approach to creating, manipulating, formatting, and converting dates, times, and timestamps. Arrow implements and updates the datetime type, providing an intelligent module API that supports many common creation scenarios. It helps you work with dates and times with fewer imports and less code.

# Project Description

Arrow is a Python library that provides a better approach to working with dates, times, and timestamps. It offers:

- A drop-in replacement for Python's datetime with enhanced functionality
- Simple and intuitive API for date/time manipulation
- Timezone-aware operations by default
- Extensive parsing and formatting capabilities
- Human-readable time differences (humanization)
- Date/time ranges and spans

# Supports

- **Python Version**: 3.8+
- **Package Format**: Standard Python package with `pyproject.toml`
- **Build System**: flit_core
- **Installation**: Installable via pip with editable mode support

# Environment Configuration

**Python Version**: 3.12

**Operating System**: Debian 12 (amd64)

**Runtime Dependencies**:
- python-dateutil >= 2.7.0
- tzdata (for Python 3.9+)

# API Usage Guide

## Core Functions

### arrow.get()

The primary method for creating Arrow objects from various inputs.

**Import Path**: `arrow.get`

**Signatures**:
```python
# From ISO 8601 string
arrow.get('2024-01-15T12:30:45+00:00') -> Arrow

# From Unix timestamp (int or float)
arrow.get(1705321845) -> Arrow
arrow.get(1705321845.5) -> Arrow

# From year, month, day components
arrow.get(2024, 1, 15) -> Arrow
arrow.get(2024, 1, 15, 12, 30, 45) -> Arrow

# From string with format
arrow.get('15/01/2024', 'DD/MM/YYYY') -> Arrow
arrow.get('2024/01/15', ['YYYY-MM-DD', 'YYYY/MM/DD']) -> Arrow

# From datetime object
from datetime import datetime
arrow.get(datetime(2024, 1, 15, 12, 30, 45)) -> Arrow

# From date object
from datetime import date
arrow.get(date(2024, 1, 15)) -> Arrow

# From struct_time
import time
arrow.get(time.strptime('2024-01-15 12:30:45', '%Y-%m-%d %H:%M:%S')) -> Arrow

# With timezone
arrow.get('2024-01-15T12:30:45', tzinfo='US/Eastern') -> Arrow
```

**Parameters**:
- Various input types for date/time creation
- `locale`: str (default: 'en_us')
- `tzinfo`: timezone identifier or tzinfo object
- `normalize_whitespace`: bool (default: False)

**Returns**: Arrow object

**Behavior**: Parses and creates Arrow objects from various input formats. Defaults to UTC timezone for naive datetimes.

## Arrow Object Methods

### format()

Format the Arrow object as a string.

**Signature**:
```python
arrow_obj.format() -> str
arrow_obj.format('YYYY-MM-DD') -> str
arrow_obj.format('HH:mm:ss') -> str
```

**Common format tokens**:
- `YYYY`: 4-digit year
- `MM`: 2-digit month
- `DD`: 2-digit day
- `HH`: 2-digit hour (24-hour)
- `hh`: 2-digit hour (12-hour)
- `mm`: 2-digit minute
- `ss`: 2-digit second
- `A`: AM/PM
- `MMMM`: Full month name
- `MMM`: Short month name
- `dddd`: Full day name
- `ZZ`: UTC offset (+00:00)
- `[text]`: Escaped text

**Returns**: Formatted string

### shift()

Move forward or backward in time.

**Signature**:
```python
arrow_obj.shift(
    years=0, quarters=0, months=0, weeks=0, days=0,
    hours=0, minutes=0, seconds=0, microseconds=0
) -> Arrow
```

**Parameters**: Integer values for each time unit (can be negative)

**Returns**: New Arrow object shifted by specified amounts

**Example**:
```python
arrow.get('2024-01-15T12:30:45+00:00').shift(days=5, hours=3)
# -> 2024-01-20T15:30:45+00:00
```

### replace()

Replace specific datetime components.

**Signature**:
```python
arrow_obj.replace(
    year=None, month=None, day=None,
    hour=None, minute=None, second=None, microsecond=None,
    tzinfo=None
) -> Arrow
```

**Parameters**: New values for specific components

**Returns**: New Arrow object with replaced values

### to()

Convert to a different timezone.

**Signature**:
```python
arrow_obj.to(tz: str | tzinfo) -> Arrow
```

**Parameters**:
- `tz`: Timezone identifier (e.g., 'US/Pacific', 'UTC', 'Asia/Tokyo')

**Returns**: New Arrow object in the specified timezone

### floor() and ceil()

Round down or up to the start/end of a time frame.

**Signature**:
```python
arrow_obj.floor(frame: str) -> Arrow
arrow_obj.ceil(frame: str) -> Arrow
```

**Parameters**:
- `frame`: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'

**Returns**: New Arrow object floored/ceiled to the frame

**Behavior**:
- `floor()`: Rounds down to the start of the frame
- `ceil()`: Rounds up to the end of the frame (e.g., 23:59:59.999999 for day)

### span()

Get the start and end of a time frame.

**Signature**:
```python
arrow_obj.span(frame: str) -> tuple[Arrow, Arrow]
```

**Parameters**:
- `frame`: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute'

**Returns**: Tuple of (start, end) Arrow objects

**Example**:
```python
arrow.get('2024-01-15T12:30:45+00:00').span('day')
# -> (2024-01-15T00:00:00+00:00, 2024-01-15T23:59:59.999999+00:00)
```

### timestamp()

Get Unix timestamp.

**Signature**:
```python
arrow_obj.timestamp() -> float
```

**Returns**: Unix timestamp (seconds since epoch) as float

### isoformat()

Get ISO 8601 format string.

**Signature**:
```python
arrow_obj.isoformat(sep='T', timespec='auto') -> str
```

**Returns**: ISO 8601 formatted string (e.g., '2024-01-15T12:30:45+00:00')

### humanize()

Get human-readable relative time.

**Signature**:
```python
arrow_obj.humanize(
    other: Arrow = None,
    only_distance: bool = False,
    granularity: str = 'auto'
) -> str
```

**Parameters**:
- `other`: Reference Arrow object (defaults to now)
- `only_distance`: If True, returns distance without direction
- `granularity`: Limit to specific unit ('day', 'hour', 'minute', 'second')

**Returns**: Human-readable string (e.g., "2 hours", "3 days")

### range() (class method)

Generate a range of Arrow objects.

**Signature**:
```python
Arrow.range(
    frame: str,
    start: Arrow,
    end: Arrow,
    limit: int = None
) -> Iterator[Arrow]
```

**Parameters**:
- `frame`: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'
- `start`: Starting Arrow object
- `end`: Ending Arrow object
- `limit`: Maximum number of items

**Returns**: Iterator of Arrow objects

**Example**:
```python
list(Arrow.range('day', 
     arrow.get('2024-01-15T00:00:00+00:00'),
     arrow.get('2024-01-18T00:00:00+00:00')))
# -> [2024-01-15, 2024-01-16, 2024-01-17, 2024-01-18]
```

# Implementation Notes

## Key Characteristics

1. **Timezone Awareness**: Arrow objects are timezone-aware by default, using UTC for naive inputs
2. **Immutability**: All manipulation methods return new Arrow objects rather than modifying in place
3. **Consistent API**: Similar methods across different operations (shift, replace, format)
4. **Deterministic Operations**: All time operations are deterministic when using fixed timestamps

## Supported Date/Time Operations

- Parsing from multiple formats (ISO 8601, custom formats, timestamps)
- Formatting with extensive token support
- Timezone conversions
- Date arithmetic (shift, replace)
- Rounding operations (floor, ceil, span)
- Range generation
- Human-readable formatting

## Edge Cases

- Leap years: Handles February 29 correctly
- Month boundaries: Shifting from Jan 31 + 1 month = Feb 28/29 (last day of target month)
- Year boundaries: Proper handling of year rollovers
- Negative timestamps: Supports dates before Unix epoch (1970-01-01)
- Microsecond precision: Maintains microsecond accuracy in timestamps

## Package Structure

```
workspace/
├── arrow/
│   ├── __init__.py
│   ├── _version.py
│   ├── api.py
│   ├── arrow.py
│   ├── constants.py
│   ├── factory.py
│   ├── formatter.py
│   ├── locales.py
│   ├── parser.py
│   └── util.py
├── pyproject.toml
├── README.rst
└── LICENSE
```

## Installation Requirements

The package requires:
- Python 3.8 or higher
- python-dateutil >= 2.7.0
- tzdata (for Python 3.9+)

Install in editable mode:
```bash
pip install -e .
```

## Version Information

- Package version: 1.4.0
- Accessed via `arrow.__version__`

# Project Directory Structure

```
workspace/
├── arrow/
│   ├── __init__.py         # Main module with Arrow class and API functions
│   ├── _version.py          # Version information
│   ├── api.py               # Public API functions (get, utcnow, etc.)
│   ├── arrow.py             # Core Arrow class implementation
│   ├── constants.py         # Constants and default values
│   ├── factory.py           # Arrow factory for object creation
│   ├── formatter.py         # Date/time formatting logic
│   ├── locales.py           # Locale support
│   ├── parser.py            # Parsing logic for various formats
│   └── util.py              # Utility functions
├── docs/                    # Documentation files
├── tests/                   # Test suite
├── pyproject.toml           # Project metadata and build configuration
├── README.rst               # Project documentation
├── CHANGELOG.rst            # Version history
├── LICENSE                  # Apache 2.0 license
└── Makefile                 # Development tasks
```
