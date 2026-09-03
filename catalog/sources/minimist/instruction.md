# Build `minimist`

## Project Description

Create a complete installable npm package named `minimist` from an empty
workspace. It is a CommonJS command-line argument parser: the package root
exports one function that accepts an array of argument strings and an optional
options object, then returns a plain JavaScript object describing flags and
positional arguments.

This is a repository-generation task. Implement the documented behavior in
your own package; do not depend on a downloaded copy of the pinned project or
on a command-line parser dependency.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use CommonJS package semantics. `require('minimist')` must return the parser
  function, and `package.json` must expose it through its normal package root.
- Include a committed `package-lock.json` using `lockfileVersion: 3`. The
  verifier installs with `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Do not declare runtime dependencies, native addons, workspaces, custom
  loaders, registry configuration, or lifecycle scripts. The package must not
  require network access during installation or use.
- The function receives only JSON-compatible option objects. Callback-valued
  `unknown` handlers, symbols, custom prototypes, mutation of global
  prototypes, and process argv/environment parsing are outside this task.

## API Usage Guide

### Package root

**Import path:** `require('minimist')`.

**Signature:**

```js
const parse = require('minimist');
const result = parse(args, options?);
```

`args` is an array of strings. `options`, when present, is a plain object that
may contain `boolean`, `string`, `alias`, `default`, `stopEarly`, and `--`.
The return value is a plain object whose `_` property is always an array of
positionals. Property insertion order is not part of the contract.

### Long flags and values

- `--name value` and `--name=value` set `name`. A following non-flag token is
  consumed as the value unless the flag is known boolean.
- `--name` without a value is `true`; `--no-name` is `false`.
- Repeating a non-boolean key preserves values in encounter order: the second
  value changes a scalar into an array, and later values append to that array.
- Numeric-looking values become numbers, including decimal, signed decimal,
  scientific notation, and hexadecimal. Other values remain strings.
- Positional tokens are appended to `_`; numeric-looking positionals use the
  same number conversion unless `_` is listed as a string option.

```js
parse(['--port=8080', '--tag', 'a', '--tag', 'b', 'file'])
// {_: ['file'], port: 8080, tag: ['a', 'b']}
```

### Short flags

- A one-letter flag such as `-v` follows the same capture rules as a long
  flag.
- Combined short letters such as `-abc` set `a` and `b` to `true` and treat
  the final letter as the value-taking flag when a suitable following token
  exists.
- A short option may carry its final value directly: `-n123` means `n: 123`,
  `-s=value` means `s: 'value'`, and `-I/path` means `I: '/path'`.

### Option declarations

`boolean` and `string` may each be a name or an array of names.

- A declared boolean is initialized before parsing: it is its declared default
  when present in `default`, otherwise `false`. It consumes literal following
  `true` or `false` as a Boolean and otherwise leaves a following token in
  `_`.
- `boolean: true` treats all long flags without `=` as booleans.
- A declared string never undergoes numeric conversion. A string flag without
  a value is the empty string.
- `alias` maps a name to one name or an array of equivalent names. Every write
  and default is reflected through every alias. String declarations apply to
  aliases too.
- `default` supplies a value only if the corresponding key was not set while
  parsing. Default and alias names may contain dots.

```js
parse(['-v', '42'], {
  alias: {verbose: 'v'},
  string: 'verbose',
  default: {color: false},
})
// {_: [], v: '42', verbose: '42', color: false}
```

### Dotted names and trailing arguments

Flag names and declared defaults/aliases may use dots to create nested plain
objects. For example, `--db.port 5432` creates `{db: {port: 5432}}`.

`--` terminates flag parsing. With ordinary options, the remaining tokens are
appended to `_` unchanged as strings. With `{ '--': true }`, they are preserved
unchanged in a separate `--` array. With `{stopEarly: true}`, the first
positional and every remaining token are appended to `_` unchanged as strings.

Names containing `__proto__` or a `constructor.prototype` path must not modify
`Object.prototype`, function prototypes, or primitive prototypes. Such writes
are ignored.

## Implementation Notes

- Input ordering is deterministic and repeated values retain encounter order.
- Return only JSON-compatible values for the supported inputs. No terminal,
  browser, filesystem, clock, random source, network, or ambient `process.argv`
  behavior is needed.
- The verifier invokes the package through a child Node process with one
  JSON-compatible request at a time. It does not require you to provide a CLI.
- The scored slice covers package installation, long and short flags, numeric
  coercion, declared string/boolean behavior, aliases/defaults, dotted keys,
  trailing arguments, stop-early parsing, repeated flags, and prototype-pollution
  resistance. Callback-valued `unknown` filtering is intentionally not scored.
