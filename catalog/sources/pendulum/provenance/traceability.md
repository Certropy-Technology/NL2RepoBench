# Traceability

The private verifier uses a fixed set of JSON-normalized scenarios. Every leaf
maps to a public section of `instruction.md`; no private helper is required.

| Contract area | Public specification | Frozen upstream test families |
| --- | --- | --- |
| Packaging and exports | Supports; root re-exports | `tests/test_main.py`, import performed by every test |
| Construction and stdlib compatibility | Constructors and conversion | `tests/date/test_construct.py`, `tests/time/test_construct.py`, `tests/datetime/test_construct.py` |
| Calendar arithmetic and boundaries | `Date`, `Time`, and `DateTime` | `tests/date/test_add.py`, `tests/datetime/test_add.py`, `test_start_end_of.py`, day-of-week modifier tests |
| DST and timezone conversion | Constructors; Timezones | `tests/tz/test_timezone.py`, `tests/datetime/test_timezone.py` |
| ISO parsing and format parsing | Current time and parsing | `tests/parsing/*`, `tests/test_parsing.py`, `tests/datetime/test_from_format.py` |
| String and token formatting | Date/time objects; formatting | date/time/datetime string tests and `tests/formatting/test_formatter.py` |
| Duration arithmetic and units | Durations and intervals | `tests/duration/*` |
| Interval endpoints, range, containment | Durations and intervals | `tests/interval/*` |
| Locale state and humanization | Timezones, locale, and formatting | `tests/localization/*`, helper locale tests |
| Controlled clock state | Controlled time travel | `tests/testing/test_time_travel.py` |
| Error contracts | Each API section | invalid construction, parser, timezone, locale, and boundary tests |

The scored denominator is the private contract scenario count, not the 1,843
expanded upstream leaves. This keeps candidate execution behind the required
UID-separated subprocess/JSON boundary while preserving representative
upstream semantics. The 1,843-leaf full-suite run establishes source truth and
is retained as task-local authoring evidence.
