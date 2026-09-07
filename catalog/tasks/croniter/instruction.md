# Project Description

croniter is a Python library that provides iteration capabilities for datetime objects using cron-like expressions. It allows developers to calculate future and past datetime occurrences based on standard cron syntax, making it useful for scheduling, recurring event calculations, and time-based automation.

The library supports standard 5-field cron expressions (minute, hour, day, month, day_of_week) as well as extended formats including seconds and years. It handles timezone-aware datetime objects, DST transitions, leap years, and various cron special characters including ranges, lists, steps, and special operators like 'L' (last), 'W' (nearest weekday), and '#' (nth occurrence).

Key capabilities include:
- Forward and backward iteration through cron schedule matches
- Validation of cron expressions
- Range-based datetime generation
- Hash-based and random time distribution within cron intervals
- Timezone-aware datetime handling

# Natural Language Instruction

Implement a Python package named `croniter` that provides cron expression parsing and datetime iteration. The package must:

1. Parse standard and extended cron expressions with proper validation
2. Support forward iteration (get_next) and backward iteration (get_prev) from a given start time
3. Handle timezone-aware datetime objects correctly including DST transitions
4. Provide cron expression validation with strict mode for cross-field validation
5. Support special cron syntax: ranges, lists, steps, 'L' (last day), 'W' (nearest weekday), '#' (nth occurrence)
6. Implement croniter_range() for generating all datetimes in a range matching a cron expression
7. Support hash-based (H) and random (R) expressions for distributed scheduling
8. Provide match() and match_range() class methods for testing if datetime(s) match a cron expression
9. Handle day_or parameter for controlling day-of-month and day-of-week interaction (OR vs AND)
10. Support multiple cron expression formats: 5-field (standard), 6-field (with seconds), 7-field (with year)

Package must be installable via pip with entry point `croniter` and import path `from croniter import croniter`.

# Supports

- Python: 3.9 or higher (tested with 3.12)
- Package manager: pip
- Build system: hatchling
- Installation: `pip install -e .` or `pip install croniter`
- Runtime dependencies: `python-dateutil`
- Testing: pytest framework
- Platform: Linux, cross-platform compatible

# Project Directory Structure

```text
workspace/
├── pyproject.toml              # Project metadata and build configuration
├── LICENSE                     # MIT license file
├── README.rst                  # Documentation (optional)
├── src/
│   └── croniter/
│       ├── __init__.py         # Package initialization with public exports
│       └── croniter.py         # Main implementation module
```

The package uses a src-layout with `croniter` as the importable package name. The build system is hatchling configured in pyproject.toml.

# API Usage Guide

## Core Classes and Functions

### croniter class

**Import:** `from croniter import croniter`

Main class for iterating through cron schedule matches.

**Constructor:**
```python
croniter(expr_format, start_time=None, ret_type=float, day_or=True, 
         max_years_between_matches=None, is_prev=False, hash_id=None,
         implement_cron_bug=False, second_at_beginning=False,
         expand_from_start_time=False)
```

Parameters:
- `expr_format` (str): Cron expression (5, 6, or 7 fields)
- `start_time` (float|datetime|None): Starting point for iteration (default: current time)
- `ret_type` (type): Return type for get_next/get_prev (float or datetime, default: float)
- `day_or` (bool): True for OR logic between day and day_of_week (default), False for AND
- `max_years_between_matches` (int|None): Maximum years to search for next match
- `is_prev` (bool): If True, iterator moves backward by default
- `hash_id` (str|bytes|None): Identifier for hash expressions (H syntax)
- `implement_cron_bug` (bool): Emulate historical cron bug behavior
- `second_at_beginning` (bool): Interpret 6-field as second-first instead of second-last
- `expand_from_start_time` (bool): Expand hash expressions from start_time instead of epoch

**Methods:**

```python
get_next(ret_type=None, start_time=None, update_current=True)
```
Calculate and return the next datetime matching the cron expression.
- `ret_type`: Override constructor ret_type (float or datetime)
- `start_time`: Override starting point for this call
- `update_current`: If True, advance internal state (default: True)
- Returns: Next matching time as ret_type

```python
get_prev(ret_type=None, start_time=None, update_current=True)
```
Calculate and return the previous datetime matching the cron expression.
Same parameters and behavior as get_next but moves backward in time.

```python
get_current(ret_type=None)
```
Return the current position without advancing.
- Returns: Current time as ret_type

