# `editables` Authoring Audit

Status: **controls-passed; awaiting integrator review and model Agent Run**.

## Frozen source

- distribution: `editables`
- upstream: `https://github.com/pfmoore/editables`
- revision: `e54908a593a1062be201d1acdb80e379e0776d4b`
- source archive: `git archive --format=tar HEAD`
- archive SHA-256: `d82a26dd246c6b5f37bc9881975d3fe2af535b390f90dc452575c0ebfea5f2aa`
- license: MIT, `LICENSE.txt`
- runtime tree: two Python modules and one `py.typed` marker
- runtime dependencies: none

The upstream suite contains `tests/test_editable.py` and
`tests/test_redirects.py`, with 27 collected tests under the authoring CPython
3.12 environment (the larger static count includes parameter definitions). The production task uses a separately authored 24-leaf
JSON scenario contract so the verifier does not import or ship upstream test
bytes, and so live Python objects remain on the candidate side of the
subprocess boundary.

## Environment and closure

The task uses the pinned Harbor Python 3.12 slim base image and
`flit_core==3.12.0` as its only candidate build dependency. The dependency
requirement is stored as a private SHA-256 lock artifact. No wheelhouse or
runtime dependency is included in the task.

## Verifier boundary

`verifier/run.py` launches `adapter.py` in a second isolated Python process.
The adapter adds only `/tmp/candidate-site` to its own `sys.path`, constructs
temporary package trees, and returns 24 fixed leaf IDs. Trusted collection,
JUnit, network, and reward reports remain owned by Harbor's verifier runtime.
