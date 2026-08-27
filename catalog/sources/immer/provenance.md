# Immer authoring provenance

## Frozen source

- upstream: `https://github.com/immerjs/immer`
- revision: `061c2425e1c9dff89e4e4189d42af1b7839dfe0a`
- commit: `chore(test): pin draft prototype-inspection behavior restored by #1271 (#1272)`
- license: MIT; `LICENSE` is present in the detached tree
- `git archive --format=tar <revision>` SHA-256:
  `df0a2fcf83800ad4878408db7d3d7cb8f4fd5a77352246a770b988e7d2401cbc`
- detached archive and source checkout are task-local under
  `.nl2repo/authoring-work/node-discovery-20260826-r1/immer/`.

## Runtime probe

The authoring host reports Node `v22.23.1` and npm `10.9.8`. A normal
`npm install --ignore-scripts` failed with npm peer-resolution error `ERESOLVE`
because `@vitest/coverage-v8@2.1.9` peers with Vitest `2.1.9` while the frozen
manifest requests Vitest `^3.2.6`. The bounded remediation
`npm install --legacy-peer-deps --ignore-scripts --no-audit --no-fund` succeeded.
The upstream `vitest run` portion passed 3764 tests with 8 skips; the full
`npm test` command then failed only because Yarn is not installed (`exit 127`).
The frozen TypeScript build `npm run build` succeeded and emitted the ESM/CJS
runtime and declaration files.

The production task does not install the upstream development closure. It has
zero runtime dependencies and uses a private root-only npm v3 cache bundle.
The trusted Oracle package was built from this exact detached revision; hidden
tests and the Oracle runtime remain private artifacts.

## Scope and traceability

The original suite exercises proxy internals, callbacks, TypeScript types,
plugins, Map/Set, and many JavaScript-only values. The production contract
retains the JSON-observable core: copy-on-write object/array mutation, array
methods, replacement/nothing, freeze settings, patches, draft lifecycle,
inspection, draftability, and package shape. The private 24-leaf test plan is
bidirectionally mapped in `evidence/traceability.json` and does not use source
tests as hidden instructions.