```python
set_current(start_time, force=True)
```
Set the current position to a specific time.
- `start_time`: New current time (float or datetime)
- `force`: If True, allow setting to any time; if False, must be a match

```python
all_next(ret_type=None, start_time=None, update_current=None)
```
Generator yielding all future matches indefinitely.

```python
all_prev(ret_type=None, start_time=None, update_current=None)
```
Generator yielding all past matches indefinitely.

```python
iter()
```
Return an iterator (same as __iter__).

**Class Methods:**

```python
@classmethod
is_valid(cls, expression, hash_id=None, encoding='UTF-8', 
         second_at_beginning=False, strict=False, strict_year=None)
```
Validate a cron expression.
- `expression` (str): Cron expression to validate
- `strict` (bool): Enable cross-field validation (e.g., reject Feb 31)
- `strict_year` (int|list): Year(s) for leap year checking in strict mode
- Returns: True if valid, False otherwise

```python
@classmethod
expand(cls, expr_format, hash_id=None, second_at_beginning=False,
       from_timestamp=None, strict=False, strict_year=None)
```
Expand cron expression into lists of integers for each field.
- Returns: Tuple of lists, one per cron field
- Raises: CroniterBadCronError if invalid

```python
@classmethod
match(cls, cron_expression, testdate, day_or=True, 
      second_at_beginning=False, precision_in_seconds=None)
```
Test if a specific datetime matches the cron expression.
- `testdate` (datetime): Datetime to test
- Returns: True if testdate matches the cron expression

```python
@classmethod
match_range(cls, cron_expression, from_datetime, to_datetime,
            day_or=True, second_at_beginning=False, precision_in_seconds=None)
```
Test if a cron expression matches any time in a datetime range.
- Returns: True if expression matches any time in [from_datetime, to_datetime]

### croniter_range function

**Import:** `from croniter import croniter_range`

```python
croniter_range(start, stop, expr_format, ret_type=None, day_or=True,
               exclude_ends=False, _croniter=None, second_at_beginning=False,
               expand_from_start_time=False)
```

Generator providing all times from start to stop matching the cron expression.
- `start` (datetime|float): Range start
- `stop` (datetime|float): Range end (must be same type as start)
- `expr_format` (str): Cron expression
- `ret_type` (type): Return type (default: datetime if inputs are datetime)
- `exclude_ends` (bool): If True, exclude start and stop from results
- Returns: Generator yielding matching datetimes

### Exception Classes

**Import:** `from croniter import CroniterError, CroniterBadCronError, ...`

- `CroniterError`: Base exception class (subclass of ValueError)
- `CroniterBadCronError`: Invalid cron expression syntax
- `CroniterBadDateError`: Invalid datetime value
- `CroniterBadTypeRangeError`: Type mismatch in croniter_range
- `CroniterNotAlphaError`: Invalid alpha abbreviation (month/weekday names)
- `CroniterUnsupportedSyntaxError`: Unsupported cron syntax

### Helper Functions

```python
datetime_to_timestamp(d)
```
Convert datetime to Unix timestamp as float.
**Import:** `from croniter import datetime_to_timestamp`
- `d` (datetime): Datetime object (can be timezone-aware)
- Returns: Float timestamp

### Constants

```python
from croniter import (
    MINUTE_FIELD, HOUR_FIELD, DAY_FIELD, MONTH_FIELD,
    SECOND_FIELD, YEAR_FIELD, UTC_DT, OVERFLOW32B_MODE
)
```

- `MINUTE_FIELD = 0`, `HOUR_FIELD = 1`, `DAY_FIELD = 2`, `MONTH_FIELD = 3`, `SECOND_FIELD = 5`, `YEAR_FIELD = 6`: Field indices
- `UTC_DT`: datetime.timezone.utc constant
- `OVERFLOW32B_MODE`: Boolean indicating 32-bit overflow handling mode

## Cron Expression Format

Standard 5-field format: `minute hour day month day_of_week`
- minute: 0-59
- hour: 0-23
- day: 1-31
- month: 1-12 (or JAN-DEC)
- day_of_week: 0-6 (0=Sunday, or SUN-SAT)

Extended formats:
- 6-field: Add seconds at the end (or beginning if second_at_beginning=True)
- 7-field: Add year field at the end

Special characters:
- `*`: Any value
- `,`: List (e.g., `1,3,5`)
- `-`: Range (e.g., `1-5`)
- `/`: Step (e.g., `*/5` = every 5 units)
- `L`: Last (day of month or day of week)
- `W`: Nearest weekday (e.g., `15W`)
- `#`: Nth occurrence (e.g., `5#3` = 3rd Friday)
- `H`: Hash-based distribution
- `R`: Random distribution

