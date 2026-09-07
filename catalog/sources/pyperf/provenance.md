# pyperf provenance

- **Package:** `pyperf`
- **Upstream:** https://github.com/psf/pyperf
- **Frozen version:** 2.10.0
- **Revision binding:** the authoring input is the immutable PyPI source distribution
  `pyperf-2.10.0.tar.gz`; its SHA-256 is
  `dd93ccfda79214725293e95f1fa6e00cb4a64adcf1326039486d4e1f91caaa62`.
- **License:** MIT, declared by upstream metadata and `COPYING`.
- **Source tree:** the extracted archive and its path/hash manifest are recorded in
  `evidence/source-freeze.txt`.

## Bindability rationale

pyperf is a pure-Python benchmarking and result-serialization package. Its public
contract can be exercised at a process boundary using ordinary Python imports and
JSON files. The stable, bindable surface is the root re-export set (`Run`,
`Benchmark`, `BenchmarkSuite`, `add_runs`, `Runner`, `format_metadata`), the
`Runner` benchmark-registration methods, ordered value and metadata accessors,
JSON load/dump round trips, and the `pyperf` console/module entry point.

Timing magnitudes, CPU identity/count, process affinity, scheduler behavior,
calibration duration, host metadata, and exact wall-clock measurements are not
bindable: they vary with hardware, operating-system load, Python build, and the
sandbox. Tests must check structural and error behavior rather than exact timing
numbers. The public API inventory and behavior graph in `evidence/` deliberately
exclude private helpers and implementation-specific test fixtures.
