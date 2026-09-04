# go-dig blocked authoring record

## Status

This task is blocked before Harbor packaging. The immutable source revision and
license are frozen, but the required third-party Go module closure is not
materialized as a private offline artifact. No Oracle, verifier, controls, or
generated `catalog/tasks/go-dig` runtime is claimed.

## Reproduced findings

- Revision `770912487056bfe8bc9bd5879a4e049f68989ab0` has source archive digest
  `sha256:6c5890219e8b3bae095197f54e66e369d78e3058cf88b322415011b8a218cef0`.
- `LICENSE` is MIT with digest
  `sha256:5cce09a0a02e15f476aa4385bf23d13ec8447de58a7057523a82dcc80f0aff04`.
- The clean `GOPROXY=off` probe fails before test collection because
  `github.com/stretchr/testify v1.7.1` and its transitive modules are absent.
- The upstream `TestProvideLocation` path assertion passes when the frozen tree
  is extracted below a `dig/` directory, so checkout layout is a resolvable
  remediation rather than a reason to weaken the assertion.

## Remediation

Materialize and hash-lock `testify v1.7.1`, `go-spew`, `go-difflib`, and `yaml.v3`
in the private Go module artifact. Compile a reviewed separate child-side typed
bridge, collect its fixed public-behavior denominator, and run Oracle plus
empty/stub/forgery/offline controls against one final bundle. Keep the source
checkout layout under `dig/` while reproducing path-sensitive upstream tests.
