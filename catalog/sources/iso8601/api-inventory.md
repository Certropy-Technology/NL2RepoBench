# iso8601 API Inventory

Frozen revision: `00c9262b9ad141f287b3263be7f2244fa01988c2`.

## Public package exports

| Import | Signature/type | Observable contract |
| --- | --- | --- |
| `iso8601.parse_date` | `(datestring: str, default_timezone: datetime.timezone | None = UTC) -> datetime.datetime` | Parses supported date/time forms; applies explicit or default timezone; raises `ParseError` for grammar or `datetime` construction failures. |
| `iso8601.is_iso8601` | `(datestring: str) -> bool` | Full-string grammar match, without constructing a datetime. |
| `iso8601.FixedOffset` | `(offset_hours: float, offset_minutes: float, name: str) -> datetime.timezone` | Creates a fixed-offset standard-library timezone. |
| `iso8601.UTC` | `datetime.timezone` | Alias of `datetime.timezone.utc`; used for `Z` and as the parser default. |
| `iso8601.ParseError` | `ValueError` subclass | Public parsing exception. |

The implementation module also exposes `ISO8601_REGEX` and `parse_timezone`; these are not package exports. The verifier observes `ISO8601_REGEX` only as a compatibility check and does not require callers to import the internal helper.

## Packaging

- Distribution/import name: `iso8601`.
- Version at the frozen revision: `2.1.0`.
- Python requirement: `>=3.7,<4.0`.
- Runtime dependencies: none outside the standard library.
- Build backend: `poetry.core.masonry.api`; build requirement `poetry-core>=1.0.0`.
- Public typing marker: `iso8601/py.typed`.