## Implementation Notes

1. **Cron Field Ranges:**
   - Minutes: 0-59
   - Hours: 0-23
   - Days: 1-31
   - Months: 1-12
   - Day of week: 0-6 (Sunday=0)
   - Seconds: 0-59
   - Years: 1970-2099

2. **day_or Behavior:**
   - When day_or=True (default): Matches when EITHER day-of-month OR day-of-week matches
   - When day_or=False: Matches only when BOTH day-of-month AND day-of-week match
   - Only applies when both fields are restricted (not *)

3. **Timezone Handling:**
   - Accepts both naive and timezone-aware datetime objects
   - When timezone-aware, handles DST transitions correctly
   - For ambiguous times during DST fall-back, selects the occurrence closer to previous match
   - For non-existent times during DST spring-forward, advances to next valid time

4. **Special Day Syntax:**
   - `L` in day field: Last day of the month (respects leap years)
   - `L5` or `5L`: Last occurrence of day-of-week (e.g., last Friday)
   - `15W`: Nearest weekday to the 15th
   - `5#3`: 3rd occurrence of day 5 (Friday) in the month
   - `sat#1,sun#2`: 1st Saturday and 2nd Sunday

5. **Hash Expressions (H):**
   - Deterministic pseudo-random distribution based on hash_id
   - `H` expands to single value based on hash(hash_id) for that field
   - `H(5-55)/10` expands to value in range 5-55, then applies step
   - Same hash_id produces same expansion across calls
   - Useful for distributed systems to avoid thundering herd

6. **Leap Year Handling:**
   - February 29th correctly handled in leap years
   - is_valid with strict=True validates day/month combinations
   - Last day of month ('L') correctly returns 29 for Feb in leap years

7. **Return Types:**
   - Default ret_type is float (Unix timestamp)
   - Can specify datetime.datetime as ret_type for datetime objects
   - Timestamps preserve microsecond precision

8. **Iteration State:**
   - Each call to get_next/get_prev with update_current=True advances internal state
   - Use update_current=False to peek without changing state
   - set_current() resets the iterator position

9. **Month and Weekday Names:**
   - Months: JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC (case-insensitive)
   - Weekdays: SUN, MON, TUE, WED, THU, FRI, SAT (case-insensitive)
   - Partial ranges work: JAN-MAR, MON-FRI

10. **Error Handling:**
    - Invalid cron syntax raises CroniterBadCronError
    - Type mismatches in croniter_range raise CroniterBadTypeRangeError
    - Invalid dates/times raise CroniterBadDateError
    - Invalid month/weekday names raise CroniterNotAlphaError

# Examples

## Basic Forward Iteration

```python
from croniter import croniter
from datetime import datetime

base = datetime(2010, 1, 25, 4, 46)
iter = croniter('*/5 * * * *', base)  # every 5 minutes
print(iter.get_next(datetime))   # 2010-01-25 04:50:00
print(iter.get_next(datetime))   # 2010-01-25 04:55:00
print(iter.get_next(datetime))   # 2010-01-25 05:00:00
```

## Backward Iteration

```python
base = datetime(2010, 8, 25)
itr = croniter('0 0 1 * *', base)
print(itr.get_prev(datetime))  # 2010-08-01 00:00:00
print(itr.get_prev(datetime))  # 2010-07-01 00:00:00
```

## Cron Expression Validation

```python
croniter.is_valid('0 0 1 * *')  # True
croniter.is_valid('0 wrong_value 1 * *')  # False
croniter.is_valid('0 0 31 2 *')  # True (no cross-validation)
croniter.is_valid('0 0 31 2 *', strict=True)  # False (Feb has max 29 days)
```

## Range Generation

```python
from croniter import croniter_range
from datetime import datetime

start = datetime(2024, 1, 1)
stop = datetime(2024, 1, 7)
for dt in croniter_range(start, stop, '0 9 * * MON-FRI'):
    print(dt)  # Prints 9:00 AM on each weekday
```

## Special Day Syntax

