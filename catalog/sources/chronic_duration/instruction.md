## Project Description

`chronic_duration` is a small natural-language parser for elapsed time. It turns
a human-readable duration string such as `4 hours and 30 minutes`, `3 mins 4
sec`, `2h20min`, or `1:20.51` into a number of seconds, and it renders a number
of seconds back into a human-readable duration string in one of several
formats. Results are integers unless the input contains a fractional value, in
which case a float is returned.

This task covers a deterministic, pure-Ruby subset of that behavior: word and
numeric duration parsing with all documented unit aliases, colon-separated
"chrono" input normalization, arithmetic across several units in one string,
the five output formats with their labels and pluralization rules, unit
truncation and joining during output, configurable day/week scaling, and the
documented invalid-input behavior (silent `nil`, or a raised error when
exceptions are enabled).

The implementation must be installable and usable without any upstream source
tree. It must work from an empty workspace, through `require
"chronic_duration"`, using only the offline Bundler dependency closure described
below. It must not contact network services, must not use native extensions, and
must not depend on the clock, the locale, the random number generator,
files outside the project, or a terminal.

## Natural Language Instruction (Prompt)

Please create a Ruby project named `chronic_duration` that implements the
documented Chronic Duration behavior. The project should include the following
functions:

1. Duration parsing: `ChronicDuration.parse(string, opts = {})` must normalize
   a duration string, total every recognized `<number> <unit>` term, and return
   the elapsed seconds, or `nil` when the normalized total is zero.
2. Unit vocabulary and arithmetic: every documented alias must resolve to its
   canonical unit, units must scale by the current `hours_per_day` and
   `days_per_week` settings, repeated terms must accumulate, and unrecognized
   words must be dropped.
3. Chrono input: a colon-separated numeric string such as `4:01:01` must be
   read right to left as `seconds`, `minutes`, `hours`, `days`, `months`,
   `years`, and must mix with ordinary words in the same string.
4. Numeric forms: decimal numbers (`2.5 hrs`), numbers glued to unit letters
   (`2h20min`), and English number words (`two hours and twenty minutes`) must
   all parse, and a fractional term must make the result a float.
5. Duration serialization: `ChronicDuration.output(seconds, opts = {})` must
   decompose a non-negative number of seconds into ordered units and render it
   in the `:default`, `:short`, `:long`, `:micro`, or `:chrono` format,
   honoring `:keep_zero`, `:units`, `:joiner`, `:weeks`, and `:limit_to_hours`.
6. Invalid-input contract: unparseable text returns `nil`; with
   `ChronicDuration.raise_exceptions = true`, unparseable text raises
   `ChronicDuration::DurationParseError` and ordinary valid text still parses.
7. Global settings: `raise_exceptions`, `hours_per_day`, and `days_per_week`
   must be readable and writable as module-level accessors with the documented
   defaults, and must affect parsing and output as specified.
8. Core file requirements: provide `Gemfile`, `Gemfile.lock`, and
   `lib/chronic_duration.rb` with the exact contents required by the
   Environment Configuration section, and make the package load with `require
   "chronic_duration"` on Ruby 3.4. Do not copy the upstream repository,
   upstream tests, verifier files, or reference source into the generated
   project.

Only the behavior named in this prompt and in the API Usage Guide is in scope.
Anything not described there is out of scope and is not exercised.

## Environment Configuration

### Ruby Version

The project is evaluated on MRI Ruby `3.4.10` with Bundler `2.6.9` on
Linux/amd64.

### Core Dependency Library Versions

```plain
ruby       3.4.10
bundler    2.6.9
numerizer  0.2.0
```

`numerizer` converts English number words to digits and is the only permitted
runtime dependency. It is available through a private, hash-verified offline
Bundler cache. The candidate's `Gemfile.lock` must use the official RubyGems
remote and resolve that exact version.

### Offline Packaging Contract

