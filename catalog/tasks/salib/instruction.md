# SALib authoring pilot (blocked)

This directory is a task-local authoring record for the SALib scientific
sensitivity-analysis library at the immutable revision recorded in
`task.toml`. It is **not** a runnable benchmark task or a complete public
behavior contract.

The eventual task scope would cover an installable `SALib` Python distribution,
its sampling and sensitivity-analysis modules, the `ProblemSpec` convenience
API, bundled test functions, and the `salib` command-line entry point. The
upstream project uses NumPy, SciPy, pandas, matplotlib, and multiprocess; its
tests also exercise seeded and unseeded numerical paths, subprocess CLI calls,
parallel evaluation, and floating-point comparisons.

Publication is blocked pending a hash-locked offline dependency bundle, a
frozen collection and verifier environment, repeated determinism/tolerance
validation, and a task-specific separate-verifier adapter for non-JSON array,
callable, dataframe, and multiprocessing interactions. Hidden tests, Oracle
assets, Docker files, and private command bytes are intentionally not included
in this pilot. See `audit.md` for the evidence and exact blockers.
