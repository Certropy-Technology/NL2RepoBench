# Frozen Source Inventory

- Upstream: `https://github.com/aio-libs/aiohappyeyeballs`
- Revision: `d3ba49e5359746f4364fb4732b238c430833cc0b`
- Archive SHA-256: `1bd56621359406cb343f099072ea4e52b75277a6e097a9a6fc57c86b642c0048`
- Archive command: `git archive --format=tar --prefix=aiohappyeyeballs/ d3ba49e5359746f4364fb4732b238c430833cc0b`
- License: Python Software Foundation License 2.0 (`LICENSE` SHA-256
  `3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf`)
- Package version: `2.7.1`; source root: `src/aiohappyeyeballs`
- Build backend: `poetry.core.masonry.api`; build requirement:
  `poetry-core>=2.0.0`
- Runtime dependencies: none.

The frozen upstream suite was installed with explicit development tools
(`pytest==9.1.1`, `pytest-asyncio==1.4.0`, and `pytest-cov==7.1.0`) because
the source does not publish a `test` extra. It collected 66 leaves: 52 passed
and 14 optional benchmark leaves skipped. Those counts come from the 66
individual JUnit `testcase` elements; pytest's suite-level `tests="70"`
attribute is not used because it disagrees with the emitted leaves. The task
verifier uses a bounded deterministic API contract rather than copying the
upstream suite.

Public implementation modules are `__init__.py`, `types.py`, `utils.py`,
`impl.py`, and `_staggered.py`. The source has no service, browser, database,
or external-data dependency. The only connection probes in the private
verifier use a verifier-owned loopback server; they do not use DNS or public
network access.
