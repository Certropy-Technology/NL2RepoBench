# Build `pendulum`

## Project Description

Create a complete, installable Python distribution named `pendulum`, version
`3.2.0`, from an empty workspace. The package provides timezone-aware date,
time, datetime, duration, interval, parsing, formatting, localization, and
controlled time-travel APIs while remaining compatible with the standard
library's `date`, `time`, `datetime`, `timedelta`, `tzinfo`, and `zoneinfo`
types.

The implementation must be self-contained. Do not depend on a preinstalled
copy of Pendulum, fetch source code, or contact a network service at runtime.
A pure-Python implementation is acceptable; the upstream native parser is an
implementation detail, not a required public interface.

## Supports

- CPython 3.12 on Linux, with support for Python 3.10 and newer where practical.
- An installable project exposing the `pendulum` package and distribution
  metadata version `3.2.0`.
- Exact runtime dependencies `python-dateutil==2.9.0.post0`, `six==1.17.0`, and
  `tzdata==2026.3`; they are preinstalled by the evaluation image.
- Standard IANA timezone names through `zoneinfo`, including daylight-saving
  transitions. `UTC` is the default timezone for constructed datetimes.
- Locale-backed formatting and humanized differences for the documented locale
  codes. At minimum, English, French, and Ukrainian behavior described below
  must work.
- Deterministic, offline operation. Ordinary package APIs must not spawn
  subprocesses, open sockets, or write outside application-requested paths.
- `pyproject.toml` or an equivalent standards-compliant build configuration.
  Installation is performed with build isolation disabled and without
  dependency resolution, so every build backend must come from the declared
  closure.

## API Usage Guide

The package root re-exports `Date`, `Time`, `DateTime`, `Duration`, `Interval`,
`Timezone`, `FixedTimezone`, `Formatter`, `WeekDay`, `UTC`, weekday constants
`MONDAY` through `SUNDAY`, transition constants `PRE_TRANSITION`,
`POST_TRANSITION`, and `TRANSITION_ERROR`, and the constructors and helpers
below.

### Constructors and conversion

```python
pendulum.datetime(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0,
    second: int = 0, microsecond: int = 0,
    tz: str | float | datetime.tzinfo | Timezone | FixedTimezone | None = UTC,
    fold: int = 1, raise_on_unknown_times: bool = False,
) -> DateTime
pendulum.local(year, month, day, hour=0, minute=0, second=0, microsecond=0) -> DateTime
pendulum.naive(year, month, day, hour=0, minute=0, second=0, microsecond=0, fold=1) -> DateTime
pendulum.date(year: int, month: int, day: int) -> Date
pendulum.time(hour: int, minute: int = 0, second: int = 0, microsecond: int = 0) -> Time
pendulum.instance(obj: datetime | date | time, tz=UTC) -> DateTime | Date | Time
pendulum.from_timestamp(timestamp: int | float, tz=UTC) -> DateTime
pendulum.from_format(string: str, fmt: str, tz=UTC, locale: str | None = None) -> DateTime
```

`datetime()` returns an aware value by default. Pass `tz=None` or use
`naive()` for a naive value. A timezone string is resolved as an IANA name;
`"local"` selects the configured local timezone. A numeric timezone value is a
fixed offset in seconds. Invalid calendar fields raise the same `ValueError`
subclasses/messages expected from standard datetime construction. Unknown
timezone names raise `pendulum.tz.exceptions.InvalidTimezone`.

Skipped and repeated local times honor `fold`. By default, a skipped time is
normalized to the post-transition instant and a repeated time uses the
post-transition occurrence. With `raise_on_unknown_times=True`, skipped times
raise `NonExistingTime` and repeated times raise `AmbiguousTime`.

```python
>>> pendulum.datetime(2024, 2, 29, 12, 30, tz="Europe/Paris").to_iso8601_string()
'2024-02-29T12:30:00+01:00'
>>> pendulum.datetime(2013, 3, 31, 2, 30, tz="Europe/Paris")
DateTime(2013, 3, 31, 3, 30, 0, tzinfo=Timezone('Europe/Paris'))
```

### Current time and parsing

```python
pendulum.now(tz: str | Timezone | None = None) -> DateTime
pendulum.today(tz: str | Timezone = "local") -> DateTime
pendulum.tomorrow(tz: str | Timezone = "local") -> DateTime
pendulum.yesterday(tz: str | Timezone = "local") -> DateTime
pendulum.parse(text: str, **options) -> Date | Time | DateTime | Duration | Interval
```

`parse()` accepts ISO-8601 dates, times, datetimes, durations, and intervals.
`exact=True` preserves the narrowest type (`Date` or `Time`) instead of
promoting it to `DateTime`. `strict=True` rejects non-ISO fallback formats.
`tz=` supplies the timezone for input without an offset. Invalid text raises
`pendulum.parsing.exceptions.ParserError`.

### `Date`, `Time`, and `DateTime`

These classes subclass their standard-library counterparts. Their
constructors, comparisons, hashing, pickling, `replace()`, and arithmetic must
remain compatible with those base types. They additionally provide immutable,
fluent operations:

