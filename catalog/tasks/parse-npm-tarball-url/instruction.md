# Build `parse-npm-tarball-url`

## Project Description

Create an installable npm package named `parse-npm-tarball-url`, version
`5.0.0`, from an empty workspace. It is a small ESM utility that parses npm
registry tarball URLs. The scored API is one named runtime export and a
JSON-only subprocess contract; it must not require a network service, a
filesystem checkout, a loader, a clock, or mutable process state.

Reproduce the specified observable behavior with your own package files. The
task is repository generation, not a request to copy the pinned upstream
source or tests.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use ESM semantics: `package.json` must contain `"type": "module"`.
- The package root must be importable as `parse-npm-tarball-url` and must
  expose this root export map:

  ```json
  {
    "exports": {
      ".": {
        "types": "./lib/index.d.ts",
        "default": "./lib/index.js"
      }
    }
  }
  ```

- The runtime entry must be JavaScript ESM and must expose exactly one named
  runtime function, `parseNpmTarballUrl`. Do not expose a default function or
  a CLI as part of the package API. A declaration file may additionally export
  the public TypeScript type.
- Include a v3 `package-lock.json` that agrees with `package.json`. Pin the
  runtime dependency `semver` to exactly `7.7.4`. A clean verifier must be
  able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The package must be usable without a build step after installation. Do not
  require TypeScript, pnpm, `npx`, a global loader, a registry, or a checkout
  path at runtime.
- Do not add `preinstall`, `install`, `postinstall`, `prepare`, `prepublish`,
  `prepublishOnly`, `publish`, or `postpublish` scripts. Do not use native
  addons, workspaces, custom loaders, registry configuration, or network
  access. Development-only files and tools are outside the scored package.
- Do not add a CLI, hidden tests, grader, reward writer, Oracle files, npm
  cache/tarball bytes, credentials, or private verifier material to the
  candidate repository.

## API Usage Guide

### `parseNpmTarballUrl`

**Import path:** the named export from the package root.

**Signature:**

```js
parseNpmTarballUrl(url: string): {
  host: string,
  name: string,
  version: string,
} | null
```

The function is stateless and synchronous. Constructing a WHATWG `URL` parses
the supplied string locally; it does not fetch the URL.

For a URL with a nonempty host and a pathname containing exactly one `/-/`
separator, decode the package portion before the separator with
`decodeURIComponent`. The package portion is the pathname after its leading
slash. Both ordinary names and scoped names are supported. Remove one final
`.tgz` suffix from the filename portion, derive the version after the package
name portion, and accept it when `semver.valid(version, true)` accepts it.
Return the original filename version slice, not a normalized SemVer string:

```js
parseNpmTarballUrl(
  'https://registry.npmjs.org/@scope%2Fpkg/-/pkg-1.2.3-beta.1.tgz'
)
// {host: 'registry.npmjs.org', name: '@scope/pkg', version: '1.2.3-beta.1'}
```

The returned `host` follows WHATWG URL host semantics, including a non-default
explicit port. Query strings and fragments do not change `pathname`. The
protocol is not restricted by this API; a parsed URL with an empty host
returns `null`.

Return `null` when the URL has no host/path, the pathname does not contain
exactly one `/-/` separator, the decoded package name is empty, or the derived
version is not accepted by loose SemVer validation. A malformed percent escape
may throw while decoding instead of returning `null`.

### Errors and JSON boundary

- A falsy input, including `''`, must raise an assertion error with the
  message `url is required`.
- A truthy non-string input must raise an assertion error with the message
  `url should be a string`.
- Malformed or relative URL text may raise the platform `URL` error. The exact
  platform wording is not scored.
- The verifier sends one JSON value as the sole function argument. Values are
  strings, booleans, finite numbers, `null`, arrays, or plain objects only;
  functions, symbols, BigInts, custom prototypes, dates, cycles, and handles
  are outside the boundary. Responses are `null`, the three-string result
  object, or a bounded error record. Do not serialize functions or executable
  strings through this boundary.

The adapter is verifier-owned and is not a candidate CLI requirement. The
candidate function itself must remain directly importable from the package
root.

## Production Slice

The upstream TypeScript development suite is not installed or run. The
frozen denominator is a compact 14-leaf `node:test` slice covering package
shape, simple and prerelease tarballs, scoped and percent-encoded names,
ports/query handling, loose SemVer preservation, malformed and invalid paths,
empty/non-string error behavior, and a null-host URL. Every scored assertion
is derived from the API contract above. The private adapter invokes only the
named export with bounded JSON values and returns JSON values or bounded error
metadata; it never transports source code or JavaScript functions.