The verifier copies the workspace, validates `Gemfile.lock`, then installs with
Bundler in `--local` mode against the offline cache. Create the project's
`Gemfile` and `Gemfile.lock` with exactly these bytes:

```plain
# Gemfile
source "https://rubygems.org"
gem "numerizer", "0.2.0"
```

```plain
# Gemfile.lock
GEM
  remote: https://rubygems.org/
  specs:
    numerizer (0.2.0)

PLATFORMS
  ruby

DEPENDENCIES
  numerizer (= 0.2.0)

BUNDLED WITH
   2.6.9
```

Do not use a `GIT`, `PATH`, or plugin dependency source, do not use the
`gemspec` directive (the lock must contain only the `GEM` section above), do not
add any other gem, and do not use native extensions or runtime network access.
The Ruby standard library may be used freely, but standard-library modules are
not gems and must not be declared as dependencies. There is no preinstalled copy
of `chronic_duration`; the verifier loads the candidate's own `lib`.

### How The Candidate Is Executed

The verifier runs the candidate from a copy of the workspace at a different
absolute path, exports `BUNDLE_GEMFILE` pointing at that copy's `Gemfile` and
`BUNDLE_PATH` pointing at a verifier-owned bundle directory, prepends the
copy's `lib` directory to `$LOAD_PATH`, executes `require "chronic_duration"`,
and then calls the documented API from a separate UID-isolated Ruby subprocess
that speaks one JSON request and one JSON response per line. Therefore:

- the public entry point must be `lib/chronic_duration.rb`;
- nothing may depend on the current working directory, on the project's own
  absolute path, or on files outside the project;
- the required entry points must be loaded by `require "chronic_duration"`
  itself, not by the caller;
- no request may depend on leftover process state from an earlier request.

## Chronic Duration Project Architecture

### Project Directory Structure

Create an installable project with this public structure or an equivalent
standard Ruby Gem layout:

```plain
workspace/
├── Gemfile
├── Gemfile.lock
└── lib/
    └── chronic_duration.rb
```

`lib/chronic_duration.rb` must define the public `ChronicDuration` module and
its public error class, and must load any supporting Ruby file it needs.
Additional files under `lib/` are allowed when they are required by that entry
point. A `gemspec`, `Rakefile`, `README`, tests, or executable scripts are not
required and are not read by the verifier. Keep runtime files inside the
project; do not read from an external checkout or write outside
application-requested paths.

### Module Shape

`ChronicDuration` is a module with module-level (class-function) behavior, so
`ChronicDuration.parse` and `ChronicDuration.output` are callable without
creating an object. Any of `extend self`, `module_function`, or an explicit
`class << self` block is acceptable. Internally the module may be split across
several files under `lib/`.

`ChronicDuration.raise_exceptions`, `ChronicDuration.hours_per_day`, and
`ChronicDuration.days_per_week` are global mutable process state with the
defaults `false`, `24`, and `7`. The documented unit scale reads them at call
time, so changing them changes later results. There is no per-object state, no
caching between calls, and no background work.

## API Usage Guide

### Core API Imports

```ruby
require "chronic_duration"

ChronicDuration
ChronicDuration::DurationParseError
```

### 1. `ChronicDuration.parse` - Duration String To Seconds

```ruby
ChronicDuration.parse(string, opts = {}) -> Integer | Float | nil
```

**Parameters**:

- `string` (`String`): a natural-language or chrono duration string. Only
  `String` input is supported; non-`String` input is out of contract.
- `opts` (`Hash`): Symbol keys.
  - `:keep_zero` (`Boolean`, default `false`): return `0` instead of `nil` when
    the parsed total is zero.
  - `:default_unit` (`String`, default `"seconds"`): the unit used for a number
    that is not followed by a recognized unit word. It must be one of the seven
    canonical unit names below; any other value contributes zero seconds.

**Return Value**: elapsed seconds. An `Integer` when every contributing term is
a whole number, otherwise a `Float`. `nil` when the total is zero and
`:keep_zero` is not truthy.

