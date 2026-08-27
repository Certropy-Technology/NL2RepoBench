# iso8601 Traceability

| Public contract | Hidden leaf IDs |
| --- | --- |
| Package exports and exception type | `exports`, `parse-error-contract` |
| `FixedOffset` offset/name/equality | `fixed-offset` |
| `UTC`, default timezone, explicit `Z`, and naive override | `default-utc`, `z-is-utc`, `default-none` |
| Reduced and calendar-only dates | `reduced-year`, `reduced-month`, `dashed-date`, `compact-date` |
| `T`/space separators and partial/compact times | `space-separator`, `t-separator`, `hour-only`, `compact-hour-minute`, `compact-hour-minute-second`, `colon-minute` |
| Signed hour/hour-minute timezone forms | `offset-hour`, `offset-compact`, `offset-colon`, `negative-offset` |
| Dot/comma fractions and microsecond truncation | `fraction-dot`, `fraction-comma`, `fraction-truncation` |
| Full-string predicate and malformed input | `regex-valid`, `is-valid`, `invalid-malformed`, `invalid-trailing` |
| Impossible calendar values and public error | `invalid-calendar`, `invalid-month`, `parse-error-contract` |
| Standard `datetime` interoperability | `copy-and-pickle`, `aware-roundtrip` |

Every hidden assertion maps to a behavior stated in `instruction.md`. The instruction does not reveal the frozen revision, source host, private leaf implementation, or exact expected value table.
