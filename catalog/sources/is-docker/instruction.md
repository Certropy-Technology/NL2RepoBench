# Build `is-docker`

## Project Description

Create an installable ESM npm package named `is-docker`, version `4.0.0`,
from an empty workspace. The default export reports whether the current
process is running in a Docker container by examining the conventional Docker
environment markers.

The verifier also calls a bounded `run` adapter. This adapter makes the three
observable marker cases deterministic without letting private tests inject
filesystem paths, source code, module specifiers, command strings, or arbitrary
environment data into your package.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, ESM, `linux/amd64`, and glibc.
- `package.json` must set `name` to `is-docker`, `version` to `4.0.0`, and
  `type` to `module`. It must export a safe root ESM entry and expose the
  default function plus named `run` export.
- Commit a compatible npm v3 `package-lock.json`. The clean verifier installs,
  packs, and reinstalls the package without network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

- The package has no runtime dependencies. Do not add workspaces, native
  addons, lifecycle hooks, custom loaders, registry overrides, subprocess
  helpers, generated downloads, or network access.

## API Usage Guide

### Default export `isDocker()`

```ts
export default function isDocker(): boolean;
```

The function is synchronous and returns a boolean. The first invocation checks
these markers in order, short-circuiting after a positive marker:

1. `/.dockerenv` exists.
2. `/proc/self/cgroup` contains the literal substring `docker`.
3. `/proc/self/mountinfo` contains the literal substring `/docker/containers/`.

Read or stat failures are ordinary negative markers and do not throw. Cache the
first computed result for later calls in the same module instance: after the
first call, later calls do not re-read markers and return the cached boolean.

```js
import isDocker from 'is-docker';

if (isDocker()) {
  console.log('Running in Docker');
}
```

### Named adapter `run(request)`

```ts
export type DockerSignals = {
  dockerenv: boolean;
  cgroup: boolean;
  mountinfo: boolean;
};

export function run(request: unknown): unknown;
```

`run` accepts only one plain JSON object. It does not receive filesystem paths,
file content, shell commands, module names, URLs, or arbitrary object keys.
It supports these operations:

- `{op: 'version'}` returns `{version: '4.0.0'}`.
- `{op: 'detect', signals}` returns the Docker decision for exactly the three
  boolean signals. It is `true` if any signal is `true`, with the same marker
  priority as the default export.
- `{op: 'cache', first, second}` returns
  `{first: boolean, second: boolean}`. Compute `first` from `first`; `second`
  must be the cached first decision, not a new decision from `second`.

For both operations, `signals` must contain exactly `dockerenv`, `cgroup`, and
`mountinfo`, each with a boolean value. Reject a malformed request, unknown
operation, extra or missing signal key, or non-boolean signal with an `Error`.

The adapter is a deterministic representation of the documented filesystem
observations. It must use the same decision and caching semantics as the
default export, but must not read real paths when handling an adapter request.

## Implementation Notes

The evaluator invokes only `run` in a UID-isolated candidate child process.
Requests are at most 64 KiB, responses at most 256 KiB, and every call has a
fixed timeout. Candidate code is never imported into the trusted test process.
The verifier owns collection, network probes, grading, and reward files.

The default export may use `node:fs` only for the three documented observations.
Do not expose an API for arbitrary filesystem access and do not let the adapter
accept paths or strings that could act as filesystem input. Exact CLI output,
other container systems, and Docker daemon access are outside the frozen
denominator.
