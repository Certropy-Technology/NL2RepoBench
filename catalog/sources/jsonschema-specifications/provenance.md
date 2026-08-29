# Authoring Provenance

- Package: `jsonschema-specifications`
- Upstream: `https://github.com/python-jsonschema/jsonschema-specifications`
- Revision: `7aee138ac610b09b81aae1d338b8ed4601a01764`
- License: MIT, from `COPYING`
- Source archive: `sha256:07328bc116206bfa14d749cb01ee5039f20e0ed28bdf017bc010101f23a11053`
- Evaluation runtime: CPython 3.12 on Debian 12 amd64
- Candidate runtime policy: no network; dependencies are installed during image build
- Verifier protocol: `custom-json-v1`, separate child-side candidate calls

The frozen upstream checkout has a VCS-derived version and cannot build from a
plain archive without `.git` metadata.  The trusted Oracle verifies the exact
archive digest first, then applies the task-local packaging adaptation of
replacing the dynamic version declaration with a fixed version before building.
This does not modify the source bytes used for the source digest or the
runtime package behavior.

The upstream test collection was four leaves: one registry content check, one
crawl idempotence check, and two dotfile parametrizations.  The production
verifier retains those behaviors and adds deterministic public-contract checks
for all 20 resources, package metadata, and installed package data.
