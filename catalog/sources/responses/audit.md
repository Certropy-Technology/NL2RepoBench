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

## Explicit Unknown Gates

The following gates are explicitly unknown; none is inferred from the supplied
project name or license evidence:

- exact archive bytes and hash, source provenance, tree digest, commit date,
  and submodule state;
- package version, import surface, Python/runtime requirements, build system,
  runtime dependencies, and offline dependency closure;
- fixture inventory and any required fixture data;
- upstream test inventory, collection behavior, test count, frozen denominator,
  and behavior coverage;
- source-only LOC, with tests, fixtures, generated files, and documentation
  excluded;
- the implementation and verification of the required loopback-only/mock
  transport boundary;
- verifier or candidate subprocess contract, image/toolchain, Oracle results,
  empty/stub/forgery/offline controls, review records, and publication
  metadata.
