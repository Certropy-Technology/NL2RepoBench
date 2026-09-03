# Minimist Source Freeze and Inventory

## Source freeze

- Upstream: `https://github.com/minimistjs/minimist`.
- Immutable revision: `ecfdaea23e7931c0d529c52b743c711c3278a8ce`.
- Oracle fetch method: `git init`, exact-revision shallow `git fetch`, detached
  checkout, then `git rev-parse HEAD` assertion inside the trusted Oracle.
- `git archive --format=tar HEAD` SHA-256:
  `880c54feb7058c36a6600d35d58a17d834d403b4460cb9c62c33cb455c8adc3c`.
- The frozen tree has no submodules. The package version is `1.2.8`.

The initial trusted Harbor probe is stored under
`.nl2repo/runs/minimist/source-freeze-probe/`; its Oracle workspace contains
the machine-readable `.oracle-source-freeze.json` that binds the revision,
source digest, license digest, and package version.

## License

`package.json` declares `MIT`. The root `LICENSE` file SHA-256 is
`27138518ed50ee99976a8a4c6fe1d5f84cbd8a95c8b9b308a15a5df962801979`.
The declaration and license file agree.

## Public API and tests

The runtime package root is CommonJS and exports one parser function with
signature `parse(args, options?)`. The frozen package's `test/` directory
contains tests for long and short options, boolean/string declarations,
aliases/defaults, dotted keys, `--`, stop-early behavior, number parsing,
repeated values, and prototype pollution resistance.

The upstream development suite uses Tape and range-based development tooling,
so it is not copied into the runtime task. The private 20-leaf `node:test`
slice preserves representative behavior across every API category named in
`instruction.md`; the exact mapping is in `traceability.md`. The trusted test
process invokes a fresh unprivileged child for every candidate request and
never imports the candidate package itself.

## Environment and closure

The task uses the locked `node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
image with Node `24.19.0` and npm `11.17.0`. `minimist` has no runtime
dependencies. Its verifier-owned closure is a package-lock v3 root entry and
an empty npm cache; the compiler validates it and candidate installation uses
offline `npm ci` with lifecycle scripts disabled.
