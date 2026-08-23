# Build `chalk`

## Project Description

Create a complete installable npm package named `chalk`, version `6.0.0`, from
an empty workspace. It is an ESM terminal string styling library. The scored
contract is the JSON-compatible, subprocess-safe subset of the public Chalk
API described here. It must produce strings and JSON metadata; it must not
require a terminal UI, a network service, a clock, random state, or a browser.

The package is a repository-generation task, not a request to copy the pinned
upstream source or tests. Reproduce the specified behavior with your own
implementation and package files.

## Supports

- Run on Node `22.23.1` with npm `10.9.8` on `linux/amd64`.
- Use ESM package semantics. `package.json` must contain `"type": "module"`.
- The package root must be importable as `chalk` and must expose an
  `exports["."]` map with a runtime default entry and a TypeScript declaration
  entry. The runtime entry must be JavaScript ESM and must not be a CommonJS
  shim.
- The package must include the source files needed by its package exports and
  a committed npm lockfile with `lockfileVersion: 3`. A clean verifier must
  support:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not declare runtime dependencies. Color conversion and terminal
  capability logic must be implemented in the package itself or in vendored
  source files. Do not use native addons, workspaces, custom loaders, registry
  configuration, or network access.
- Do not add `preinstall`, `install`, `postinstall`, `prepare`, `prepack`, or
  `postpack` lifecycle scripts. The verifier disables lifecycle scripts and
  does not run a publish or browser-bundle workflow.
- The default scored formatting path receives an explicit color `level` from
  the JSON boundary below. Ambient terminal detection is tested only in a
  separately controlled process and must not leak host state into ordinary
  formatting calls.

## API Usage Guide

### Package root and exports

The package root must support this ESM import shape:

```js
import chalk, {
  Chalk,
  chalkStderr,
  supportsColor,
  supportsColorStderr,
  modifierNames,
  foregroundColorNames,
  backgroundColorNames,
  underlineColorNames,
  colorNames,
} from 'chalk';
```

The default export and `chalkStderr` are callable Chalk instances. `Chalk` is
a constructible class that returns a callable instance. The four `*Names`
exports and `colorNames` are arrays of strings. The compatibility aliases
`modifiers`, `foregroundColors`, `backgroundColors`, and `colors` must refer to
the corresponding name arrays. `supportsColor` and `supportsColorStderr` are
either `false` or an object with JSON-compatible fields `level`, `hasBasic`,
`has256`, and `has16m`.

Type-only declarations do not need runtime exports. The scored runtime
surface is the default function, the `Chalk` constructor, the named values,
and the style methods described below.

### `Chalk`

**Import path:** `Chalk` from the package root.

**Signature:**

```js
new Chalk(options?)
```

`options` may be omitted or may be an object with an optional `level` field.
An explicit level is an integer from `0` through `3`:

- `0`: styling is disabled and ordinary styles return the unmodified text;
- `1`: basic 16-color ANSI output is enabled;
- `2`: ANSI 256-color output is enabled;
- `3`: truecolor output is enabled.

An invalid level must raise an ordinary `Error`. The returned value is
callable and exposes a mutable `level` property. Assigning a value outside
the integer range must also raise an ordinary `Error`, without changing the
previous valid level. A builder obtained after chaining styles shares the
root instance's level; changing the root or a builder changes the other.

When `level` is omitted, detection may use the process environment and stream
state as described in **Terminal determinism**. The JSON formatting boundary
always supplies an explicit level.

### Default callable and style builders

**Import path:** the default `chalk` export or any callable style builder.

**Signature:**

```js
chalk(...values)
chalk.red.bold(...values)
```

The callable joins its arguments with one ASCII space. Each JSON value is
converted using JavaScript string conversion on the ordinary parsed JSON
value. In-scope values are strings, booleans, `null`, finite numbers, arrays,
and plain JSON objects, recursively. Thus `null` becomes `"null"`, a finite
number uses its normal JavaScript string form, an array uses its normal
comma-joined string form, and a plain object uses its ordinary
`"[object Object]"` form. `undefined`, symbols, functions, BigInt, dates,
custom prototypes, custom `toString` methods, non-finite numbers, and cyclic
values are outside the scored boundary.

