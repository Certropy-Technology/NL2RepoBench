# Build `tzlocal`

Create a complete, installable Python distribution named `tzlocal` from an empty workspace. The package must discover the operating system's configured local time zone and return standard-library `zoneinfo.ZoneInfo` objects. Keep the implementation local and deterministic: it must not download source code, query a remote service, or depend on the reference package being preinstalled.

## Project Description

The import package is `tzlocal`. The frozen distribution version is `5.4.5.dev0`. Use a normal PEP 517 build configured by `pyproject.toml`; the evaluator installs the project from the workspace without Git metadata. The implementation uses the standard library's `zoneinfo` support and must include a `tzlocal/py.typed` marker.

The evaluator runs CPython 3.12 on Linux. The upstream package supports Python 3.10 and newer on Unix-like systems and Windows. On Windows, the distribution may declare the conditional dependency `tzdata; platform_system == "Windows"`; on Linux it has no third-party runtime dependency. The project is MIT licensed.

## Natural Language Instruction

Create the installable `tzlocal` package from an empty workspace. Implement
local-zone discovery, independent caches, reload behavior, Unix configuration
parsing, Windows compatibility modules, and offset validation using standard
library `zoneinfo` objects.

## Supports

- Python 3.10 and newer, with the evaluator using CPython 3.12 on Linux.
- Ordinary `pip install .` through a PEP 517 wheel build with no `.git` directory and no build-time network access.
- `TZ` environment values written as IANA names, names prefixed by `:`, or absolute paths to TZif files.
- Cached local-zone and local-zone-name lookups, plus an explicit reload operation after system or environment changes.
- Unix configuration discovery and Windows time-zone mapping without replacing `zoneinfo.ZoneInfo` with a third-party timezone type.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── tzlocal/
    ├── __init__.py
    ├── unix.py
    ├── utils.py
    ├── win32.py
    ├── windows_tz.py
    └── py.typed
```

## API Usage Guide

### `tzlocal.get_localzone() -> zoneinfo.ZoneInfo`

Import path: `from tzlocal import get_localzone`. It takes no arguments and returns the configured local timezone as a `zoneinfo.ZoneInfo` object. The first successful result is cached. Later changes to `TZ` or operating-system configuration do not change this function's result until `reload_localzone()` is called.

When `TZ` contains an IANA key such as `"Africa/Harare"` or `":Africa/Harare"`, return the corresponding `ZoneInfo` with that key. When `TZ` is an absolute existing TZif file, load that file and use a recognizable zone key when the path identifies one. A missing or unsupported value, including POSIX-style strings such as `"GMT+03:00"`, raises `zoneinfo.ZoneInfoNotFoundError` rather than silently inventing a fixed offset.

### `tzlocal.get_localzone_name() -> str`

Import path: `from tzlocal import get_localzone_name`. It takes no arguments and returns the configured IANA timezone name when one can be identified. Its name cache is independent from the timezone-object cache. A leading `:` in `TZ` is ignored. An absolute path under a zoneinfo tree should be reduced to its IANA name when possible.

On Unix, when `TZ` is absent, consult conventional timezone configuration in a deterministic order. Relevant sources include `/etc/timezone`, `/var/db/zoneinfo`, `ZONE` or `TIMEZONE` entries in distribution clock files, and `/etc/localtime`. Conflicting explicit configurations must raise `ZoneInfoNotFoundError` with useful diagnostics instead of choosing arbitrarily. On Windows, map the configured Windows registry timezone name to its IANA equivalent.

### `tzlocal.reload_localzone() -> zoneinfo.ZoneInfo`

Import path: `from tzlocal import reload_localzone`. It takes no arguments, refreshes both caches from the current environment and operating-system configuration, and returns the newly selected `ZoneInfo`. After a successful reload, `get_localzone()` and `get_localzone_name()` must describe the same current zone.

### `tzlocal.assert_tz_offset(tz, error=True)`

Import path: `from tzlocal import assert_tz_offset`. `tz` is a timezone object whose current UTC offset can be computed. The function compares that offset with the process's current system offset and returns `None` when they agree within one minute. If they differ by more than one minute, the default `error=True` raises `ValueError` with both offsets in the message. With `error=False`, emit a `UserWarning` carrying the same diagnostic and return `None`.

### Package exports and compatibility modules

The root package's `__all__` is, in order, `get_localzone`, `get_localzone_name`, `reload_localzone`, and `assert_tz_offset`. The compatibility modules `tzlocal.unix`, `tzlocal.utils`, `tzlocal.win32`, and `tzlocal.windows_tz` remain importable on their applicable platforms. Distribution metadata must report name `tzlocal`, version `5.4.5.dev0`, and the conditional Windows-only `tzdata` requirement.

## Examples

```python
import tzlocal

zone = tzlocal.get_localzone()
assert zone is tzlocal.get_localzone()
```

```python
from zoneinfo import ZoneInfo
from tzlocal import assert_tz_offset

assert_tz_offset(ZoneInfo("UTC"), error=False) is None
```

## Error Handling and Boundary Conditions

Unsupported `TZ` values and genuine configuration conflicts raise
`ZoneInfoNotFoundError`; failed lookups are not cached. Missing configuration
warns before the documented UTC fallback, and `reload_localzone()` refreshes
both caches after a successful selection.

## Additional Contract Details

`get_localzone_name()` and `get_localzone()` have separate caches, so asking
for one does not implicitly populate or invalidate the other. `reload_localzone`
must observe an updated `TZ` value and make both accessors agree afterward.

An IANA key is passed to `ZoneInfo` unchanged after removing a leading colon.
Absolute TZif paths are read with `ZoneInfo.from_file`; their bytes are not
copied into package data. Configuration parsing ignores comments and blank
lines, but conflicting authoritative names are an error rather than a random
choice. A symlink to a zoneinfo file may be resolved when its path identifies a
known name.

The package must remain importable on platforms where only the applicable
compatibility module is usable. Public exports retain their declared order and
the implementation must not invoke a subprocess, install a package, or alter
the caller's environment. Warnings use standard `warnings` behavior and failed
discovery is never stored as a successful cache value.

The implementation should expose clear helper boundaries between Unix file
parsing, Windows registry mapping, and the public cache. A successful named
lookup returns a standard `ZoneInfo` whose `.key` matches the selected IANA
name. A loaded file zone may have no key, but it must still provide correct
UTC offsets. Use one-minute tolerance in `assert_tz_offset`, compare aware
datetimes in UTC, and include both observed offsets in any diagnostic.

## Implementation Notes

Read `TZ` before operating-system configuration. Keep the name cache and timezone-object cache separate, and refresh both in `reload_localzone()`. Do not cache a failed lookup. Use `ZoneInfo.from_file()` for absolute TZif files and `ZoneInfo(name)` for IANA keys.

Configuration files may be missing, empty, binary, malformed, symlinks, or mutually inconsistent. Ignore unreadable non-authoritative files, warn for malformed clock-file lines, and fail clearly for genuine conflicts. If Unix has no named configuration but has a localtime TZif file, return a `ZoneInfo` loaded from that file. If no timezone configuration exists at all, warn and fall back to UTC.

Do not add network calls, runtime package installation, subprocess-based source acquisition, or evaluator-specific shortcuts. The verifier imports candidate code only in bounded unprivileged child processes.
