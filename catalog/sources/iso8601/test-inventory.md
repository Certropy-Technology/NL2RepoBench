# iso8601 Test Inventory

## Upstream baseline

At the frozen revision, `iso8601/test_iso8601.py` collects 47 pytest items with pytest 8.4.1, Hypothesis 6.138.4, and pytz 2025.2 on Python 3.12.11. All 47 pass after disabling unrelated root-worktree pytest `addopts` with `-o addopts=`.

The collection consists of four standalone tests, 12 invalid-input parameter leaves, 29 valid-input parameter leaves, and two Hypothesis properties. The property tests draw random examples and therefore are not used directly as the fixed Harbor denominator.

## Frozen Harbor denominator

The private custom-json verifier contains 31 deterministic unique leaves. It preserves the upstream behavioral surface while replacing randomized generation with explicit cases:

- 3 API/export/fixed-offset compatibility leaves;
- 3 timezone default and `Z` leaves;
- 10 reduced, dashed, compact, separated, and partial date/time leaves;
- 5 signed timezone offset leaves;
- 3 fractional-second leaves;
- 4 invalid grammar/calendar/error leaves;
- 3 copy, pickle, round-trip, and public predicate leaves.

Each leaf starts a separate `python -I` candidate subprocess and imports only from `/tmp/candidate-site`. The root verifier never imports candidate code in its own process. The expected denominator is exactly 31, with no skipped statuses.
