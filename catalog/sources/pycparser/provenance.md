# pycparser authoring provenance

- Upstream: `https://github.com/eliben/pycparser`
- Revision: `10d17757e282d8af5426d6df4d55eb394042b550`
- License: BSD-3-Clause, from the frozen `LICENSE` file.
- Source archive: `git archive --format=tar HEAD`, SHA-256
  `ed31469eea243e25ce86310039c174a61890d2acc7586cd06f8be38cf1baf5a1`,
  1,331,200 bytes.
- Native baseline: CPython 3.12.11, `python -m unittest discover -v`,
  136/136 passed, exit code 0. Log is retained under task-local authoring
  work and is not part of the public Agent bundle.
- Packaging: upstream `pyproject.toml` uses `setuptools.build_meta`, package
  version `3.00`, and no runtime dependencies. The task lock contains only
  pinned build tools `setuptools==80.9.0` and `wheel==0.45.1`, each with
  SHA-256 hashes.
- Boundary adaptation: upstream unittest imports the implementation in-process;
  production scoring uses a private custom JSON verifier and candidate child
  process, comparing only explicit serializable projections.
- Graphviz and arbitrary external tool behavior are outside the scored contract;
  the deterministic local `cpp` probe is retained only for `parse_file`/the
  preprocessor API boundary.
