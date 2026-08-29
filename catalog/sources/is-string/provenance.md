# is-string Authoring Provenance

## Immutable source and license

- Upstream: `https://github.com/inspect-js/is-string`
- Revision: `42a850857133d6525a02a623bf45c9e904a347d2`
- Source archive SHA-256: `sha256:ef0d9f5631282a1db137c201c231953a212baedbacddaf2636c97d3be0b8a8f5`
- License: MIT, from the tracked `LICENSE` file; its bytes were separately hashed
  during source freeze.
- No submodules. The source tree contains one runtime module, one declaration,
  package metadata, and one upstream tape test file.

## Adaptation and dependency closure

The upstream runtime declares `call-bound` and `has-tostringtag`. The scored
contract does not need their package-specific wrappers, so the reference and
candidate contract use the equivalent built-in `String.prototype.valueOf.call`
internal-slot check. This makes the runtime closure empty while retaining the
observable predicate behavior, including protection from `Symbol.toStringTag`
spoofs. The private npm bundle still contains an integrity-checked npm v3
lock/cache contract, with no package tarballs.

The verifier uses a separate Node child for every API call. Tagged JSON inputs
construct boxed strings, cross-realm objects, symbols, BigInts, getters, and
conversion-method probes inside that child; no executable values cross the JSON
boundary.

## Reproducibility

Authoring source acquisition and probes are under
`.nl2repo/authoring-work/node-author-wave2-20260828/is-string/`. Generated Harbor
runtimes are compiler output and are intentionally not hand-authored in this
lane. Private test, command, npm, and Oracle bundles are content-addressed in
`.nl2repo/artifacts` and referenced by digest from `task.toml`.
