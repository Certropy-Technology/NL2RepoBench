# ISO 8601 Date Parsing Library

Create an installable Python package named `iso8601` in the empty workspace. The package must be usable on Python 3.12 without network access at runtime and must expose the public API described below from both `iso8601` and its implementation module where noted.

## Project Description

Implement a small, dependency-light parser for common ISO 8601 calendar dates and date-times. The library returns standard-library `datetime.datetime` values, including fixed-offset timezone objects when an offset is present. It must preserve predictable behavior for reduced-precision dates, fractional seconds, timezone defaults, invalid input, and round trips through `datetime.isoformat()`.

## Supports

- Provide normal Python packaging metadata so `python -m pip install <project> --target <dir> --no-deps --no-build-isolation` succeeds from the project root.
- The import package is `iso8601`; include package metadata sufficient for an ordinary wheel or source installation.
- Runtime behavior must use only the Python standard library. The package must not require network access or a service.
- Public package exports are `parse_date`, `is_iso8601`, `ParseError`, `UTC`, and `FixedOffset`.

## API Usage Guide

### `iso8601.parse_date(datestring, default_timezone=datetime.timezone.utc)`

Accept a string in the supported ISO 8601 forms and return a `datetime.datetime`. Accepted forms include `YYYY`, `YYYY-MM`, dashed or compact `YYYY-MM-DD`/`YYYYMMDD`, and a time separated by `T` or a space. A time may contain hour only, hour and minute, or hour, minute, and second; separators between time fields may be present or omitted. Fractional seconds may use `.` or `,` and are converted to microseconds, truncated to the precision supported by `datetime`.

Accept timezone `Z`, signed hour offsets, signed hour-minute offsets with or without a colon, or no timezone. `Z` always means the exported `UTC` object. When no timezone is present, use `default_timezone`; when it is `None`, return a naive datetime. Preserve the correct offset and a conventional `+HH:MM`/`-HH:MM` timezone name for parsed offsets.

Raise the exported `ParseError` (a `ValueError` subclass) for strings that do not match the supported grammar or that cannot construct a valid `datetime`, including malformed separators and impossible calendar values. `is_iso8601` must return `False` for malformed strings, while `parse_date` raises.

For compatibility, the implementation module `iso8601.iso8601` must also provide a compiled `ISO8601_REGEX` object whose `.match()` recognizes supported complete strings; this helper is not required as a package-root export. Grammar failures should use an error message beginning with `Unable to parse date string`.

### `iso8601.is_iso8601(datestring)`

Return a boolean indicating whether the complete input string matches the supported ISO 8601 grammar. Do not accept trailing characters or an alternate separator such as `X`.

### `iso8601.FixedOffset(offset_hours, offset_minutes, name)`

Return a `datetime.timezone` with the requested hour/minute offset and the supplied display name. Equal offsets compare equal to equivalent standard-library timezone values.

### `iso8601.UTC` and `iso8601.ParseError`

`UTC` is the UTC timezone singleton used for `Z` and the default timezone. `ParseError` is the documented exception type for parsing failures.

## Implementation Notes

Keep the public behavior deterministic and compatible with `datetime`: parsed values should compare equal to expected `datetime` instances, support `deepcopy` and `pickle`, and round-trip through `parse_date(parsed.isoformat())` for valid aware values. The exact internal regular expression and module organization are up to you; do not add unrelated command-line behavior.