Normalization, in observable order:

1. The string is lowercased.
2. English number words are converted to digits, so `two hours` behaves like
   `2 hours`.
3. A colon-separated numeric run is expanded into words before anything else is
   tokenized, as described in section 2.
4. The string is split on single spaces. Each token is stripped; a leading or
   trailing comma is removed before lookup.
5. A token that contains a number (`/[0-9]*\.?[0-9]+/`, so `2.5`, `.5`, `20`)
   is kept as-is. Otherwise it is replaced by its canonical unit name if it is a
   documented alias, dropped silently if it is a join word, and otherwise
   dropped - or, when `ChronicDuration.raise_exceptions` is `true`, it raises
   `ChronicDuration::DurationParseError`.
6. If the first surviving token is a unit name rather than a number, an implicit
   `1` is inserted in front of it.
7. Tokens are then read left to right: every number is multiplied by the unit
   name in the following token, and the products are summed. A number with no
   following token uses `:default_unit`. A number followed by something that is
   not a canonical unit name contributes nothing.

Results accumulate; repeated units are allowed (`1 day 1 day` is `172800`), and
the order of terms inside the string does not matter to the total.

#### Unit Scale

Seconds per canonical unit, where `hours_per_day` and `days_per_week` are the
current module settings:

```plain
seconds    1
minutes    60
hours      3600
days       3600 * hours_per_day
weeks      3600 * hours_per_day * days_per_week
months     3600 * hours_per_day * 30
years      31557600
```

`years` is the fixed constant `31557600` and does not follow `hours_per_day`.

#### Unit Aliases

Each canonical unit accepts exactly these input words (in addition to the
canonical plural name itself):

```plain
seconds   second  secs  sec  s
minutes   minute  mins  min  m
hours     hour    hrs   hr   h
days      day     dy    d
weeks     week    wks   wk   w
months    month   mo    mos
years     year    yrs   yr   y
```

Join words, which are always dropped and never raise: `and`, `with`, `plus`.

#### Examples

```ruby
ChronicDuration.parse('4 minutes and 30 seconds')  # => 270
ChronicDuration.parse('3 mins 4 sec')              # => 184
ChronicDuration.parse('2 hrs 20 min')              # => 8400
ChronicDuration.parse('2h20min')                   # => 8400
ChronicDuration.parse('6 mos 1 day')               # => 15638400
ChronicDuration.parse('1 year 6 mos 1 day')        # => 47196000
ChronicDuration.parse('3 weeks and 2 days')        # => 1987200
ChronicDuration.parse('day')                       # => 86400
ChronicDuration.parse('minute 30s')                # => 90
ChronicDuration.parse('two hours and twenty minutes') # => 8400
ChronicDuration.parse('2.5 hrs')                   # => 9000.0
ChronicDuration.parse('12 mins 3.141 seconds')     # => 723.141
ChronicDuration.parse('5')                         # => 5
ChronicDuration.parse('5', default_unit: 'minutes') # => 300
ChronicDuration.parse('0 seconds')                 # => nil
ChronicDuration.parse('0 seconds', keep_zero: true) # => 0
ChronicDuration.parse('gobblygoo')                 # => nil
```

Case is not significant: `'3 Mins 4 Sec'` is `184`.

### 2. Chrono Input Normalization

A numeric field is a run of digits with an optional fractional part. When the
string, with its spaces removed, is two or more such fields separated by single
colons, the fields are consumed from the right against the fixed chrono scale
`seconds, minutes, hours, days, months, years` (there is no `weeks` position),
and are rewritten into `<number> <unit>` words before the rest of the rules
above apply. Fewer fields start lower in the scale: `1:20` is one minute twenty
seconds, `4:01:01` is four hours one minute one second, and six fields begin at
years. A chrono run with more than six fields is out of contract.