```python
value.add(years=0, months=0, weeks=0, days=0, hours=0, minutes=0,
          seconds=0, microseconds=0)
value.subtract(years=0, months=0, weeks=0, days=0, hours=0, minutes=0,
               seconds=0, microseconds=0)
value.set(**components)
value.start_of(unit: str)
value.end_of(unit: str)
value.next(day_of_week: WeekDay | None = None, keep_time: bool = False)
value.previous(day_of_week: WeekDay | None = None, keep_time: bool = False)
value.diff(other=None, abs: bool = True) -> Interval | Duration
value.diff_for_humans(other=None, absolute=False, locale=None, separator=" ") -> str
value.format(fmt: str, locale: str | None = None) -> str
```

Supported boundary units include `second`, `minute`, `hour`, `day`, `week`,
`month`, `quarter`, `year`, `decade`, and `century` where meaningful. Calendar
arithmetic clamps an invalid target day to the final day of the target month;
adding one month to January 31 therefore yields the final day of February.
Datetime arithmetic preserves timezone rules across DST changes rather than
blindly adding an offset.

With no weekday argument, `next()` and `previous()` move to the next or
previous occurrence of the value's current weekday, one week away. Supplying a
weekday chooses that weekday explicitly. Unless `keep_time=True`, these
operations return the start of the selected day.

`DateTime` exposes `int_timestamp`, `float_timestamp`, `offset`,
`offset_hours`, `timezone`, `timezone_name`, `is_local()`, `is_utc()`,
`is_dst()`, `date()`, `time()`, `naive()`, `in_timezone()` (alias `in_tz()`),
and string helpers `to_date_string()`, `to_time_string()`,
`to_datetime_string()`, `to_iso8601_string()`, `to_atom_string()`,
`to_cookie_string()`, `to_rfc822_string()`, `to_rfc850_string()`,
`to_rfc1036_string()`, `to_rfc1123_string()`, `to_rfc2822_string()`,
`to_rfc3339_string()`, `to_rss_string()`, and `to_w3c_string()`.

### Durations and intervals

```python
pendulum.duration(days=0, seconds=0, microseconds=0, milliseconds=0,
                  minutes=0, hours=0, weeks=0, years=0, months=0) -> Duration
pendulum.interval(start: DateTime, end: DateTime, absolute: bool = False) -> Interval
```

`Duration` subclasses `timedelta` while preserving separate calendar `years`
and `months`. It supports normal timedelta arithmetic and exposes
`years`, `months`, `weeks`, `days`, `remaining_days`, `hours`, `minutes`,
`seconds`, `remaining_seconds`, `microseconds`, `total_minutes()`,
`total_hours()`, `total_days()`, `total_weeks()`, `in_weeks()`, `in_days()`,
`in_hours()`, `in_minutes()`, `in_seconds()`, `in_words(locale=None,
separator=" ")`, and `as_timedelta()`.

`Interval` is a `Duration` with immutable `start` and `end` endpoints. It
supports containment, iteration, arithmetic, `range(unit, amount=1)`,
`as_duration()`, and localized `in_words()`. A forward range includes its
start and advances by the requested positive amount without stepping beyond
the end.

### Timezones, locale, and formatting

```python
pendulum.timezone(name: str | int) -> Timezone | FixedTimezone
pendulum.fixed_timezone(offset: int) -> FixedTimezone
pendulum.local_timezone() -> Timezone | FixedTimezone
pendulum.timezones() -> set[str]
pendulum.set_locale(name: str) -> None
pendulum.get_locale() -> str
pendulum.locale(name: str) -> Locale
pendulum.week_starts_at(wday: WeekDay) -> None
pendulum.week_ends_at(wday: WeekDay) -> None
```

Timezone objects implement `tzinfo`, `convert()`, `utcoffset()`, `dst()`, and
`tzname()`. Equal named/fixed zones compare and hash consistently. `set_locale`
and week-boundary helpers update process-local package state and reject unknown
locale names or weekday values outside Monday through Sunday. Formatting uses
Pendulum tokens such as `YYYY`, `MM`, `DD`, `HH`, `mm`, `ss`, `SSSSSS`, `Z`,
`ZZ`, `dddd`, and escaped literals in square brackets. Locale-specific month,
weekday, relative-time, and unit strings must be deterministic.

### Controlled time travel

```python
pendulum.travel_to(dt: DateTime, freeze: bool = False) -> Traveller
pendulum.travel(*, years=0, months=0, weeks=0, days=0, hours=0,
                minutes=0, seconds=0, microseconds=0, freeze=False) -> Traveller
pendulum.freeze() -> Traveller
```

Each helper returns a context manager/decorator backed by `time-machine` when
that optional dependency is installed. It affects `pendulum.now()` only for
the context's lifetime and restores the previous clock even when the body
raises. Without `time-machine`, entering the context raises `NotImplementedError`.

## Implementation Notes

Keep locale and timezone data available from the installed distribution; do
not assume the source tree remains present. Avoid host locale settings and
wall-clock assertions in deterministic operations. Calendar objects are not
directly JSON serializable, so the scored verifier invokes documented API
sequences in an isolated child process and returns only normalized strings,
numbers, booleans, lists, dictionaries, and exception names. Native object
identity, callback objects, arbitrary `tzinfo` subclasses, private helpers,
filesystem probing, and platform-specific local-time discovery are outside the
scored boundary.

Do not include upstream tests, verifier code, reference source, or build caches
in the generated repository.
