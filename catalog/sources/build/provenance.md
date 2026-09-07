# build provenance

- Package: `build`
- Version: `1.2.2`
- Upstream: https://github.com/pypa/build
- Frozen input: `.nl2repo/authoring-live/python-wave1/build.tar.gz`
- Archive SHA-256: `119b2fb462adef986483438377a13b2f42064a2a3a4161f24a0cca698a07ac8c`
- License SPDX: `MIT` (the frozen sdist contains `LICENSE` and declares the MIT classifier).
- Source basis: extracted sdist under `.nl2repo/authoring-work/build-staging`; public symbols were inventoried with Python stdlib `ast` without importing or executing candidate code.

## Bindability rationale

The package has a compact, documented PEP 517 frontend API. Pure filename parsing,
dependency inspection, builder properties, metadata path contracts, and CLI argument
validation can be specified through black-box behavior. A tiny local `pyproject.toml`
project with a preinstalled backend can exercise non-isolated output creation in a
fully offline image.

Isolated-environment creation and installation are deliberately not asserted as a
network-free behavior: `DefaultIsolatedEnv` creates a temporary environment and may
invoke pip/uv plus backend installation. Such behavior is non-bindable for the
NoNetwork hidden verifier unless every dependency and backend artifact is preinstalled
and the local build path is explicitly proven offline-safe. The public instruction
therefore describes this boundary without requiring network access or unverifiable
implementation details.
