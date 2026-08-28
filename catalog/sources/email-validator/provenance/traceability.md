# Public Contract Traceability

The private verifier has 30 unique leaves. Each leaf invokes candidate code only through the isolated `candidate_client`; the root verifier owns collection, JUnit, grading, and reward.

| Contract area | Instruction section | Coverage |
| --- | --- | --- |
| Distribution metadata and root exports | Supports; Package exports | version, `__all__`, importable result and exception names |
| Basic ASCII validation and normalization | `validate_email` | case-normalized domain, result fields, bytes input |
| Syntax and error boundaries | `validate_email`; Exceptions | missing at-sign, bad local/domain, special-use domain, invalid type |
| Unicode and IDNA | `validate_email` | Unicode domain to IDNA, internationalized local, SMTPUTF8 gate |
| Optional syntax forms | `validate_email` | display names, quoted locals, empty locals, IPv4/IPv6 literals |
| Result object compatibility | `ValidatedEmail` | repr, dict conversion, legacy accessors, warnings, equality |
| DNS boundary | `validate_email`; `caching_resolver` | sorted MX, A/AAAA fallback, NXDOMAIN, null MX, timeout, cache lifetime |
| CLI | Command line interface | module execution for valid and invalid input |

The full upstream test suite was used only for source/environment diagnosis. Hidden leaves are newly authored behavior checks and do not expose upstream test files or reference implementation bytes.
