# Build `execa`

## Project Description

Create a complete, installable npm package named `execa`, version `10.0.1`, from
an empty workspace. The package is an ESM library for running local processes
without a shell by default. This is a repository-generation task: implement the
documented contract with your own code. Do not copy the upstream repository or
its tests.

The scored contract is a deterministic, local subset of the public API of the
frozen Execa revision. It must work on Linux with Node `>=22`, must not contact a
network service, and must not depend on ambient terminal state, a clock, or
randomness for any assertion below.

## Supports

- Use Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must set `"type": "module"`, name the package `execa`, and
  expose `"."` to `./index.js` through the `exports` map.
- Include a committed npm lockfile with `lockfileVersion: 3`.
- The package must have **no runtime npm dependencies**. A clean verifier runs:

  ```sh
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not add lifecycle scripts, custom loaders, registry configuration, native
  addons, or network access.
- All subprocesses in the scored tests are local invocations of the Node binary
  or a temporary script created by the verifier.

## API Usage Guide

### Package exports

The package root must provide these named exports:

```js
import {
  execa,
  execaSync,
  execaNode,
  parseCommandString,
  ExecaError,
  ExecaSyncError,
} from 'execa';
```

`execa`, `execaSync`, and `execaNode` are functions. `ExecaError` and
`ExecaSyncError` are constructible error classes (they may share an
implementation). `parseCommandString` is a pure function.

### `execa(file, arguments?, options?)`

`file` is a program name or absolute path. `arguments` is an array of strings;
each element is passed as one argument without shell splitting. `options` is an
object. The scored options are:

- `cwd`: working directory for the child;
- `env`: environment entries, converted to strings by Node;
- `extendEnv`: defaults to `true`; when `false`, use only the supplied `env`;
- `input`: a string or Uint8Array written to stdin and then closed;
- `reject`: defaults to `true`; when `false`, resolve with a failed result;
- `stripFinalNewline`: defaults to `true`; when `false`, preserve one final
  LF/CRLF in `stdout` and `stderr`;
- `timeout`: positive milliseconds. On expiry terminate the child and report a
  timed-out failure.

The function returns a Promise-like subprocess which resolves to a result on a
zero exit code and rejects with `ExecaError` otherwise (unless `reject: false`).
The result has string `stdout` and `stderr`, integer `exitCode` when available,
boolean `failed`, and the fields `command`, `escapedCommand`, `cwd`,
`timedOut`, `isCanceled`, `isGracefullyCanceled`, `isTerminated`, and
`isMaxBuffer`. A successful result has `failed: false`, `timedOut: false`, and
`exitCode: 0`.

Output is collected as UTF-8 text. With `stripFinalNewline: true`, remove one
final LF or CRLF from each stream. Empty output is the empty string.

The default is `shell: false`: arguments containing spaces or shell metacharacters
must remain a single argument and must not be interpreted by a shell. Supporting
`shell: true` is optional and is not scored.

### Failure contract

For a non-zero exit, the rejected `ExecaError` must have `name: "ExecaError"`,
`failed: true`, `exitCode` equal to the child exit code, captured `stdout` and
`stderr`, and a useful `shortMessage` containing the command and exit code.
For a timeout, set `timedOut: true` and reject unless `reject: false`.

### `execaSync(file, arguments?, options?)`

This is the synchronous equivalent. It returns a result with the same output and
status fields, or throws `ExecaSyncError` on failure unless `reject: false`.
`input`, `cwd`, `env`, `extendEnv`, and `stripFinalNewline` have the same
meaning. The synchronous call must not leave child processes running.

### `execaNode(scriptPath, arguments?, options?)`

Run a JavaScript module using the current Node executable, equivalent to
`execa(process.execPath, [scriptPath, ...arguments], options)`. The script path
may be a string or a file URL. Its arguments must arrive unchanged.

### `parseCommandString(command)`

Return an array of whitespace-separated tokens. Backslash escapes the following
character, including a space. Quotes are ordinary characters for this helper and
are not removed or interpreted. For example:

```js
parseCommandString('node a\\ b') // ['node', 'a b']
parseCommandString('node "a b"') // ['node', '"a', 'b"']
```

## Implementation Notes

- Preserve argument boundaries by using `node:child_process` APIs rather than
  constructing a shell command for the default path.
- Preserve the supplied `cwd` in the result and report a deterministic command
  string for diagnostics. Quoting in `escapedCommand` only needs to make spaces
  and shell-significant characters readable; tests do not require one exact
  quoting algorithm.
- The verifier uses fresh child processes and pipes, so do not rely on TTYs.
- Keep candidate-owned files and any `reward.json` under the workspace from
  influencing grading. The verifier copies the workspace before installing and
  writes its own report outside the candidate tree.
