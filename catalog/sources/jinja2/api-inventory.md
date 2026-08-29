# Jinja2 API Inventory

## Public modules

The frozen package contains `async_utils`, `bccache`, `compiler`, `constants`,
`debug`, `defaults`, `environment`, `exceptions`, `ext`, `filters`,
`idtracking`, `lexer`, `loaders`, `meta`, `nativetypes`, `nodes`, `optimizer`,
`parser`, `runtime`, `sandbox`, `tests`, `utils`, and `visitor`, plus the
`py.typed` marker. The root package re-exports 35 documented classes,
functions, sentinels, and exception types.

## Behavioral groups

| Group | Frozen source modules | Adapter coverage |
| --- | --- | --- |
| Environment/template lifecycle | environment, runtime | construction, caching, globals, render/generate/stream |
| Language core | lexer, parser, compiler, nodes, filters | expressions, statements, loops, macros, inheritance, escaping |
| Loaders/cache | loaders, bccache | dict/function/filesystem/prefix/choice and bytecode APIs |
| Async/native | async_utils, nativetypes | async render and native scalar preservation |
| Safety/errors | sandbox, exceptions, debug | strict/chainable undefined and unsafe attribute/call rejection |
| Extensions/analysis | ext, meta, utils | extension registration, autoescape, undeclared/reference analysis |

All hidden leaves call the candidate only through a child-side JSON adapter.
Rich Template/Environment objects never cross the trusted verifier boundary.
