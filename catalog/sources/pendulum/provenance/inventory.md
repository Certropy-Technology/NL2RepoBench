# Inventory

`nl2repo author scan-source` parsed the frozen tree without importing it.

- Python implementation files: 121
- Python implementation LOC: 11,867
- Public symbols found statically: 1,426
- Test files: 103
- Static test definitions: 1,113
- Test LOC: 8,008
- Scanner risk flag: `dynamic-execution`

The runtime API is centered on root constructors plus `Date`, `Time`,
`DateTime`, `Duration`, `Interval`, timezone classes, formatting, locale state,
ISO parsing, and optional time travel. The frozen source also contains a
Maturin/PyO3 extension for parsing and arithmetic helpers. The task contract
permits an equivalent pure-Python implementation and never imports candidate
code in the trusted verifier process.

With CPython 3.12.11, pytest 7.4.4, pytest-benchmark 4.0.0,
python-dateutil 2.9.0.post0, tzdata 2026.3, time-machine 3.5.0, and the frozen
source installed locally, independent collection produced 1,843 leaves. The
full suite completed with 1,840 passed and 3 skipped. Static and expanded
counts differ because parametrized timezone tests expand against the frozen
tzdata database.
