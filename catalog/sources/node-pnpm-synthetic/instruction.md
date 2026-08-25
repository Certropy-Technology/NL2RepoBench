# Build a bounded JSON ESM utility with pnpm

Create a zero-dependency package named `node-pnpm-synthetic` using one ESM
entry point. Export `normalize(value)`, `stableStringify(value)`, and
`summarize(values)` with deterministic JSON behavior matching the examples in
the private contract tests. Use a pnpm v9 lockfile and do not use lifecycle
scripts, native addons, workspaces, loaders, or registry configuration.
