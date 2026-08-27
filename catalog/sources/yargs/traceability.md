# yargs Specification Traceability

| Public contract | Private behavior group | Coverage |
| --- | --- | --- |
| ESM package identity and export map | package inventory | root and helper entries, callable shapes, UID 10001 |
| Basic argument parsing | basic argv | positionals, long/equals syntax, short groups, booleans, Unicode |
| Typed options and declarations | option declarations | strings, numbers, arrays, counts, defaults, aliases, combined definitions |
| Validation failures | validation | choices, demand, requiresArg, nargs, implies, strict variants, check |
| Parser configuration | parser behavior | camel case, dot notation, duplicates, `--` modes |
| Transformation | callbacks | scalar/array coercion, middleware mutation, sync/async parity |
| Commands | command handling | command options, required positionals, empty command rejection |
| Help | deterministic help | usage, option name, description, and default |
| Helpers | helper subpath | `hideBin`, `Parser`, configuration; `applyExtends` callable inventory |

Reverse review found no private assertion outside the published instruction.
The instruction's explicitly unscored surfaces have no hidden leaves.
