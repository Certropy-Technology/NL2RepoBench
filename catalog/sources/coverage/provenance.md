# Coverage Source Provenance

- Upstream: `https://github.com/coveragepy/coveragepy`
- Frozen revision: `aeaa79b812d1bc637ebb5582ab12c076e192c87e`
- License: Apache-2.0, from `LICENSE.txt`
- Version metadata: `7.16.0a0.dev1`, from `coverage/version.py`
- Source archive: unprefixed `git archive --format=tar <revision>`
- Source archive SHA-256: `sha256:d4c34fff118dcfe6e22a637411cdd5c5a7605dd2e65ed510560637ee94467e56`
- Source tree: 44 Python modules under `coverage/`, 202 test/support files,
  412 tracked archive entries.
- Native-risk adaptation: the contract exercises the pure-Python tracer and
  standard-library report/data paths; the C tracer is optional.

The Oracle bundle fetches only this revision from the declared upstream host,
asserts the resolved commit, verifies the archive digest, and extracts it into
the Oracle workspace. The model Agent and separate verifier have no source-host
authorization.
