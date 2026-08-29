# LangChain task traceability

The private verifier is organized into stable leaf groups mapped to the public instruction:

| Leaf prefix | Public contract | Adapter boundary |
| --- | --- | --- |
| `import-` | Required modules and re-exports | Candidate child imports and reports names |
| `structured-` | Schema classification, union/`oneOf` flattening, tool binding, provider kwargs, message parsing, and errors | Pydantic/dataclass/`TypedDict` objects are normalized to JSON |
| `pii-` | Built-in detectors, offsets, strategies, custom detectors, sync/async message hooks, and error context | Core message objects are serialized after candidate hooks |
| `model-limit-` | Constructor validation, count updates, end/error behavior, and async parity | Middleware state/result dictionaries are normalized in the child |
| `tool-limit-` | Constructor validation, filtering, count semantics, continue/end/error behavior, parallel calls, and async parity | Tool calls and returned message objects are normalized in the child |

The trusted verifier never imports candidate code. It copies a generic operation adapter into a UID-10001 subprocess, supplies operations over JSON, and converts only returned JSON into verifier-owned leaves, collection, JUnit, grading, and reward files. Provider calls, graph execution, shell middleware, and network behavior are excluded from both the instruction and hidden assertions.
