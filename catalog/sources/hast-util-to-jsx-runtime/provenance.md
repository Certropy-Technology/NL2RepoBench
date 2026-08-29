# Authoring Provenance

- Upstream: `https://github.com/syntax-tree/hast-util-to-jsx-runtime`
- Frozen revision: `b0920cd0837052144ebe94f53d8f792b05619444`
- Package: `hast-util-to-jsx-runtime@2.3.6`
- License: MIT; upstream license file digest `sha256:dd1081884a92952802f4803110a6bb543acea9a814c786d58605b4c1219b5ebb`
- Raw source archive: `sha256:0b65e0053265f212057697912c49e5d929c91d254495433fbb2a416682b91306`
- Public runtime entry: `index.js` -> `lib/index.js`; public declaration: `index.d.ts`
- Upstream source inventory: one runtime export, `toJsxRuntime`, plus its public
  TypeScript option/runtime types; 74 `node:test` leaves in `test/index.js`.
- Upstream `npm run test-api` passed 74/74 on the host probe. The repository does
  not commit a development lockfile, so the full `npm test` build was not used
  as the task denominator: current caret-resolved TypeScript declarations reject
  three MDX fixtures and one stale `@ts-expect-error`, while runtime behavior
  remains executable.

## Scored Traceability

The private 24-leaf `custom-json-v1` adapter preserves the observable contract
through a child process. Its leaves cover production/development callback
selection, required-option errors, HTML and SVG property conversion, style
handling, table whitespace, generated keys, component replacement and node
passing, MDX JSX literals, MDX expression/ESM evaluation, member components,
attribute/style casing, and development source positions. The private bundle is
content-addressed and is not part of the public instruction.

The evaluator does not import a candidate in the trusted test process. It
copies the candidate workspace, performs an offline npm install with lifecycle
scripts disabled, validates the packed tarball, and launches each JSON request
under the candidate UID. Reward is `clamp(passed / 24, 0, 1)`; collection or
report mismatches invalidate the verifier result.