```ruby
ChronicDuration.parse('1:20')      # => 80
ChronicDuration.parse('1:20.51')   # => 80.51
ChronicDuration.parse('4:01:01')   # => 14461
ChronicDuration.parse('3:41:59')   # => 13319
```

### 3. Invalid Input And Errors

- `ChronicDuration::DurationParseError < StandardError` is raised, while
  `ChronicDuration.raise_exceptions` is truthy, for a token that is neither a
  number, a documented unit alias, nor a join word. The message conventionally
  names the offending word; the message text is not part of the contract, the
  error class is.
- While `raise_exceptions` is falsy the same input is dropped silently, so
  `'23 gobblygoos'` parses as `23`.
- Valid input is unaffected by `raise_exceptions`: `'3 mins 4 sec'` is still
  `184` while it is enabled.
- Text with no recognized term returns `nil`, and a zero total returns `nil`
  unless `:keep_zero` is truthy.

### 4. `ChronicDuration.output` - Seconds To Duration String

```ruby
ChronicDuration.output(seconds, opts = {}) -> String | nil
```

**Parameters**:

- `seconds` (`Integer` or `Float`): a non-negative elapsed time. Negative
  values, non-numeric values, and string numbers are out of contract.
- `opts` (`Hash`): Symbol keys.
  - `:format` (`Symbol`): `:default` (used when absent), `:short`, `:long`,
    `:micro`, or `:chrono`. An unknown format is out of contract.
  - `:keep_zero` (`Boolean`, default `false`): render a zero value instead of
    `nil`. Only the `:seconds` field is affected by this option.
  - `:units` (`Integer`): keep only the first N non-empty unit fields. `0`
    yields `nil`; a value larger than the number of printed units keeps them
    all.
  - `:joiner` (`String`, default `' '`): text inserted between printed units.
    `:micro` and `:chrono` always join with an empty string and ignore
    `:joiner`.
  - `:weeks` (`Boolean`, default `false`): express whole weeks with their own
    field, as described below.
  - `:limit_to_hours` (`Boolean`, default `false`): stop the decomposition at
    hours, so no day, week, month, or year field is produced.

**Return Value**: the rendered duration `String`, or `nil` when nothing is
printed.

#### Decomposition

Fields are produced in the fixed order `years, months, weeks, days, hours,
minutes, seconds` and each is labeled and joined in that order.

1. When `seconds >= 31557600` **and** `seconds % 31557600 < seconds % month`,
   where `month` is `3600 * hours_per_day * 30`, the value is split
   successively by whole years, then 30-day months, days, hours, minutes, and
   seconds. `seconds % 31557600` and `seconds % month` are remainders.
2. Otherwise, when `seconds >= 60`, minutes and seconds come first
   (`minutes = seconds / 60`, `seconds = seconds % 60`), then hours when
   `minutes >= 60`, then days when `hours >= hours_per_day` - unless
   `:limit_to_hours` is truthy, which stops here. When days are produced and
   `:weeks` is falsy, `days >= 30` rolls into months of 30 days. When `:weeks`
   is truthy, `days >= days_per_week` rolls into weeks and leaves the remainder
   as days, and `weeks >= 4` rolls into months of four weeks.
3. Values below 60 produce only a seconds field.

Only fields whose value is not zero are printed, except in `:chrono`, which
prints every field of its scale, and except for the seconds field, which is
also printed when `:keep_zero` is truthy.

#### Labels And Pluralization

Each printed field is the field value followed by its label. The `:default`
and `:long` labels begin with a space, which is the separator between the
number and the unit; `:short` and `:micro` labels do not.

| Format | years | months | weeks | days | hours | minutes | seconds | Pluralize |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `:default` | `" yr"` | `" mo"` | `" wk"` | `" day"` | `" hr"` | `" min"` | `" sec"` | yes |
| `:long` | `" year"` | `" month"` | `" week"` | `" day"` | `" hour"` | `" minute"` | `" second"` | yes |
| `:short` | `"y"` | `"mo"` | `"w"` | `"d"` | `"h"` | `"m"` | `"s"` | no |
| `:micro` | `"y"` | `"mo"` | `"w"` | `"d"` | `"h"` | `"m"` | `"s"` | no |

