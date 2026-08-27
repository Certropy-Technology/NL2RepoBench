# annotated-doc Authoring Provenance

## Frozen source

- Upstream: `https://github.com/fastapi/annotated-doc`
- Revision: `826e18a4ba8409d543306bbcf81384407d888068` (`main` at freeze time)
- Package snapshot: `annotated-doc==0.0.5`
- PyPI source distribution: 10,758 bytes,
  SHA-256 `c7e58ce09192557605d8bbd92836d7e1d520ac9580096042c0bfd197efacf1bb`
- License: MIT; frozen `LICENSE` SHA-256
  `fff170779a6acbf65abdb405c087f1cee1786691e4a96a4034517e4a504a0cdf`.
- `git ls-remote` confirmed that the selected revision is the upstream `main`
  head. Git source acquisition is confined to the trusted Oracle `solve.sh`,
  which fetches and asserts this full revision before copying the source.

The public package-core files in the frozen 0.0.5 distribution match the
selected revision's package contract. The sdist digest is retained as the
source snapshot digest because this authoring lane does not materialize a Git
checkout in the model-visible workspace.

## Inventory and tests

The deterministic AST inventory found 4 implementation Python files, 3 test
files, 33 public symbols, 20 upstream test definitions, and no unresolved
syntax or external-service risk. The package-core upstream test module has 6
tests and passes. The full sdist test collection has 22 passing tests; the 16
release-automation tests are not scored because they depend on Typer and
mutable release-note files rather than the runtime package API.

The private verifier freezes 18 leaves for root exports, version, value
storage, repr, equality, hashing, constructor boundaries, `Annotated`
parameter/return/class metadata, pickle compatibility, special text, and
isolated imports. Candidate code is loaded only by verifier child processes.

## Environment and closure

- Target runtime: CPython 3.12.14 on Debian 12 `linux/amd64`.
- Base image: `python:3.12.14-slim-bookworm`, digest
  `sha256:356b0d18f9385f4bdcc673af60e1e64c9d1504952e4ec36ee32044c722a6bc4e`.
- Hash-locked build closure: `pdm-backend==2.4.9`, `setuptools==80.10.2`,
  and `wheel==0.45.1`; no runtime dependency and no vendored wheelhouse.
- Agent and verifier run phases are `no-network`; only the trusted Oracle gets
  a run-scoped authorization for the exact source host.

Source validation and production compilation passed. This lane intentionally
does not claim Harbor Oracle, Agent, or negative-control receipts.
