# Project Description

Create an installable Python distribution named `pytz` from an empty workspace.
The package provides deterministic timezone objects backed by bundled IANA
resources. This task covers timezone lookup, localization, normalization,
fixed offsets, release constants, and the documented exception classes. The
runtime must not consult the host operating-system timezone database or fetch
timezone data.

# Natural Language Instruction

Build the `pytz` project and expose its public API through the `pytz` package.
Implement all of the following capabilities:

1. Resolve named zones and expose the UTC aliases and deterministic zone lists.
2. Localize naive datetimes and normalize aware datetimes across DST changes.
3. Distinguish ambiguous fall-back times from nonexistent spring-forward times.
4. Provide cached fixed-offset zones and the documented public exceptions.
5. Package the timezone resources so the installed project works from an empty
   caller workspace with no external files, services, or network.

Preserve the standard `datetime.tzinfo` protocol, the public import paths, and
the exact distinction between `is_dst=True`, `False`, and `None`. Do not replace
the required package data with calls to `zoneinfo.ZoneInfo` or host files.

# Supports or Environment Configuration

- Runtime: CPython 3.12.14 on Debian 12 amd64.
- Distribution and import name: `pytz`; the task version is `1.0.0`.
- Install from `workspace/` with the declared setuptools build metadata and no
  runtime dependency beyond the Python standard library.
- The package must include `setup.py`, the `pytz` source package, and bundled
  zone resources. At minimum support `UTC`, `US/Eastern`, `Europe/London`, and
  `Asia/Tokyo`, including aliases required to resolve those names.
- Build dependencies are available during image construction. The frozen
  runtime and all checks are NoNetwork: Agent, candidate, verifier, Oracle,
  and controls must not access GitHub, PyPI, npm, Go proxy, DNS, or services.
- Results must be deterministic for fixed datetime inputs, independent of the
  host timezone database, current working directory, and machine locale.

# Project Directory Structure

```text
workspace/
├── setup.py
├── pytz/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── lazy.py
│   ├── tzfile.py
│   ├── tzinfo.py
│   └── zoneinfo/
│       ├── UTC
│       ├── US/Eastern
│       ├── Europe/London
│       └── Asia/Tokyo
└── README.md
```

The tree shows the required public package and resource locations. Additional
zone files may be included when they are represented by the frozen resource
contract, but do not require an operating-system resource directory.

# API Usage Guide

## `pytz.timezone`

```python
from pytz import timezone, utc

zone = timezone("US/Eastern")
assert zone.zone == "US/Eastern"
assert utc is timezone("UTC")
```

`timezone(zone: str) -> datetime.tzinfo` accepts an IANA name and returns a
cached timezone object. `UTC` returns the singleton `pytz.utc`; named zones
return objects whose `zone` value is stable. Unknown or empty names raise
`UnknownTimeZoneError`, not `KeyError`. `all_timezones` is a deterministic
sequence of names and `all_timezones_set` is the corresponding set; callers
must not infer an ordering from the set.

The root exports `utc`, `UTC`, `timezone`, `all_timezones`,
`all_timezones_set`, `__version__`, and `OLSON_VERSION`.

## Localizing and converting datetimes

```python
from datetime import datetime
from pytz import timezone, utc

eastern = timezone("US/Eastern")
local = eastern.localize(datetime(2024, 1, 15, 12, 0))
converted = local.astimezone(utc)
assert converted.tzinfo is utc
```

`localize(dt: datetime, is_dst=False) -> datetime` accepts a naive datetime
and returns an aware datetime with the zone's applicable offset. Passing an
already-aware datetime is invalid according to the timezone object's normal
contract and must not silently reinterpret it. During a fall-back overlap,
`is_dst=True` selects the daylight occurrence and `is_dst=False` selects the
standard occurrence; `is_dst=None` raises `AmbiguousTimeError`. During a
spring-forward gap, `is_dst=None` raises `NonExistentTimeError`. The default
boolean behavior follows the locked upstream release.

`normalize(dt: datetime, is_dst=False) -> datetime` accepts an aware datetime
from the zone, corrects its offset after arithmetic across a transition, and
returns an aware datetime. It preserves the instant represented by the input.
Normal `datetime.astimezone()` conversion to another timezone remains valid.

## Fixed offsets and exceptions

```python
from pytz import FixedOffset, UnknownTimeZoneError

offset = FixedOffset(90)
assert offset.utcoffset(None).total_seconds() == 90 * 60
try:
    timezone("Not/AZone")
except UnknownTimeZoneError:
    pass
```

`FixedOffset(minutes: int) -> datetime.tzinfo` returns a cached fixed-offset
timezone. Its offset is exactly `minutes`, and its `zone` label is stable.
`UTC` is an alias of `utc`. Export `UnknownTimeZoneError`,
`AmbiguousTimeError`, and `NonExistentTimeError` from the root package and
preserve their exception identity and useful string representations.

## Supporting module imports

```python
from pytz.lazy import LazyDict, LazyList
from pytz.tzfile import build_tzinfo
from pytz.tzinfo import BaseTzInfo, DstTzInfo, StaticTzInfo
```

The public compatibility modules `pytz.lazy`, `pytz.tzfile`, and
`pytz.tzinfo` must be importable. `build_tzinfo(zone: str, fileobj)` reads a
bundled tzfile stream and constructs the appropriate timezone object; resource
lookup and parsing remain local. Lazy collections must preserve their mapping
or sequence behavior and deterministic iteration once loaded.

# Implementation Notes

- Keep zone resource lookup relative to the installed `pytz` package.
- Preserve timezone object caching without sharing mutable state between
  unrelated resource parsers.
- Use aware/naive checks and the exact public exception classes for DST gaps
  and overlaps; do not silently choose an occurrence for `is_dst=None`.
- Package data must be included in normal and editable installs.
- The separate JSON-lines verifier invokes the package in a child process and
  does not provide test fixtures, a reference package, or network access.

# Examples

```python
from datetime import datetime
from pytz import timezone

zone = timezone("Europe/London")
summer = zone.localize(datetime(2024, 7, 1, 9, 30))
winter = zone.localize(datetime(2024, 1, 1, 9, 30))
assert summer.utcoffset() != winter.utcoffset()
```

```python
from datetime import datetime
from pytz import timezone, AmbiguousTimeError

zone = timezone("US/Eastern")
try:
    zone.localize(datetime(2024, 11, 3, 1, 30), is_dst=None)
except AmbiguousTimeError:
    pass
```

# Error Handling and Boundary Conditions

- Empty or unknown zone names raise `UnknownTimeZoneError`.
- A DST overlap with `is_dst=None` raises `AmbiguousTimeError`.
- A DST gap with `is_dst=None` raises `NonExistentTimeError`.
- Fixed offsets use minutes exactly, including negative values supported by the
  public contract; repeated lookup returns the same cached object.
- Resource absence, malformed tzfile data, and invalid datetime state must
  raise the documented package or standard-library exception rather than
  falling back to host `/usr/share/zoneinfo` data.
