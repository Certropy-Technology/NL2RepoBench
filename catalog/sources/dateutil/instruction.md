# Project Description

The `python-dateutil` package provides powerful extensions to the standard Python `datetime` module. It enables developers to work with dates and times more effectively through features like relative date calculations, flexible date parsing, recurrence rule handling, timezone management, and Easter date computation.

The project targets Python developers who need to perform date arithmetic with relative offsets, parse dates from text, generate recurring patterns, handle timezones, or calculate holiday dates. This implementation must provide a pure-Python solution installable via `pip install -e .` from the workspace root, with no network access required during execution.

# Natural Language Instruction

Build the `python-dateutil` package (PyPI package name: `python-dateutil`, import name: `dateutil`) that extends Python's standard `datetime` module with:

1. **Relative Date/Time Calculations**: Implement `relativedelta` class for date arithmetic with relative (years, months, days) and absolute (year, month, day) components
2. **Flexible Date Parsing**: Provide `parser.parse()` for parsing datetime objects from various string formats
3. **Recurrence Rules**: Implement `rrule` module for RFC 5545 recurrence rules
4. **Timezone Handling**: Provide `tz` module with UTC, local, and fixed offset timezones
5. **Easter Calculation**: Implement `easter.easter()` for computing Easter Sunday dates
6. **Utility Functions**: Provide helpers like `utils.today()`, `utils.within_delta()`

The package must be installable with `python -m pip install --no-build-isolation --no-deps --no-index -e .` and work offline.

# Environment Configuration

