# Camelcase Keys Traceability

| Public contract | Private behavior group | Frozen leaves | Coverage |
| --- | --- | ---: | --- |
| package identity and ESM export | package shape | 1 | name/version/type/export map/default callable; install and pack are verifier setup gates |
| ordinary key conversion | basic conversion | 5 | separators, insertion order, numeric-looking keys, digit boundaries, `_`/`$` prefixes |
| input and value handling | JSON values | 3 | primitives, falsy nested values, empty objects and arrays |
| top-level arrays | arrays | 2 | object elements converted and primitive elements preserved |
| shallow versus deep behavior | deep recursion | 4 | default shallow behavior, nested objects, object elements, nested arrays |
| conversion options | options | 8 | pascalCase, uppercase preservation, string exclude, stopPaths, option composition |
| repeatability | determinism | 1 | equivalent repeated calls return equivalent JSON |

The 24 rows above are the complete frozen denominator. The verifier calls only
the default export through a UID-separated JSON child process. No private
assertion requires a network service, mutable clock, filesystem path, callback,
regular expression transport, symbol, built-in instance, cyclic graph, or
candidate-controlled report. Those non-JSON public surfaces are inventoried but
are not claimed as scored parity with all 22 upstream AVA tests.
