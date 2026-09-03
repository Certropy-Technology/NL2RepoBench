# msgspec Traceability

| Frozen leaves | Public instruction contract |
| --- | --- |
| `exports`, `version`, `repr-determinism` | Supports; Implementation Notes; public imports |
| `struct-basics`, `struct-options`, `field-metadata`, `defstruct`, `frozen-mutation`, `unknown-field`, `missing-field` | `Struct`, `StructMeta`, `field`, `defstruct` |
| `raw`, `meta`, `strict-type` | `Raw`, `Meta`, conversion/error contract |
| `to-builtins`, `convert-valid`, `convert-invalid`, `struct-helpers` | Builtin conversion helpers and `msgspec.structs` |
| `json-encode`, `json-decode`, `json-typed-struct`, `json-deterministic`, `json-encoder`, `json-decoder-lines`, `json-format`, `json-schema`, `json-components`, `json-hook`, `json-invalid`, `buffer-input` | `msgspec.json` |
| `msgpack-roundtrip`, `msgpack-typed-struct`, `msgpack-ext`, `msgpack-deterministic`, `msgpack-hook`, `msgpack-invalid` | `msgspec.msgpack` |
| `toml-roundtrip`, `yaml-roundtrip` | `msgspec.toml` and `msgspec.yaml` |

The private verifier only observes JSON-safe projections from fresh candidate child processes. It does not import candidate modules in the trusted verifier process, and no leaf relies on an undeclared service, current time, random seed, or developer path.
