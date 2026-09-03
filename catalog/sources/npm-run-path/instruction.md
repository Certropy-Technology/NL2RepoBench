# Build `npm-run-path`

## Project Description

Create a complete installable npm package named `npm-run-path`, version
`6.0.0`, from an empty workspace. The package augments a PATH string with
directories for locally installed executables and the running Node executable.
Reproduce the observable behavior of the pinned `sindresorhus/npm-run-path`
revision on the declared Linux runtime.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- ESM package semantics using `"type": "module"`.
- The package root must expose exactly the named runtime exports `npmRunPath`
  and `npmRunPathEnv`. TypeScript declarations must be available through
  `index.d.ts`.
- A committed npm v3 lockfile that installs with:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Declare the runtime dependencies `path-key` and `unicorn-magic`. Resolve them
  to the exact versions available in the supplied offline closure. Do not use
  git, file, workspace, native-addon, or network dependencies.
- `npm pack --ignore-scripts` must produce an installable package. Do not rely
  on a prepare hook, generated files, a global compiler, or a download at
  evaluation time.

## API Usage Guide

### `npmRunPath(options?)`

**Import path:** named export from the package root.

```js
import {npmRunPath} from 'npm-run-path';

npmRunPath({
  cwd: '/srv/app',
  path: '/usr/bin:/bin',
  execPath: '/usr/local/bin/node',
});
```

**Signature:**

```ts
function npmRunPath(options?: RunPathOptions): string;
```

`options` has these fields:

| Field | Type | Default | Behavior |
| --- | --- | --- | --- |
| `cwd` | `string \| URL` | `process.cwd()` | Starting directory for local executable paths. Relative values resolve against the process working directory. |
| `path` | `string` | the platform PATH from `process.env` | Original PATH string appended after generated entries. |
| `preferLocal` | `boolean` | `true` | Prepends `node_modules/.bin` for `cwd` and each parent through the filesystem root, nearest first. |
| `execPath` | `string \| URL` | `process.execPath` | Node executable path. Relative values resolve against `cwd`. |
| `addExecPath` | `boolean` | `true` | Prepends the directory containing `execPath`, after local executable directories. |

On Linux, PATH entries use `:`. Generated entries already present as complete
segments of the original `path` are not added again. Existing segments keep
their order and duplicates. The function only computes strings; directories
and executables do not need to exist.

When `path` is an empty string, return only the enabled generated entries with
no trailing separator. When both switches are false, return `path` unchanged,
including an empty string. A `path` equal to one separator retains one trailing
separator without introducing an extra empty segment. Leading and trailing
empty segments in other non-empty PATH strings are preserved.

Examples on Linux:

```js
npmRunPath({
  cwd: '/work/app',
  path: '/bin',
  execPath: '/opt/node/bin/node',
  preferLocal: false,
});
// '/opt/node/bin:/bin'

npmRunPath({path: '/a:/b', preferLocal: false, addExecPath: false});
// '/a:/b'
```

The return value is a string. The function does not mutate the options object.
Invalid path-like values and a non-string `path` retain the ordinary Node
`TypeError` behavior instead of being coerced.

### `npmRunPathEnv(options?)`

**Import path:** named export from the package root.

**Signature:**

```ts
type ProcessEnv = Record<string, string | undefined>;

function npmRunPathEnv(options?: EnvOptions): ProcessEnv;
```

This function accepts the common `cwd`, `execPath`, `preferLocal`, and
`addExecPath` options plus:

| Field | Type | Default | Behavior |
| --- | --- | --- | --- |
| `env` | `ProcessEnv` | `process.env` | Environment object to clone and augment. |

Return a shallow clone. Preserve every unrelated key and leave the supplied
object unchanged. Select the platform's PATH key, then compute its value with
`npmRunPath`. The scored runtime is Linux, so the selected key is `PATH` and a
differently cased key such as `Path` remains an unrelated preserved key. If
the supplied object has no `PATH` value, the nested `npmRunPath` call uses the
child process PATH default.

```js
const input = {PATH: '/bin', KEEP: 'yes'};
const output = npmRunPathEnv({
  env: input,
  cwd: '/work/app',
  execPath: '/opt/node/bin/node',
  preferLocal: false,
});

output.PATH; // '/opt/node/bin:/bin'
output.KEEP; // 'yes'
input.PATH; // '/bin'
```

## Implementation Notes

- Keep the runtime entry point and declarations at `index.js` and `index.d.ts`.
- Package files must be ready before installation. Lifecycle scripts and the
  upstream development-only AVA/XO/tsd toolchain are not part of the runtime
  package.
- Preserve URL-to-path conversion, nearest-first parent traversal, exact PATH
  segment handling, option defaults, and environment cloning.
- Do not add a CLI, subprocess execution, filesystem writes, network access,
  native addon, custom loader, or extra runtime export.
- Do not include hidden tests, verifier code, Oracle files, reward files,
  credentials, private npm cache bytes, or generated Harbor assets in the
  candidate repository.