- **Language**: Python 3.12
- **Package Manager**: pip
- **Installation**: `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- **Runtime Dependency**: `six >= 1.5` (preinstalled)
- **Build Backend**: `setuptools` with `setuptools_scm` (preinstalled)
- **Network Policy**: No network access during agent, candidate, or verifier execution
- **Python Requirement**: `>=2.7, !=3.0.*, !=3.1.*, !=3.2.*`
- **Base Image**: python:3.12-slim-bookworm (Debian 12)

# Project Directory Structure

```
workspace/
├── pyproject.toml
├── setup.cfg
├── setup.py
├── src/
│   └── dateutil/
│       ├── __init__.py
│       ├── _version.py
│       ├── _common.py
│       ├── relativedelta.py
│       ├── rrule.py
│       ├── easter.py
│       ├── utils.py
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── _parser.py
│       │   └── isoparser.py
│       └── tz/
│           ├── __init__.py
│           ├── tz.py
│           ├── _common.py
│           └── _factories.py
```

# API Usage Guide

## Module: dateutil.relativedelta

**Class: relativedelta**

`from dateutil.relativedelta import relativedelta`

Constructors:
- `relativedelta(dt1, dt2)` - Difference between two datetimes
- `relativedelta(years=0, months=0, days=0, weeks=0, hours=0, minutes=0, seconds=0, microseconds=0, year=None, month=None, day=None, weekday=None, hour=None, minute=None, second=None, microsecond=None)` - Keyword constructor

Plural keywords are relative (add/subtract). Singular keywords are absolute (replace).

Operations: `datetime ± relativedelta`

Attributes: `.years`, `.months`, `.days`, `.hours`, `.minutes`, `.seconds`, `.microseconds`, `.year`, `.month`, `.day`, `.weekday`, etc.

Example:
```python
from datetime import datetime
from dateutil.relativedelta import relativedelta
dt = datetime(2020, 1, 31)
dt + relativedelta(months=1)  # -> datetime(2020, 2, 29)
```

**Weekday Constants**

`from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU`

Constants for weekday calculations. Each has `.weekday` attribute (0-6).

## Module: dateutil.parser

**Function: parse**

`from dateutil.parser import parse` or `parser.parse(...)`

Signature: `parse(timestr, default=None, ignoretz=False, tzinfos=None, dayfirst=False, yearfirst=False, fuzzy=False, ...)`

Parameters:
- `timestr` (str): String to parse
- `default` (datetime, optional): Default for missing components
- `dayfirst` (bool): Interpret first value as day
- `yearfirst` (bool): Interpret first value as year
- `fuzzy` (bool): Ignore unrecognized tokens

Returns: `datetime.datetime`

Raises: `ParserError` if unparseable

Formats: ISO 8601, slash-separated, text-based, time-only

Example:
```python
from dateutil import parser
parser.parse("2020-01-15")  # -> datetime(2020, 1, 15, 0, 0, 0)
parser.parse("15/01/2020", dayfirst=True)
```

**Function: isoparse**

`from dateutil.parser import isoparse`

Parse ISO 8601 datetime strings. Returns `datetime.datetime` or `datetime.date`.

**Class: parser, parserinfo**

Stateful parser and configuration classes.

**Exception: ParserError**

Raised when parsing fails.

## Module: dateutil.rrule

**Class: rrule**

`from dateutil.rrule import rrule` or `from dateutil import rrule; rrule.rrule(...)`

Signature: `rrule(freq, dtstart=None, interval=1, wkst=None, count=None, until=None, bysetpos=None, bymonth=None, bymonthday=None, byweekday=None, byhour=None, byminute=None, bysecond=None, ...)`

Parameters:
- `freq`: DAILY, WEEKLY, MONTHLY, YEARLY, HOURLY, MINUTELY, SECONDLY
- `dtstart` (datetime): Start date
- `count` (int): Number of occurrences
- `until` (datetime): End date
- `interval` (int): Spacing
- `byweekday`: Weekday constraint
- `bymonthday`, `bymonth`, `byhour`, etc.: Additional constraints

Returns: Iterable rrule object

Example:
```python
from datetime import datetime
from dateutil import rrule
start = datetime(2020, 1, 1, 9, 0, 0)
list(rrule.rrule(rrule.DAILY, count=3, dtstart=start))
# -> [datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 9, 0), datetime(2020, 1, 3, 9, 0)]
```

**Function: rrulestr**

`from dateutil.rrule import rrulestr`

Parse RRULE strings: `rrulestr("FREQ=DAILY;COUNT=3", dtstart=dt)`

**Class: rruleset**

Container for multiple rrules and rdates.

Methods: `.rrule(r)`, `.rdate(dt)`, `.exrule(r)`, `.exdate(dt)`

## Module: dateutil.easter

**Function: easter**

`from dateutil.easter import easter` or `easter.easter(...)`

Signature: `easter(year, method=EASTER_WESTERN)`

Parameters:
- `year` (int): Year
- `method` (int): EASTER_WESTERN, EASTER_ORTHODOX, EASTER_JULIAN

Returns: `datetime.date` (not datetime)

Example:
```python
from dateutil import easter
easter.easter(2020)  # -> date(2020, 4, 12)
```

## Module: dateutil.tz

**Class/Functions**

`from dateutil.tz import UTC, tzutc, tzlocal, tzoffset, tzstr, tzrange, gettz, enfold, resolve_imaginary`

- `UTC`: UTC timezone constant
- `tzutc()`: UTC timezone class
- `tzlocal()`: Local timezone
- `tzoffset(name, offset)`: Fixed offset timezone
- `tzstr(s)`: Parse POSIX timezone strings
- `tzrange(...)`: Timezone with DST
- `gettz(name=None)`: Get timezone by name
- `enfold(dt, fold=1)`: Set fold attribute
- `resolve_imaginary`: Callable for DST resolution

Example:
```python
from datetime import datetime, timedelta
from dateutil import tz
dt = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz.UTC)
est = tz.tzoffset("EST", timedelta(hours=-5))
```

## Module: dateutil.utils

**Function: today**

`from dateutil.utils import today` or `utils.today()`

Returns: `datetime.datetime` for today (not just date)

**Function: default_tzinfo**

`default_tzinfo(dt, tzinfo)` - Apply default timezone if dt has none

**Function: within_delta**

`within_delta(dt1, dt2, delta)` - Check if datetimes are within timedelta

Returns: `bool`

# Implementation Notes

1. **Package Naming**: PyPI name is `python-dateutil`, import name is `dateutil`
2. **Build System**: Use setuptools with static version or setuptools_scm fallback
3. **Lazy Imports**: Implement `__getattr__()` in `__init__.py` for lazy module loading
4. **Dependency**: Declare `six >= 1.5` in `install_requires`
5. **Month-end Handling**: Handle overflow intelligently (Jan 31 + 1 month = Feb 29/28)
6. **Weekday Calculation**: `weekday=MO` moves to next Monday
7. **Parser Flexibility**: Support ISO 8601, slash/dash separated, and text formats
8. **RRULE Compliance**: Implement RFC 5545 subset for common patterns
9. **Timezone**: Support UTC, local, and fixed offsets offline
10. **Easter Algorithms**: Implement Gregorian, Julian, and Orthodox methods

# Examples

## Date Arithmetic
```python
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO
dt = datetime(2020, 1, 15, 12, 0, 0)
dt + relativedelta(months=3, days=2)  # -> datetime(2020, 4, 17, 12, 0, 0)
dt + relativedelta(weekday=MO)  # -> Next Monday
```

## Date Parsing
```python
from dateutil import parser
parser.parse("2020-01-15")
parser.parse("Jan 15, 2020")
parser.parse("Today is 2020-01-15", fuzzy=True)
```

## Recurring Dates
```python
from datetime import datetime
from dateutil import rrule
start = datetime(2020, 1, 1, 9, 0, 0)
list(rrule.rrule(rrule.WEEKLY, byweekday=rrule.MO, count=4, dtstart=start))
```

## Timezone Operations
```python
from datetime import datetime
from dateutil import tz
utc_dt = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz.UTC)
```

# Error Handling

- `parser.parse()` raises `ParserError` for invalid strings
- `relativedelta()` raises `ValueError` for non-integer years/months
- Handle month-end overflow, leap years, DST transitions
- `count=0` returns empty list
- Ambiguous dates use `dayfirst`/`yearfirst` parameters

# Security

- No code execution in parser
- Resource limits for large recurrence rules
- No runtime timezone data downloads
- Input validation to prevent arithmetic errors
- Use preinstalled dependencies only
