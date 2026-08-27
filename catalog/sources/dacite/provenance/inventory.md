# Source And Test Inventory

- Upstream: `https://github.com/konradhalas/dacite`
- Frozen revision: `9898ccbb783e7e6a35ae165e7deb9fa84edfe21c`
- Commit time: `2025-03-17T16:24:48+01:00`
- License: MIT; `LICENSE` SHA-256
  `e1741cee11fc82b815210f5368d301c940e7e3def89af718da81550150ba3277`
- Reproducible unprefixed `git archive --format=tar HEAD` SHA-256:
  `bd30874ca55029421d5279be2d1b327dda2b86ab1865e3bdc3cfb91e48f7e834`
- No submodules.
- Static inventory: 11 implementation Python files, 569 implementation
  lines, 22 test files, and 203 collected test functions.
- Risk flag `dynamic-execution` comes from runtime type-hint resolution. The
  production verifier handles it through bounded, unprivileged child
  processes rather than importing candidate code into the trusted grader.

The frozen upstream suite passed three independent Python 3.12 runs with the
same result: **203 passed**, exit code 0. The production denominator is a
separate fixed set of 45 JSON-safe behavior scenarios covering packaging,
exports, configuration, primitive/nested/collection conversion, defaults,
errors, hooks, casting, key conversion, unions, forward references, literals,
new types, frozen/non-init fields, and cache controls.
