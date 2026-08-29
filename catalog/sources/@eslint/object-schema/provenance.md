# `@eslint/object-schema` Authoring Provenance

## Source freeze

- Upstream: `https://github.com/eslint/rewrite`
- Package directory: `packages/object-schema`
- Revision: `095661b9e87506b017e2d39fbc86e5d38d7eb91c`
- Frozen git archive digest: `sha256:64c90db8352d57c56779c8c2bd9df83521d6903108760aedb25df5e4e13fc99b`
- License: Apache-2.0; package license and repository `LICENSE` were inspected.
- Package version: `3.0.5`

## Scope decision

The monorepo has 246 tracked files and 8 packages. The selected package has four JavaScript
source modules and no runtime dependencies. Its upstream package tests contain 134 Mocha leaves
plus TypeScript type checks. The fixed Harbor denominator is a private 20-leaf `node:test` slice
covering the package exports, all named built-in strategies, schema construction and immutability,
validation and merge behavior, nested schemas, required/dependent keys, error wrapping, and
CommonJS/ESM package loading. The broader monorepo, TypeScript compiler, Rollup plugin, and type
checker are not runtime dependencies and are not exposed to the model.

## Environment remediation

The upstream monorepo does not commit a package lock and its package-level build uses the root
development toolchain. The task therefore uses a zero-entry npm v3 candidate lock and a private
Oracle build bundle that materializes the package's published ESM/CJS layout from the exact source
revision. Candidate and verifier phases install with npm offline and ignore scripts. No build
tooling or registry access is required during evaluation.

## Security boundary

The candidate is packed and installed in a UID-isolated subprocess boundary. Hidden tests, the
Oracle source archive, and control receipts are private artifacts. Agent metadata has
`agent_network_mode = "no-network"` and no allowed hosts; only an Oracle invocation can receive
the exact upstream source-host authorization.
