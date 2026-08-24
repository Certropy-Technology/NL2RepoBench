# Build a bounded JSON ESM utility

Create a zero-dependency npm package named `node-synthetic` using one ESM entry
point. The package must expose the following JSON-serializable functions from
its package export:

- `normalize(value)`: accept a JSON string, parse it, and return an object with
  keys sorted recursively. Reject invalid JSON with a regular `Error`.
- `stableStringify(value)`: return deterministic JSON with object keys sorted
  recursively and no insignificant whitespace.
- `summarize(values)`: accept an array of JSON values and return an object with
  `count`, `first`, and `last`; for an empty array, `first` and `last` are
  `null`.

Use `package.json` with an ESM `exports` entry, a committed v3
`package-lock.json`, and no runtime dependencies. The package must install
with `npm ci --offline --ignore-scripts` and must not declare lifecycle scripts,
native addons, workspaces, loaders, or registry configuration.
