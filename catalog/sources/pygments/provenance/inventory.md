# Pygments Authoring Inventory

## Frozen source

- Upstream: `https://github.com/pygments/pygments`
- Revision: `38f426a6b1cd4ffc6429f5808031b7c62ea57b1f`
- Revision subject: `Add heading for 2.22.0`
- License: BSD-2-Clause; `LICENSE` is 1331 bytes and its SHA-256 is
  `a9d66f1d526df02e29dce73436d34e56e8632f46c275bbdffc70569e882f9f17`.
- Unprefixed `git archive --format=tar HEAD` is 47,749,120 bytes with SHA-256
  `3020b621c9c647c499fe804a4606c9818a3d318af42ee867d653ae7d145bb53c`.
- No submodules, native extension, database, or network runtime requirement.

## Tree and tests

The frozen checkout has 405 Python files, 263 lexer modules, 49 style modules,
and 14 formatter modules. It has 45 tracked test/support files and uses
pytest, `pytest-randomly`, and `wcag-contrast-ratio` for its test suite.

On CPython 3.12.11 with the task-local hash-locked probe environment:

- collection: 5346 tests, exit 0;
- collection excluding `tests/contrast`: 5345 tests, exit 0;
- full run: 5330 passed, 16 skipped, exit 0, 28.31 seconds.

The production verifier uses a separate 32-leaf JSON scenario contract to
bound process time while covering the core root API, token model, representative
lexers, lookup/guess behavior, formatters, styles, utility helpers, regex
construction, CLI, and failure contracts. The full upstream run remains
provenance evidence and is not the production denominator.

## Dependency remediation

The upstream build backend is Hatchling 1.27.0. A task-local build-only lock was resolved
with `uv pip compile --generate-hashes` and installed with
`uv pip install --require-hashes`; it contains only exact pins and package
hashes for Hatchling, Packaging, Pathspec, Pluggy, and Trove Classifiers. The
candidate runtime has no third-party dependency. These build dependencies are
installed in the image build phase; agent and verifier execution are
no-network. Pytest and contrast dependencies were used only for the task-local
upstream baseline and are not put into the candidate dependency site.
