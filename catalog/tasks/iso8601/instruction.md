# ISO 8601 Date Parsing Library

Create an installable Python package named `iso8601` in the empty workspace. The package must be usable on Python 3.12 without network access at runtime and must expose the public API described below from both `iso8601` and its implementation module where noted.

## Project Description

Implement a small, dependency-light parser for common ISO 8601 calendar dates and date-times. The library returns standard-library `datetime.datetime` values, including fixed-offset timezone objects when an offset is present. It must preserve predictable behavior for reduced-precision dates, fractional seconds, timezone defaults, invalid input, and round trips through `datetime.isoformat()`.

## Natural Language Instruction

Create the `iso8601` package from an empty `workspace/`. Implement the public
date parser, grammar predicate, UTC and fixed-offset timezone helpers, and
public parsing exception described in this document. Keep the package usable
through both its root exports and the documented compatibility module. Preserve
the distinction between syntax validation and datetime construction, and keep
all accepted forms deterministic under repeated calls and different process
hash seeds. Do not add a network client, command-line service, or dependency
outside the declared standard-library runtime.

## Supports

- Provide normal Python packaging metadata so `python -m pip install <project> --target <dir> --no-deps --no-build-isolation` succeeds from the project root.
- The import package is `iso8601`; include package metadata sufficient for an ordinary wheel or source installation.
- Runtime behavior must use only the Python standard library. The package must not require network access or a service.
- Public package exports are `parse_date`, `is_iso8601`, `ParseError`, `UTC`, and `FixedOffset`.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── iso8601/
│   ├── __init__.py
│   ├── iso8601.py
│   └── py.typed
└── README.md
```

The package root must re-export the five public names listed above. The
compatibility module `iso8601.iso8601` contains `ISO8601_REGEX` and
`parse_timezone`; these helpers need not be re-exported from `__init__.py`.
Packaging metadata must describe version `2.1.0`, Python `>=3.7,<4.0`, and the
`poetry-core` build backend without declaring standard-library modules as
runtime dependencies.

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

## Examples

```python
from iso8601 import UTC, parse_date

value = parse_date("2024-03-15T12:30:45Z")
assert value.tzinfo is UTC
```

```python
from iso8601 import parse_date

aware = parse_date("20240315 123045+0530")
assert aware.utcoffset().total_seconds() == 19800
```

```python
from iso8601 import parse_date

naive = parse_date("2024-03", default_timezone=None)
assert naive.tzinfo is None
```

## Error Handling and Boundary Conditions

`parse_date` must reject impossible months, days, malformed separators,
trailing characters, invalid offsets, and unsupported timezone text with the
exported `ParseError`. A valid grammar match that cannot construct a calendar
value is also a `ParseError`, not a raw `ValueError`. `is_iso8601` returns a
boolean and never turns a malformed or trailing input into a partial match.
Fractional seconds longer than microsecond precision are truncated in the
documented direction, and comma and dot fractions have equivalent meaning.
The `default_timezone=None` boundary produces a naive value only when the
input has no explicit timezone; an explicit `Z` or signed offset always wins.

The public API accepts text strings, not bytes, arbitrary objects, or locale-
dependent date formats. A caller can inspect `value.tzinfo`, compare values
with standard-library `datetime`, and serialize them without package-specific
wrappers. Parsing never performs I/O and never mutates module-global timezone
state. The implementation may use a compiled regular expression internally,
but `ISO8601_REGEX.match(text)` must represent a complete supported input and
must not silently accept a valid prefix followed by junk.

Timezone offsets must remain within the representable ISO 8601 range and use
the supplied display name when created through `FixedOffset`. Standard-library
timezone equality, copying, and pickling are observable compatibility
requirements, so do not return a mutable custom timezone surrogate.
