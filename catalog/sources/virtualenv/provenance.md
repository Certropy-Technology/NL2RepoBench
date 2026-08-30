# Virtualenv Provenance

- Upstream: `https://github.com/pypa/virtualenv`
- Frozen revision: `2a645aece0241e6dc02bf3d67acd88aa0770b601`
- Upstream release: `21.7.5`
- License: MIT; `LICENSE` SHA-256:
  `5c15919378c5b2aaab7b19cea70d8cdc75f76879e32454e4c0399f8b71d171e9`
- Raw `git archive` SHA-256:
  `362a56eab724517cdcc3d8206bc36a562d4a51231256fd47f71dd9c6dabebe7a`

The upstream source declares Python `>=3.9`, Hatchling/Hatch-VCS packaging,
and runtime dependencies `distlib`, `filelock`, `platformdirs`, and
`python-discovery`. The task freezes the CPython 3.12 branch and includes the
Hatch build backend in the private, hash-locked build dependency closure so the
trusted Oracle can install without network access at evaluation time.

The upstream suite has 232 test functions across filesystem, subprocess,
activation, cache, plugin, and interpreter variants. The task uses a 36-leaf
deterministic POSIX adaptation. It excludes network wheel updates,
non-CPython interpreters, other operating systems, and dynamic plugin behavior.
Upstream baseline probe: `12 passed` for `tests/unit/test_run.py` and
`tests/unit/config/test___main__.py` with Python 3.12.11; the production
image is pinned to the available CPython 3.12.14 Debian runtime.
