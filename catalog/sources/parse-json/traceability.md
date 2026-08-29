# Specification Traceability

| Published contract | Private behavior group | Coverage |
| --- | --- | --- |
| ESM package identity and exports | package identity | package name/version, type, root runtime/type entries, default and named exports |
| JSON parsing | successful values | objects, arrays, primitives, whitespace, nested values, repeated calls |
| overloads | filename overload | second-argument filename and explicit filename metadata |
| JSONError contract | errors and cause | class identity, native cause, error name, message suffixes, empty input, unexpected token code point |
| source location | code frames | raw frame, line/column, UTF-16 positions, CRLF and no-location cases |
| JSON.parse compatibility | fixed reviver | deterministic numeric and root transformations created in the child |

The adapter never accepts executable model input. No private assertion requires
filesystem access, a CLI, terminal state, network access, or a non-JSON value.
