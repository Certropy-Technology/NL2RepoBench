# Build `yargs`

## Project Description

Create a complete installable npm package named `yargs`, version `18.1.0`,
from an empty workspace. The package is an ESM command-line argument parser.
It must expose a callable package-root factory that builds a fluent parser,
plus the documented `yargs/helpers` helper exports. The scored contract is a
deterministic JSON-compatible subset of the public runtime API: parsing,
option typing, aliases, defaults, parser configuration, validation, commands,
middleware, coercion, help generation, and helper functions.

This is a repository-generation task. Implement the behavior described here
without retrieving a reference implementation or hidden tests.

## Supports

- Node `24.19.0`, npm `11.17.0`, `linux/amd64`, and ESM semantics.
- `package.json` must have `name: "yargs"`, `version: "18.1.0"`, and
  `type: "module"`.
- The package export map must expose the root as `./index.mjs`, the alias
  `./yargs` as `./index.mjs`, `./helpers` as `./helpers/helpers.mjs`, and
  `./package.json`. The root module has a default callable export and a named
  callable export whose name is the string `module.exports`.
- A committed npm v3 lockfile. A clean verifier runs both of these without
  network access or lifecycle scripts:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

- A self-contained implementation is allowed. If you use runtime packages,
  only these exact direct versions are available in the offline cache:
  `cliui@9.0.1`, `escalade@3.2.0`, `get-caller-file@2.0.5`,
  `string-width@8.2.1`, `y18n@5.0.8`, and `yargs-parser@22.0.0`.
- Do not use workspaces, native addons, custom loaders, network access,
  runtime downloads, arbitrary shell commands, or lifecycle hooks such as
  `preinstall`, `install`, `postinstall`, `prepare`, or `prepack`.

## API Usage Guide

### Package-root factory

```js
import yargs from 'yargs';

const parser = yargs(argv);
```

`argv` is either a shell-style argument string or an array of strings. The
factory returns a fluent parser. Configuration methods return the parser so
they can be chained. Parsing does not mutate the caller's input array.

The parser exposes `parse()`, `parseSync()`, and `parseAsync()`. For a fully
synchronous configuration, `parseSync()` returns an object and `parseAsync()`
resolves to the same object. Parsed output always contains `_`, an array of
positional values, and normally contains `$0`, the executable name. The
subprocess scoring boundary omits `$0` because it depends on the launch path.

Ordinary untyped option values use parser-compatible scalar coercion:
numeric-looking values become numbers, options without a value become
`true`, and repeated options become arrays. A short group such as `-abc`
sets `a`, `b`, and `c` to `true`. `--no-cache` sets a declared boolean
`cache` to `false`. Arguments after `--` remain positional unless the parser
configuration `populate--` is enabled, in which case they are stored under
the key `--`.

### Option declarations

Support these fluent methods with either one key or, where conventional, an
array/dictionary of keys:

```js
alias(key, alias)
array(keys)
boolean(keys)
choices(key, values)
count(keys)
default(key, value)
describe(key, description)
nargs(key, count)
number(keys)
option(key, definition)
options(definitions)
requiresArg(keys)
string(keys)
```

`option()` definitions support `alias`, `type`, `array`, `choices`,
`default`, `demandOption`, `description`/`describe`, `nargs`, and
`requiresArg` as applicable. Aliases are populated alongside the canonical
key. String options preserve spelling such as `"0012"`; number options
produce numbers; arrays collect repeated values; counts accumulate grouped
short flags; and defaults are inserted only when an option is absent.

### Parser configuration

`parserConfiguration(configuration)` changes parser behavior. The scored
surface includes:

- `camel-case-expansion` (default `true`): `--dry-run` also produces
  `dryRun`; disabling it leaves only `dry-run`;
- `dot-notation` (default `true`): `--db.host localhost` produces
  `{db: {host: "localhost"}}`;
- `duplicate-arguments-array` (default `true`): repeated values become an
  array; and
- `populate--` (default `false`): controls whether trailing arguments are
  stored in `_` or under `--`.

### Validation

Support `demandOption()`, `demandCommand()`, `requiresArg()`, `nargs()`,
`choices()`, `implies()`, `check()`, `strict()`, `strictOptions()`, and
`strictCommands()`. With `exitProcess(false)`, validation failures throw an
ordinary `Error` rather than terminating the process. The message identifies
the relevant option or command and the failure class, for example a missing
required argument, an unknown argument, an invalid choice, an implication
failure, or an insufficient value count.

`check(callback)` runs after parsing. A callback may return `true`, return a
string describing the failure, or throw an error. A returned string or thrown
error fails parsing with that message.

### Coercion and middleware

`coerce(key, callback)` replaces the parsed value with the callback result;
the result may be a scalar or a JSON-compatible array/object.

`middleware(callback, applyBeforeValidation?)` runs for parsed arguments. A
middleware callback may mutate `argv` or return a partial object whose fields
are merged into `argv`. Global middleware applies to command parsing as well
as top-level parsing. Promise-returning middleware makes asynchronous parsing
necessary; synchronous middleware remains compatible with `parseSync()`.

### Commands

```js
parser.command(command, description, builder, handler)
```

`command` supports a command name and required positional declarations such
as `copy <source> <dest>`. `builder` may be an option-definition object or a
function returning a configured parser. When the command matches, `handler`
receives the parsed command options and positional values. `demandCommand(1)`
rejects an empty command line.

### Help

`usage(message)` sets the usage line. `getHelp()` returns a promise resolving
to help text. The text includes the configured usage, option names,
descriptions, aliases, choices, required markers, and defaults. `wrap(cols)`
controls formatting width. `help(false)` disables automatic `--help`
handling without disabling `getHelp()`.

### `yargs/helpers`

```js
import {applyExtends, hideBin, Parser} from 'yargs/helpers';
```

- `hideBin(argv = process.argv)` returns `argv.slice(2)` and does not mutate
  the input.
- `Parser(argv, options?)` exposes the argument parser directly. It accepts a
  string or string array and returns parsed JSON-compatible arguments. Parser
  options include typed key arrays and the `configuration` object described
  above.
- `applyExtends(config, cwd, mergeExtends)` resolves the public configuration
  extension behavior. The fixed scored denominator inventories this callable
  export but does not read candidate-controlled external configuration files.

## Implementation Notes

The verifier uses a fixed, verifier-owned JSON request/response adapter because
the fluent parser and callbacks are not serializable as direct function
arguments. It launches candidate code in a separate bounded Node process as a
non-root user. Requests select only the public operations documented above;
they cannot provide source code, arbitrary module names, or shell commands.

Keep behavior deterministic under `TERM=dumb`, `CI=true`, `FORCE_COLOR=0`, and
the English locale used by the task. Preserve Unicode strings, alias identity,
positional order, synchronous/asynchronous parity, and informative validation
errors. Browser, Deno, completion shell scripts, locale file loading, command
directory discovery, environment-variable parsing, external config files,
and non-JSON values are outside the fixed scored denominator.
