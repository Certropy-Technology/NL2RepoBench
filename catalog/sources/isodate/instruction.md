# Project Description

Implement the installable Python package `isodate`, an ISO 8601 date, time,
datetime, duration, timezone, and formatting library. Work from an empty
workspace and keep the runtime dependency-free. The package must support Python
3.12 on Linux and must not require network access, a service, or a command-line
interface at runtime.

# Supports

- Use a normal PEP 517 project layout with the import package `isodate`.
- Set `isodate.__version__` to `"0.7.3.dev3+g17cb25eb7"`.
- Re-export the documented parsing and formatting functions, `Duration`,
  `ISO8601Error`, `UTC`, `LOCAL`, `FixedOffset`, and all format constants from
  `isodate`.
- Keep parsing and formatting deterministic. Syntax that does not match a
  supported ISO representation raises `ISO8601Error`; values rejected by a
  standard-library constructor may propagate `ValueError` or `OverflowError`.
- Preserve standard-library value semantics, including timezone offsets,
  equality, hashing, arithmetic, `repr`, pickle, and deepcopy behavior.
- The evaluation image already contains build dependencies. Do not install
  packages or access the network from the evaluation workspace.

# API Usage Guide

## Dates, times, and datetimes

`isodate.parse_date(datestring: str, yeardigits: int = 4, expanded: bool = False,
defaultmonth: int = 1, defaultday: int = 1) -> datetime.date` accepts complete
calendar dates, reduced-precision year/month forms, ordinal dates, and ISO week
dates in basic or extended notation. Missing month/day components use the two
defaults. For example, `parse_date("2012-05", defaultday=17)` is
`date(2012, 5, 17)`, `parse_date("2012-060")` is leap day, and
`parse_date("2012-W01-1")` is `date(2012, 1, 2)`.

`isodate.parse_time(timestring: str) -> datetime.time` accepts basic or extended
hour, minute, and second forms, decimal fractions introduced by `.` or `,`, and
`Z` or signed hour/minute offsets. Decimal fractions are truncated to six
microsecond digits. Examples include `"123045"`, `"12:30"`,
`"12:30:45.5"`, and `"12:30:00+0230"`.

`isodate.parse_datetime(datetimestring: str) -> datetime.datetime` combines any
supported date and time separated by uppercase `T`. A space is not a substitute
for `T`. `"2012-05-29T12:30:45Z"` produces an aware datetime whose offset is
zero.

The inverse formatters have these signatures:

- `date_isoformat(tdate, format: str = DATE_EXT_COMPLETE, yeardigits: int = 4) -> str`
- `time_isoformat(ttime, format: str = TIME_EXT_COMPLETE + TZ_EXT) -> str`
- `datetime_isoformat(tdt, format: str = DT_EXT_COMPLETE) -> str`

They accept the corresponding `datetime` value and apply the supplied isodate
format string. Default examples are `"2012-05-29"`, `"12:30:45"`, and
`"2012-05-29T12:30:45Z"` for an aware datetime using `isodate.UTC`.

## Durations

`isodate.parse_duration(datestring: str, as_timedelta_if_possible: bool = True)
-> datetime.timedelta | isodate.Duration` accepts ISO duration syntax, including
an optional leading minus sign and week notation. It returns `timedelta` when the
value has no calendar years or months and conversion is allowed; otherwise it
returns `Duration`. Thus `parse_duration("P2W") == timedelta(days=14)`, while
`parse_duration("P1Y2M3DT4H5M6S")` retains its year and month fields.

`isodate.Duration(days=0, seconds=0, microseconds=0, milliseconds=0,
minutes=0, hours=0, weeks=0, months=0, years=0)` stores `years`, `months`, and a
`tdelta` for the remaining units. It supports equality, hashing, unary negation,
integer multiplication, and compatible addition/subtraction with `Duration`,
`timedelta`, `date`, and `datetime`. Operations involving only fixed units may
return a standard `timedelta`. Calendar addition clips the day when necessary,
so adding one month to `date(2020, 1, 31)` yields `date(2020, 2, 29)`.

