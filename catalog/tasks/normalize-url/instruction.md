# Build `normalize-url`

## Project Description

Create an installable npm package named `normalize-url`, version `9.0.1`, from an empty workspace. The package is an ESM utility whose default export synchronously normalizes URL text into a deterministic canonical string. The task is repository generation: implement the observable contract with your own package files rather than copying the pinned upstream source or tests.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use ESM semantics with `package.json` containing `"type": "module"`.
- The package root must expose exactly the default runtime export through this map:

  ```json
  {"exports":{"types":"./index.d.ts","default":"./index.js"}}
  ```

- Include a v3 `package-lock.json` that agrees with `package.json`. This package has no runtime dependencies. A clean verifier runs `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- The package must work after installation without TypeScript, a loader, a registry, a network service, a clock, or a checkout path at runtime.
- Do not add lifecycle scripts (`preinstall`, `install`, `postinstall`, `prepare`, `prepublish`, `prepublishOnly`, `publish`, or `postpublish`), workspaces, native addons, custom loaders, registry configuration, or a CLI. Do not include grader, reward, hidden-test, cache, credential, or Oracle files.

## API Usage Guide

### `normalizeUrl`

**Import path:** the default export from the package root.

**Signature:**

```js
normalizeUrl(url: string, options?: Options): string
```

The function is synchronous and stateless. Trim the input and normalize ordinary URL text using WHATWG URL semantics. Human-friendly host text without a protocol receives `defaultProtocol`, which defaults to `http`. Protocol-relative input (`//host/path`) also receives that protocol unless `normalizeProtocol` is false, in which case the leading `//` is retained.

By default, normalize `http:`, `https:`, `file:`, and `data:` URLs. Unknown custom protocols are returned unchanged unless their protocol is listed in `customProtocols`; listed custom protocols receive the same host/path/query normalization. The `data:` form is normalized locally by lowercasing its media type and charset, removing the default `text/plain;charset=us-ascii` spelling, preserving payload bytes, and preserving the hash unless `stripHash` is true.

The default output removes URL authentication, one `www.` prefix for ordinary domains, tracking query keys matching `/^utm_\w+/i`, trailing path slashes, and a sole root slash. It sorts remaining query keys while preserving duplicate-key order and the distinction between empty `key` and `key=` according to `emptyQueryValue` (`preserve`, `always`, or `never`). It removes default HTTP/HTTPS ports through WHATWG serialization, but keeps non-default ports unless `removeExplicitPort` is true. It decodes safe URI octets in the pathname, removes dot-segment traversal through URL parsing, and retains encoded backslashes.

Supported options and observable behavior:

- `defaultProtocol: 'http' | 'https'`: protocol for host-like and protocol-relative input; a trailing `:` is accepted.
- `customProtocols: string[]`: protocol names that should receive host/path/query normalization instead of being returned unchanged.
- `normalizeProtocol: boolean`: preserve `//` when false.
- `forceHttp` and `forceHttps`: rewrite the corresponding HTTP(S) protocol. Supplying both throws `The \`forceHttp\` and \`forceHttps\` options cannot be used together`.
- `stripAuthentication`: defaults true; false preserves `user:password@`.
- `stripHash`: remove the entire fragment when true.
- `stripProtocol`: remove an `http:`, `https:`, or protocol-relative prefix from the final output when true.
- `stripTextFragment`: defaults true; remove a `:~:text...` suffix from a fragment while retaining the preceding fragment.
- `stripWWW`: defaults true; false preserves `www.`.
- `removeQueryParameters`: an array of exact string keys and/or regular expressions, `true` for all keys, or `false` for none. JSON tasks can use string keys; regex-valued callbacks are outside the subprocess boundary.
- `keepQueryParameters`: an array of exact string keys; when present it overrides removal and keeps only matching keys.
- `removeTrailingSlash`: defaults true; false preserves a trailing slash on a non-root path.
- `removeSingleSlash`: defaults true; false preserves the sole `/` after a host.
- `removeDirectoryIndex`: true removes a final `index.<letters>` component; an array of string names removes matching final components.
- `removeExplicitPort`: remove any explicit non-default port.
- `sortQueryParameters`: defaults true; false preserves input query order.
- `emptyQueryValue`: `preserve`, `always`, or `never` controls empty query values.
- `removePath`: replace the pathname with `/` before normal output trimming.

`transformPath` is a function-valued option and is intentionally outside the JSON subprocess contract. The same applies to regular-expression option values and other executable values. The verifier sends only JSON-compatible values and checks the default export through a separate child process.

## Implementation Notes

Keep the package root directly importable. Return a string for every supported input. Preserve URL query values and encoded reserved characters as URL text, and avoid network, filesystem, environment, process-global, random, or time-dependent behavior. Invalid URL text may throw the platform `URL` error. The verifier owns the candidate adapter, fixed leaf collection, grading, and network proof.
