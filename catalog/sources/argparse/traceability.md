# Argparse Specification Traceability

| Public contract | Private behavior group | Coverage |
| --- | --- | --- |
| Package identity and CommonJS exports | package-shape | name/version/main, all required exports, constants |
| Basic positional and optional parsing | basic-parse | positionals, long/short options, equals syntax, Unicode |
| Typed declarations | typed-options | int/float/string, nargs, choices, aliases, defaults |
| Standard actions | actions | store_true, store_false, store_const, append, count |
| Parser errors | validation | required options, invalid choices, unknown arguments, nargs |
| Groups and subparsers | composition | mutually-exclusive groups, argument groups, child parser |
| Help and namespace | presentation | deterministic usage/help, custom namespace, defaults |
| Public constants | constants | exact exported constant values |

Reverse review found no private assertion requiring an unlisted external service,
filesystem fixture, callback, or candidate-controlled source path. The six
upstream Node 24 compatibility failures are recorded in `test-inventory.json`
and are not represented as hidden passing leaves.