`Duration.totimedelta(start: date | datetime | None = None, end: date | datetime
| None = None) -> timedelta` resolves years and months relative to exactly one
endpoint. Supplying neither endpoint for a calendar duration, or supplying both,
raises `ValueError`.

`duration_isoformat(tduration, format: str = D_DEFAULT) -> str` formats either
duration representation. For example, a two-day, three-second `timedelta`
formats as `"P2DT3S"`.

## Timezones and general formatting

`parse_tzinfo(tzstring: str) -> datetime.tzinfo | None` parses `Z` and signed
offsets; an empty timezone component returns `None`. `Z` returns the singleton
`UTC`. `tz_isoformat(dt: datetime, format: str = TZ_EXT) -> str` formats the
timezone attached to a datetime, such as `"-05:00"`.

`isodate.tzinfo.Utc`, `isodate.tzinfo.FixedOffset(offset_hours: float = 0,
offset_minutes: float = 0, name: str = "UTC")`, and
`isodate.tzinfo.LocalTimezone` implement the `datetime.tzinfo` protocol.
`isodate.UTC` and `isodate.LOCAL` are singleton instances; `FixedOffset` is also
re-exported at package level. Offset and name methods return deterministic
`timedelta` and string values.

`strftime(tdt, format: str, yeardigits: int = 4) -> str` is the common formatter
used by the public helpers. Unlike platform `strftime`, it must format supported
years before 1900 consistently.

The package re-exports these format constants with the exact values shown:

```text
DATE_BAS_COMPLETE=%Y%m%d       DATE_EXT_COMPLETE=%Y-%m-%d
DATE_BAS_ORD_COMPLETE=%Y%j     DATE_EXT_ORD_COMPLETE=%Y-%j
DATE_BAS_WEEK=%YW%W            DATE_EXT_WEEK=%Y-W%W
DATE_BAS_WEEK_COMPLETE=%YW%W%w DATE_EXT_WEEK_COMPLETE=%Y-W%W-%w
DATE_BAS_MONTH=%Y%m            DATE_EXT_MONTH=%Y-%m
DATE_YEAR=%Y                    DATE_CENTURY=%C
TIME_BAS_COMPLETE=%H%M%S       TIME_EXT_COMPLETE=%H:%M:%S
TIME_BAS_MINUTE=%H%M           TIME_EXT_MINUTE=%H:%M
TIME_HOUR=%H                    TZ_BAS=%z
TZ_EXT=%Z                       TZ_HOUR=%h
DT_BAS_COMPLETE=%Y%m%dT%H%M%S%z
DT_EXT_COMPLETE=%Y-%m-%dT%H:%M:%S%Z
DT_BAS_ORD_COMPLETE=%Y%jT%H%M%S%z
DT_EXT_ORD_COMPLETE=%Y-%jT%H:%M:%S%Z
DT_BAS_WEEK_COMPLETE=%YW%W%wT%H%M%S%z
DT_EXT_WEEK_COMPLETE=%Y-W%W-%wT%H:%M:%S%Z
D_DEFAULT=P%P                   D_WEEK=P%p
D_ALT_BAS=P%Y%m%dT%H%M%S       D_ALT_EXT=P%Y-%m-%dT%H:%M:%S
D_ALT_BAS_ORD=P%Y%jT%H%M%S     D_ALT_EXT_ORD=P%Y-%jT%H:%M:%S
```

# Implementation Notes

- Keep the documented `isodate.*` module names, signatures, re-exports, and
  return types. The implementation may use only the Python standard library.
- Timezone and duration values must remain pickleable and deepcopyable.
- Do not copy hidden tests or rely on the reference source being reachable at
  runtime.
- The verifier observes candidate behavior through an unprivileged child
  process. Trusted collection, JUnit, reward, and network receipts remain
  separate from candidate code.
