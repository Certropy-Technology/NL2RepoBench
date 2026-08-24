# Build `rollup`

Create a complete, installable npm package named `rollup`, version `4.62.5`,
from an empty workspace. The package is a CommonJS-compatible JavaScript
module bundler with a command-line interface. This is a repository-generation
task: implement the package and its package metadata rather than copying the
private reference package or its tests.

## Supports

- Node `24.19.0` and npm `11.17.0` on `linux/amd64` with glibc.
- A clean verifier runs `npm ci --offline --ignore-scripts --no-audit --no-fund`.
  Commit a v3 `package-lock.json` whose root package is named `rollup` and
  version `4.62.5`.
- The package must have no lifecycle hooks, registry configuration, git
  dependencies, workspaces, or runtime dependency that is absent from the
  lockfile. The scored package is self-contained and must not require a
  native addon or network access at runtime.
- Use the WASM parser/runtime layout used by the frozen Rollup 4.62.5 source:
  the packed package must include the parser's `.wasm` asset and resolve it
  relative to the installed package, not relative to the agent workspace.

## Package surface

`require("rollup")` must return an object containing:

```text
VERSION, rollup, watch, defineConfig
```

`VERSION` is the string `4.62.5`. The package metadata must expose
`dist/rollup.js` through `main`, `dist/rollup.d.ts` through `types`, and a
`rollup` executable through `bin`. Keep the CommonJS root import working and
provide TypeScript declarations for the public entry point.

## JavaScript API behavior

- `rollup({ input })` returns a Promise for a bundle. Local relative imports
  are resolved and included in the graph.
- `bundle.generate({ format: "es" | "cjs" | "iife", name? })` returns a
  result with an `output` array. Each generated chunk has a string `code`, a
  `fileName`, and a `type` of `chunk` or `asset`.
- Tree-shake unused exports in ordinary local modules. Preserve used exports
  and generate valid JavaScript for the requested format.
- Plugin objects may implement `resolveId`, `load`, and `transform`; their
  results must participate in the bundle.
- An `external` module remains an import/require in generated output instead
  of being read from the local filesystem.
- `bundle.write({ file, format })` writes the generated output to the requested
  path, and `bundle.close()` releases resources. Invalid input rejects with an
  Error carrying a stable Rollup error `code` such as `UNRESOLVED_ENTRY`.
- Multiple outputs and code splitting must produce deterministic file names and
  valid output objects for ordinary local input.

## CLI behavior

- `rollup --version` prints `rollup v4.62.5` and exits successfully.
- With an input file and `--format es|cjs|iife --file <path>`, the CLI writes a
  bundle to the requested file. `-` may be used for stdin input and stdout
  output.
- Missing files and invalid options exit nonzero and print a useful diagnostic
  to stderr.

## Package hygiene

Do not include tests, `.git`, registry credentials, host-specific absolute
paths, lifecycle hooks, or native `.node` addons in the packed package. Do not
use network access at runtime. The package must pass the fixed private checks
after being packed and installed with lifecycle scripts disabled.

## Implementation notes

The source revision and environment in the task metadata are authoritative.
Implement the documented behavior from the public contract; do not rely on the
private test files, a hidden reference package, or access to GitHub/npm during
the agent run.