Pluralization appends a single `s` to the label whenever the field value is not
exactly `1`, so `1` prints `1 day`, `1 mo`, `1 min`, `1 sec`, while `0`, `2`,
and `15` print `0 secs`, `2 days`, `15 days`. `:short` and `:micro` never
pluralize, so the same value prints as `1mo 15d` in `:short`.

The weeks field only exists when `:weeks` is truthy, in every format: without
that option `3888000` prints as `1 mo 15 days`, with it as `1 mo 2 wks 3 days`.
A years-scale result (rule 1 above) never emits a weeks field.

#### Fractional Seconds

When `seconds` is a `Float`, the seconds field keeps as many decimal places as
the value's own string representation has after the point, and the result is a
`Float`. Whole-number floats such as `90.0` lose their fractional part in
non-chrono formats.

#### Chrono Format

`:chrono` renders each field of its scale separated by `:` with no joiner: an
integer field is zero-padded to two digits, and a fractional seconds field is
padded to its own number of decimal places. Leading `00:` groups are removed,
then one further leading `0` is removed, then any trailing `:` is removed. A
zero value therefore renders as `"0"` regardless of `:keep_zero`.

#### Examples

```ruby
ChronicDuration.output(270)                                 # => "4 mins 30 secs"
ChronicDuration.output(8400)                                # => "2 hrs 20 mins"
ChronicDuration.output(14461, format: :default)             # => "4 hrs 1 min 1 sec"
ChronicDuration.output(14461, format: :micro)               # => "4h1m1s"
ChronicDuration.output(14461, format: :short)               # => "4h 1m 1s"
ChronicDuration.output(14461, format: :long)                # => "4 hours 1 minute 1 second"
ChronicDuration.output(14461, format: :chrono)              # => "4:01:01"
ChronicDuration.output(8400, format: :chrono)               # => "2:20:00"
ChronicDuration.output(80.51, format: :chrono)              # => "1:20.51"
ChronicDuration.output(14461, units: 2)                     # => "4 hrs 1 min"
ChronicDuration.output(15642061, units: 3, format: :long)   # => "6 months 1 day 1 hour"
ChronicDuration.output(8400, joiner: ', ')                  # => "2 hrs, 20 mins"
ChronicDuration.output(3888000)                             # => "1 mo 15 days"
ChronicDuration.output(3888000, weeks: true)                # => "1 mo 2 wks 3 days"
ChronicDuration.output(1299600, weeks: true, units: 2)      # => "2 wks 1 day"
ChronicDuration.output(34128900, limit_to_hours: true)      # => "9480 hrs 15 mins"
ChronicDuration.output(31557600)                            # => "1 yr"
ChronicDuration.output(15638400)                            # => "6 mos 1 day"
ChronicDuration.output(0)                                   # => nil
ChronicDuration.output(0, keep_zero: true)                  # => "0 secs"
ChronicDuration.output(0, format: :micro, keep_zero: true)  # => "0s"
ChronicDuration.output(0, format: :chrono)                  # => "0"
ChronicDuration.output(14461, units: 0)                     # => nil
```

### 5. Module Settings

```ruby
ChronicDuration.raise_exceptions -> true | false
ChronicDuration.raise_exceptions=(value) -> value
ChronicDuration.hours_per_day -> Integer
ChronicDuration.hours_per_day=(value) -> value
ChronicDuration.days_per_week -> Integer
ChronicDuration.days_per_week=(value) -> value
```

All three are module-level accessors, default to `false`, `24`, and `7`, and
are read at call time by both `parse` and `output`. `raise_exceptions=` stores
the truthiness of its argument, so the reader returns only `true` or `false`.
Assignments are global to the process; there is no per-call override and no
reset method in this scope. The verifier resets all three to their defaults
before it exercises them. `years` is the fixed constant above, so it never
follows `hours_per_day`; the other four units do.

