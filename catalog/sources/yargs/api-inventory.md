# yargs API Inventory

## Frozen package surface

- Package: `yargs@18.1.0`
- Root ESM entry: `index.mjs`, default callable factory plus named
  `module.exports` callable compatibility export.
- Public subpaths: `.`, `./yargs`, `./helpers`, `./browser`, and
  `./package.json`.
- Helper runtime exports: `Parser`, `applyExtends`, and `hideBin`.

The frozen `YargsInstance` class contains 69 public methods. The scored slice
selects the JSON-deterministic repository-generation core: factory creation,
parse/parseSync/parseAsync, option declarations, parser configuration,
validation, commands, coercion, middleware, help text, and helpers.

## Scored method families

| Family | Public members |
| --- | --- |
| Parse | `parse`, `parseSync`, `parseAsync` |
| Types and values | `array`, `boolean`, `count`, `default`, `number`, `string` |
| Declarations | `alias`, `choices`, `describe`, `nargs`, `option`, `options` |
| Validation | `check`, `demandCommand`, `demandOption`, `implies`, `requiresArg`, `strict`, `strictCommands`, `strictOptions` |
| Transformation | `coerce`, `middleware`, `parserConfiguration` |
| Commands and help | `command`, `usage`, `getHelp`, `wrap` |
| Helpers | `Parser`, `hideBin`; callable inventory for `applyExtends` |

## Explicitly unscored surfaces

Browser and Deno shims, completion shell generation, locale file loading,
external config and command-directory discovery, ambient environment parsing,
TTY behavior, and non-JSON callback values are excluded because they require
additional platform or filesystem contracts beyond the fixed subprocess
boundary. They remain visible in the source inventory and are not represented
as silently required hidden behavior.
