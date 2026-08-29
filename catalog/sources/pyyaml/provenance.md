# PyYAML provenance and remediation record

## Source freeze

- `git fetch --depth=1 https://github.com/yaml/pyyaml 34a9bf82357f4952d8f194a5a31f1c39743652d0`: exit 0
- Frozen revision: `34a9bf82357f4952d8f194a5a31f1c39743652d0`
- `git archive --format=tar HEAD | sha256sum`: exit 0,
  `sha256:18387c6163aa3de3221240cade5f77768963c1096061119d67503462049eab68`
- Archive size: 1,218,560 bytes. License is MIT; `LICENSE` digest is
  `sha256:8d3928f9dc4490fd635707cb88eb26bd764102a7282954307d3e5167a577e8a4`.

## Build and test probes

- Runtime probe: CPython 3.12.11, Linux amd64; target lock is CPython 3.12.14
  on Debian 12 using the digest-pinned task base image.
- `pip install -e . --no-build-isolation`: exit 0 with setuptools 84.0.0,
  wheel 0.48.0, and Cython 3.0.12.
- `PYTHONPATH=lib python -m pytest -c /dev/null --collect-only -q tests`:
  exit 0, 1,287 collected.
- `PYTHONPATH=lib python -m pytest -c /dev/null -q tests`: exit 0, 1,287 passed.
- `PYYAML_FORCE_LIBYAML=1 ... --collect-only`: exit 2 because the optional
  LibYAML extension is unavailable in the probe image. This is a documented
  optional-extension boundary; the production task intentionally scores the
  pure-Python baseline.

## Remediation

- The upstream build backend dynamically requests setuptools and Cython. A
  private, hash-locked build/test closure was generated with `uv pip compile`:
  `provenance/requirements.lock.txt`, 7,323 bytes,
  `sha256:d226ffcdb54f7b30c35189714c0af444c46d3697c23efcb1f838808e1c3a05e9`.
- An early draft embedded `source.tar` in the Oracle bundle. It was replaced by
  a root-level `solve.sh` that clones the exact upstream revision, asserts the
  resolved commit, recreates the archive, and verifies the frozen source digest.
- The verifier uses `custom-json-v1` with 64 unique deterministic scenarios;
  all 64 pass against the frozen source through the candidate subprocess
  boundary. The verifier bundle is private CAS ref
  `sha256:322fe75d26fc55d3ce7654099ed86cf4c03db7ddb7442e3005a8265a65542bec`.

## Current checkout replay

- `PYTHONPATH=.nl2repo/authoring-work/source-run/lib uv run python -m pytest
  -c /dev/null --collect-only -q .nl2repo/authoring-work/source-run/tests`:
  exit 0, 1,287 collected; the optional LibYAML extension was unavailable and
  its tests were skipped by the frozen upstream configuration.
- The matching full command exited 0 with 1,287 passed in 4.34 seconds.
- A first task-local `uv pip install --no-deps --no-build-isolation` probe
  failed because the fresh authoring virtual environment lacked setuptools.
  Installing `provenance/requirements.lock.txt` with `--require-hashes`, then
  repeating the build, exited 0 and installed `pyyaml==7.0.0.dev0` into the
  isolated target. This verifies the declared build-backend remediation.
- Production compile, Oracle, and all controls below were rerun from Git checkout
  `abfa9c2bbab4f187b36bac8c5abdb92bf66738fb`; no prior run receipt was reused.
