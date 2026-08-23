# `getsentry/responses` Audit

Status: **blocked**.

## Scope

This is a fast, bounded audit of the requested exact revision. It records only
the evidence supplied for this candidate and does not create an authoring or
publication package.

- Repository: `getsentry/responses`
- Requested exact commit: `2827d43f9ac5637baae4ba7740dbe61d934d3e16`
- Project description: requests mocking library
- License: Apache-2.0
- Network constraint: no external network
- Boundary requirement: loopback-only boundary needed

No clone or property-test run was performed. No `task.toml`, `instruction.md`,
hidden tests, Harbor assets, or shared catalog/index edit is included.

## Decision

Keep this candidate in the **blocked** state. The supplied evidence identifies
the candidate and its required network boundary, but does not establish the
source, packaging, test, verifier, or publication gates needed to author a
task.

## Explicit Unknowns

- source tree, source archive, provenance evidence, tree digest, commit date,
  and submodule state;
- package version, import surface, Python/runtime requirements, build system,
  runtime dependencies, and offline dependency closure;
- public API signatures, behavior contracts, error behavior, and supported
  entry points;
- upstream test inventory, collection behavior, test count, frozen denominator,
  and behavior coverage;
- the implementation and verification of the required loopback-only boundary;
- verifier or candidate subprocess contract, image/toolchain, Oracle results,
  empty/stub/forgery/offline controls, review records, and publication
  metadata.
