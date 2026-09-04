# go-dig adapter assessment

The public package is reflection-heavy and has callbacks, scopes, graph
visualization, and arbitrary constructor values. A reviewed typed bridge can
faithfully cover fixed constructors, `dig.In`/`dig.Out` tags, named and grouped
values, optional dependencies, caching, scopes, decorators, and structured
error predicates; `harbor/tests/bridge.go` records that proposed boundary.

Production authoring is blocked before verifier execution because the frozen
upstream suite does not pass in the captured checkout: `TestProvideLocation`
asserts a repository-relative source path. The test dependency closure also
requires `testify v1.7.1`, `go-spew`, `go-difflib`, and `yaml.v3`, none of which
has been materialized and hash-bound for offline Harbor builds. No Oracle,
verifier, or controls receipt is claimed.

Remediation: reproduce the upstream test in a checkout layout that preserves
its expected path or document a source-only, review-approved test relaxation;
freeze the complete module cache/vendor bundle and test collection; then build
the child-side verifier and run Oracle plus adversarial controls against one
final compiled manifest.