```ruby
ChronicDuration.hours_per_day = 8
ChronicDuration.days_per_week = 5
ChronicDuration.parse('5d')   # => 144000
ChronicDuration.parse('40h')  # => 144000
ChronicDuration.parse('1w')   # => 144000
ChronicDuration.parse('1mo')  # => 864000
ChronicDuration.parse('1y')   # => 31557600
ChronicDuration.hours_per_day = 24
ChronicDuration.days_per_week = 7
ChronicDuration.parse('1w')   # => 604800
```

### 6. Ordering And Determinism

- `parse` totals terms left to right and is order-insensitive for the sum, but
  the number-to-unit pairing is positional: only the token immediately after a
  number names its unit.
- `output` always emits fields in the order `years, months, weeks, days, hours,
  minutes, seconds` and joins them with `:joiner` (or `''` for `:micro` and
  `:chrono`).
- Both methods are pure functions of their arguments plus the three documented
  settings: no time, locale, environment variable, file, random number, socket,
  or terminal access, and no mutation of the argument strings.
- Integer arithmetic stays exact (`1499148000.0` is a float only because `4.5d`
  is fractional); rounding is never applied except when formatting a fractional
  seconds field.

### 7. Bounded Scope

Out of scope and not exercised: any CLI or executable, Rake tasks, gemspec
packaging, documentation generation, calendar or clock-anchored parsing of dates
(a `Time` or `Date` never appears in the contract), IANA time zones, currency or
non-English number words, `ChronicDuration::VERSION`, and any behavior of
`output` for negative or non-numeric input or of `parse` for non-`String`
input.

## Implementation Notes

- Packaging is byte-exact: the `Gemfile` and `Gemfile.lock` reproduced in the
  Offline Packaging Contract section are the only accepted contents. No `GIT`,
  `PATH`, or plugin source, no `gemspec` directive, and no gem other than
  `numerizer 0.2.0`. Standard-library modules may be used freely but are not gems
  and must not be declared as dependencies.
- The verifier copies the workspace to a different absolute path, exports
  `BUNDLE_GEMFILE` and a verifier-owned `BUNDLE_PATH`, prepends the copy's `lib`
  to `$LOAD_PATH`, and then runs `require "chronic_duration"`. Therefore nothing
  may depend on the working directory, on the project's own absolute path, or on
  files outside the project, and the entry point must load its own support files
  rather than relying on the caller.
- Each call arrives in a UID-isolated Ruby subprocess over one JSON request and
  one JSON response per line, so no request may depend on leftover process state
  from an earlier request. There is no preinstalled `chronic_duration`; the
  verifier loads the candidate's own `lib`.
- `ChronicDuration.parse` totals every recognized `<number> <unit>` term after
  normalization and returns integer seconds unless a fractional term makes the
  result a float; a normalized total of zero returns `nil`. Unrecognized words are
  dropped and repeated terms accumulate.
- Colon-separated chrono input is read right to left as
  seconds, minutes, hours, days, months, years, and mixes with ordinary words in
  the same string. Decimal numbers, numbers glued to unit letters, and English
  number words all parse.
- Unit scaling follows the current `hours_per_day` and `days_per_week` settings,
  and `ChronicDuration.output` honors `:keep_zero`, `:units`, `:joiner`,
  `:weeks`, and `:limit_to_hours` across the five formats.
- Unparseable text returns `nil`, or raises `ChronicDuration::DurationParseError`
  when `ChronicDuration.raise_exceptions` is `true`; valid text still parses in
  that mode.
- Only the behavior named in the prompt and the API Usage Guide is in scope, and
  nothing may depend on the clock, locale, random number generator, terminal, or
  files outside the project. Do not copy the upstream repository, upstream tests,
  verifier files, or reference source into the generated project.