```python
# Last day of each month
iter = croniter('0 0 L * *', datetime(2024, 1, 1))
print(iter.get_next(datetime))  # 2024-01-31 00:00:00
print(iter.get_next(datetime))  # 2024-02-29 00:00:00 (leap year)

# 3rd Friday and last Friday
iter = croniter('0 0 * * 5#3,L5', datetime(2024, 1, 1))
print(iter.get_next(datetime))  # 2024-01-19 00:00:00 (3rd Fri)
print(iter.get_next(datetime))  # 2024-01-26 00:00:00 (last Fri)
```

## Nearest Weekday

```python
# 15W = nearest weekday to 15th
iter = croniter('0 9 15W * *', datetime(2024, 6, 1))
# If 15th is Saturday, fires on Friday 14th
print(iter.get_next(datetime))  # 2024-06-14 09:00:00
```

## Match Testing

```python
from datetime import datetime

# Test if specific datetime matches cron
croniter.match('*/5 * * * *', datetime(2024, 1, 1, 10, 30))  # True
croniter.match('*/5 * * * *', datetime(2024, 1, 1, 10, 31))  # False

# Test if any time in range matches
croniter.match_range('0 9 * * MON', 
                     datetime(2024, 1, 1), 
                     datetime(2024, 1, 7))  # True if range includes a Monday at 9 AM
```

# Error Handling and Boundary Conditions

## Invalid Cron Expressions

```python
from croniter import croniter, CroniterBadCronError

try:
    croniter('invalid cron', datetime.now())
except CroniterBadCronError as e:
    print(f"Invalid cron: {e}")

try:
    croniter('60 * * * *', datetime.now())  # minute field max is 59
except CroniterBadCronError as e:
    print(f"Out of range: {e}")
```

## Type Mismatches

```python
from croniter import croniter_range, CroniterBadTypeRangeError

try:
    # start and stop must be same type
    list(croniter_range(1234567890.0, datetime(2024, 1, 1), '* * * * *'))
except CroniterBadTypeRangeError as e:
    print(f"Type mismatch: {e}")
```

## Empty Results

```python
# No matches in range
start = datetime(2024, 1, 1)  # Monday
stop = datetime(2024, 1, 5)   # Friday
result = list(croniter_range(start, stop, '0 0 * * SAT', exclude_ends=True))
# result is [] because no Saturday in range
```

## Leap Year Edge Cases

```python
# February 29 in non-leap year
iter = croniter('0 0 29 2 *', datetime(2023, 1, 1))
next_match = iter.get_next(datetime)
# Skips to 2024-02-29 (next leap year)

# Last day of February
iter = croniter('0 0 L 2 *', datetime(2023, 1, 1))
print(iter.get_next(datetime))  # 2023-02-28 (non-leap)
print(iter.get_next(datetime))  # 2024-02-29 (leap)
```

## Timezone and DST

```python
import pytz
from datetime import datetime

# During DST transition
eastern = pytz.timezone('US/Eastern')
base = eastern.localize(datetime(2024, 3, 10, 1, 0))  # Before DST
iter = croniter('0 3 * * *', base)  # 3 AM daily
next_match = iter.get_next(datetime)
# Handles DST spring-forward at 2 AM correctly
```

## day_or Behavior

```python
# OR behavior (default): matches Wednesday OR 1st of month
iter = croniter('0 0 1 * WED', datetime(2024, 1, 1), day_or=True)
print(iter.get_next(datetime))  # 2024-01-03 (Wed)
print(iter.get_next(datetime))  # 2024-02-01 (1st)

# AND behavior: matches 1st of month ONLY if it's Wednesday
iter = croniter('0 0 1 * WED', datetime(2024, 1, 1), day_or=False)
next_match = iter.get_next(datetime)
# Waits for a month where 1st is Wednesday
```

## Hash Expression Determinism

```python
# Same hash_id produces same results
iter1 = croniter('H H * * *', datetime(2024, 1, 1), hash_id='task1')
iter2 = croniter('H H * * *', datetime(2024, 1, 1), hash_id='task1')
assert iter1.get_next(datetime) == iter2.get_next(datetime)

# Different hash_id produces different results
iter3 = croniter('H H * * *', datetime(2024, 1, 1), hash_id='task2')
assert iter1.get_next(datetime) != iter3.get_next(datetime)
```

## Maximum Search Range

```python
# Prevent infinite search with max_years_between_matches
try:
    # Very restrictive expression that might never match
    iter = croniter('0 0 31 2 *', datetime(2024, 1, 1), 
                    max_years_between_matches=5)
    iter.get_next(datetime)  # Raises error if no match in 5 years
except CroniterBadDateError as e:
    print(f"No match found: {e}")
```
