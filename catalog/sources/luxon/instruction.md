# Project Description

Build an installable npm package named `luxon`, version `3.7.2`, from an empty
workspace. The package provides a deterministic, JSON-compatible slice of the
public Luxon date-time API described below. It must work on Node.js 24 in a
network-isolated runtime and preserve both CommonJS and ESM package entry
points.

The evaluator calls the public package through a subprocess JSON transport.
That transport is part of the verifier, not part of the requested package. Do
not add a bridge, server, CLI, or task-specific evaluation entry point.

# Supports

- Use Node.js 24.19.0 and npm 11.17.0.
- Provide a `package.json` with `name: "luxon"`, `version: "3.7.2"`, and
  `license: "MIT"`.
- Commit an npm lockfile with `lockfileVersion: 3`.
- Do not require runtime dependencies, lifecycle scripts, native addons,
  loaders, registry configuration, or network access.
- Export the package root through both `require("luxon")` and ESM import.
- Export `VERSION`, `DateTime`, `Duration`, `Interval`, `Info`, `Zone`,
  `FixedOffsetZone`, `IANAZone`, `InvalidZone`, `SystemZone`, and `Settings`.
  `VERSION` is the string `"3.7.2"`; the other exports are constructors or
  static API classes.

# API Usage Guide

Every scored input is JSON-compatible. Dates are supplied as ISO strings,
durations as unit objects or ISO duration strings, and intervals as ISO
interval strings or endpoint pairs. An API that creates an invalid Luxon value
returns that invalid value unless the contract below explicitly says it
throws. Invalid values expose `isValid: false`, an `invalidReason`, and `null`
for ISO serialization.

## DateTime

The following constructors are required:

- `DateTime.fromISO(text, options = {})` parses an ISO date or date-time.
- `DateTime.fromObject(values, options = {})` constructs calendar fields.
  Supported numeric fields are `year`, `month`, `day`, `hour`, `minute`,
  `second`, and `millisecond`.
- `DateTime.fromMillis(milliseconds, options = {})` constructs a Unix
  millisecond instant from a finite number.

The supported constructor option keys are `zone`, `setZone`, `locale`, and
`numberingSystem`. A zone may be `"utc"`, `"local"`, a fixed offset such as
`"UTC+5:30"`, or an IANA zone such as `"America/New_York"`. With `setZone:
true`, an offset parsed from the input is retained rather than converted to the
requested/default zone.

The required immutable instance operations are:

- `set(values)` replaces selected calendar fields.
- `setZone(zone, options = {})` changes the zone; `keepLocalTime` is supported.
- `plus(durationLike)` and `minus(durationLike)` perform calendar arithmetic.
- `startOf(unit)` and `endOf(unit)` accept `year`, `quarter`, `month`, `week`,
  `day`, `hour`, `minute`, or `second`.
- `diff(other, units, options = {})` returns a `Duration`; `units` is a unit
  string or an array of unit strings.
- `hasSame(other, unit)` compares calendar membership in the requested unit.
- `equals(other)` compares the instant, zone, and locale configuration.
- `toISO(options = {})`, `toISODate(options = {})`, and
  `toISOTime(options = {})` serialize the value. Supported ISO options are
  `includeOffset`, `suppressMilliseconds`, and `extendedZone` where applicable.
- `toFormat(format, options = {})` supports ordinary Luxon tokens including
  `yyyy`, `LL`, `dd`, `HH`, `mm`, `ss`, `ZZ`, and `ZZZ`.
- `toObject(options = {})` returns numeric calendar fields.
- `toMillis()` returns Unix milliseconds, or `NaN` for an invalid value.

The readable DateTime properties are `isValid`, `invalidReason`, `zoneName`,
`offset`, `year`, `month`, `day`, `hour`, `minute`, `second`, and
`millisecond`. Calendar operations clamp or cross month and leap-year
boundaries as Luxon does and never mutate the receiver.

`DateTime.now()`, `DateTime.local()`, and default-zone behavior are outside the
scored slice because they depend on the host clock or timezone.

## Duration

The following constructors are required:

- `Duration.fromObject(values, options = {})` accepts numeric `years`,
  `quarters`, `months`, `weeks`, `days`, `hours`, `minutes`, `seconds`, and
  `milliseconds` fields.
- `Duration.fromISO(text, options = {})` parses ISO 8601 durations, including a
  leading sign and fractional seconds.
- `Duration.fromMillis(value, options = {})` constructs a millisecond duration.

The required immutable operations are `plus(durationLike)`,
`minus(durationLike)`, `negate()`, `normalize()`, `rescale()`,
`shiftTo(...units)`, `as(unit)`, and `equals(other)`. `normalize()` carries
values between adjacent units while preserving the represented duration;
`rescale()` additionally shifts to conventional ranges and removes zero units.
Months and years must not be treated as fixed millisecond counts where Luxon
uses calendar-aware conversion.

Serialization operations are `toObject()`, `toISO()`, `toISOTime()`,
`toFormat(format, options = {})`, and `toMillis()`. Readable properties are
`isValid`, `invalidReason`, `years`, `months`, `weeks`, `days`, `hours`,
`minutes`, `seconds`, and `milliseconds`.

## Interval

Intervals are half-open: the start belongs to the interval and the end does
not. Endpoint order is preserved. The following constructors are required:

- `Interval.fromDateTimes(start, end)` accepts two DateTimes.
- `Interval.fromISO(text, options = {})` parses two ISO endpoints.
- `Interval.after(start, durationLike)` and
  `Interval.before(end, durationLike)` construct a relative interval.

The required query and relation operations are `length(unit)`, `count(unit)`,
`contains(dateTime)`, `isAfter(dateTime)`, `isBefore(dateTime)`,
`overlaps(other)`, `abutsStart(other)`, `abutsEnd(other)`, `engulfs(other)`,
and `equals(other)`. `count(unit)` counts calendar sections touched rather than
returning fractional elapsed units.

The required transformation and serialization operations are
`intersection(other)`, `union(other)`, `splitBy(durationLike)`,
`divideEqually(numberOfParts)`, `toDuration(unit)`, `toISO()`, and
`toFormat(format, options = {})`. The supported `toFormat` option is
`separator`. Readable observations include `isValid`, `isEmpty()`, `start`,
and `end`.

## Info and fixed-offset zones

`Info.months(length, options)`, `Info.weekdays(length, options)`,
`Info.meridiems(options)`, and `Info.eras(length, options)` return localized
arrays. `length` is `"long"`, `"short"`, or `"narrow"` where the public API
accepts it. Results for an explicit `locale: "en-US"` must be deterministic.

`FixedOffsetZone.instance(offsetMinutes)` creates a fixed-offset zone.
`FixedOffsetZone.parseSpecifier(text)` accepts forms such as `"UTC+5:30"` and
returns a zone or `null`. The resulting zone exposes `name`, `type`,
`isUniversal`, `isValid`, `offsetName(timestamp, options)`,
`formatOffset(timestamp, format)`, `offset(timestamp)`, and `equals(other)`.

# Implementation Notes

- Preserve Luxon's immutable-object model; operations return new values and do
  not mutate their receivers.
- Keep calculations deterministic for explicit inputs. Do not hard-code the
  examples or substitute incomplete timezone tables.
- Preserve invalid-value behavior rather than converting invalid inputs into
  plausible dates or unrelated exceptions.
- Include generated package entry output in the packed npm artifact so both
  module systems work without a build step after installation.
- Browser bundles, source maps, documentation generation, callbacks, custom
  classes, direct `Date` objects, development tooling, and locale behavior
  outside the explicit `en-US` calls are outside the scored slice.