With zero arguments the result is an empty string. With no styling, the result
is the joined string. With styling enabled, the builder wraps the complete
text in ANSI open/close sequences. An empty text produces an empty string and
does not emit escape codes. A newline is closed and reopened so styling does
not bleed across lines; both LF and CRLF must be preserved in the text.

The following modifier builders are required:

```text
reset bold dim italic underline underlineDouble underlineCurly
underlineDotted underlineDashed overline inverse hidden strikethrough visible
```

The following foreground builders are required:

```text
black red green yellow blue magenta cyan white blackBright gray grey
redBright greenBright yellowBright blueBright magentaBright cyanBright
whiteBright
```

The following background builders are required:

```text
bgBlack bgRed bgGreen bgYellow bgBlue bgMagenta bgCyan bgWhite
bgBlackBright bgGray bgGrey bgRedBright bgGreenBright bgYellowBright
bgBlueBright bgMagentaBright bgCyanBright bgWhiteBright
```

The following underline-color builders are required:

```text
underlineBlack underlineRed underlineGreen underlineYellow underlineBlue
underlineMagenta underlineCyan underlineWhite underlineBlackBright
underlineGray underlineGrey underlineRedBright underlineGreenBright
underlineYellowBright underlineBlueBright underlineMagentaBright
underlineCyanBright underlineWhiteBright
```

Style builders are chainable. The order of a chain determines the order of
the open sequences and the reverse order of the close sequences. Nested styled
strings must be reopened when an inner string contains a close sequence. A
later style of the same family may replace an earlier conflicting style.
`visible` returns the text only when the effective level is greater than zero;
otherwise it returns an empty string.

### Color-model builders

The following builders are required and are chainable to an eventual callable:

```js
chalk.rgb(red, green, blue)
chalk.hex(color)
chalk.ansi256(index)
chalk.bgRgb(red, green, blue)
chalk.bgHex(color)
chalk.bgAnsi256(index)
chalk.underlineRgb(red, green, blue)
chalk.underlineHex(color)
chalk.underlineAnsi256(index)
```

For the scored boundary, RGB components and ANSI indexes are finite JSON
numbers in the usual `0..255` domain, and hex colors are strings accepted by
the package's hex conversion behavior. At level `1`, RGB and hex colors are
downsampled to basic ANSI codes; at level `2`, they use ANSI 256 codes; at
level `3`, RGB and hex use truecolor codes while ANSI 256 values remain in
their 256-color form. Underline colors use the corresponding `58`/`59`
sequences.

### Terminal capability values

`supportsColor` describes stdout capability and `supportsColorStderr`
describes stderr capability. A support object has:

```js
{
  level: 0 | 1 | 2 | 3,
  hasBasic: boolean,
  has256: boolean,
  has16m: boolean,
}
```

The values are computed when the module is loaded. Their environment policy
is specified below; a verifier must launch a new child process for each
environment/argv case rather than mutating environment variables after
import.

## Terminal determinism

Color detection may inspect `FORCE_COLOR`, `TERM`, `COLORTERM`, `CI`, selected
CI variables, `TERM_PROGRAM`, `process.argv` color flags, `process.platform`,
and whether stdout/stderr are TTYs. A deterministic verifier must therefore:

- run candidate children with stdout and stderr as pipes, not a host TTY;
- use `TERM=dumb`, `CI=true`, `LC_ALL=C.UTF-8`, and no `COLORTERM` for the
  default no-color environment;
- remove `FORCE_COLOR`, color flags, proxy/registry variables, loader options,
  and host-specific terminal variables unless a detection case explicitly
  supplies one; and
- use explicit `new Chalk({level})` for all ordinary formatting assertions.

Detection cases may explicitly supply `FORCE_COLOR=0`, `FORCE_COLOR=1`,
`FORCE_COLOR=true`, `COLORTERM=truecolor`, `TERM=xterm-256color`, or
`--color=256`/`--color=16m` in the child argv. The expected level must be
derived from that complete isolated launch, not from the evaluator's ambient
environment. Windows behavior, host-specific TTY dimensions, and terminal
control protocols other than the SGR sequences emitted by styles are outside
the scored contract.

## JSON-safe subprocess boundary

The verifier-facing boundary is one request and one response per UTF-8 JSONL
line. A request has a string `id`, an operation, and a JSON object payload. The
proposed operation contract is recorded in `candidate-boundary.json`:

- `format` accepts an explicit level, a chain of style steps, and JSON values,
