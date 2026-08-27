# Build `until-async`

## Project Description

Create an installable npm package named `until-async`, version `3.0.2`, from an
empty workspace. The package converts the outcome of one promise-producing
callback into a two-element tuple, allowing callers to handle success and
failure without surrounding each awaited operation with `try`/`catch`.

The catalog source path retains the historical discovery identity
`@open-draft/until`. The frozen revision's actual npm identity is
`until-async`, and that npm identity is authoritative for the repository you
must build. Do not copy upstream source or tests into the generated repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must name `until-async` version `3.0.2`, use
  `"type": "module"`, and expose a safe in-package ESM root entry.
- Use `./build/index.js` as `main` and the root default export condition. Use
  `./build/index.d.ts` as `types` and the root types condition. Export
  `./package.json` at `./package.json`.
- The runtime module has exactly one named export, `until`, and no default
  export.
- Include a v3 `package-lock.json` for the package. Declare no runtime or
  development dependencies, npm scripts, lifecycle hooks, workspaces, native
  addons, custom loaders, registry configuration, or network requirements.
- A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

The workspace must contain the already runnable JavaScript and declaration
files. The evaluation environment does not provide TypeScript or a build tool
and will not download one.

## Bounded Execution Contract

The verifier never imports candidate code into its trusted test process. It
starts an unprivileged, resource-bounded child that imports the installed
package and constructs allowlisted callbacks inside that child. Requests and
responses are JSON objects no larger than 32 KiB and 128 KiB respectively.
At most 16 independent calls are made in one scenario.

Callback fulfillment values and non-Error rejection reasons crossing this
boundary are JSON null, booleans, finite numbers, strings, arrays, or ordinary
objects. The child also checks `undefined` fulfillment and standard `Error`
name/message pairs. No callback source, executable string, function, symbol,
BigInt, cyclic object, custom prototype, accessor, filesystem path, random
state, or wall-clock assertion crosses the boundary.

## API Usage Guide

### `UntilResult`

```ts
export type UntilResult<RejectionReason, ResolveData> =
  | [reason: RejectionReason, data: null]
  | [reason: null, data: ResolveData]
```

This two-element tuple is a discriminated union. A failure occupies the first
slot and puts `null` in the data slot. A success puts `null` in the reason slot
and preserves the fulfilled value in the data slot. Do not omit tuple entries
or substitute `undefined` for either required `null` sentinel.

### `until`

```ts
export function until<RejectionReason = Error, ResolveData = unknown>(
  callback: () => Promise<ResolveData>,
): Promise<UntilResult<RejectionReason, ResolveData>>
```

Invoke `callback` exactly once. If its returned promise fulfills, resolve to
`[null, data]` with the value unchanged, including `null`, `false`, `0`, or
`undefined`. If the callback throws synchronously or its promise rejects,
resolve to `[reason, null]` with the thrown or rejected reason unchanged.
For a callback satisfying the declared signature, `until` resolves with one
of those tuples instead of propagating the callback failure as a rejection.

Example:

```js
import { until } from 'until-async';

const [error, data] = await until(async () => {
  return { id: 7, state: 'ready' };
});

// error is null
// data is { id: 7, state: 'ready' }
```

Independent calls must not share mutable result state. Concurrent calls settle
according to their own callback while `Promise.all` preserves input order.

## Implementation Notes

Keep the implementation deterministic and side-effect free except for invoking
the supplied callback. Do not inspect, transform, stringify, clone, log, or
coerce fulfillment values or failure reasons. The frozen verifier contains 18
`node:test` leaves adapted from the pinned runtime and declaration tests plus
documented boundary cases for falsey values, synchronous throws, delayed
settlement, exact callback count, package metadata, and independent parallel
calls.
