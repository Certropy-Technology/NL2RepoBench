# Public Contract Traceability

The task uses a fixed 45-leaf private verifier. The verifier imports candidate
code only in bounded UID 10001 child processes; the root-owned report writer
compares JSON observations and writes the final collection, JUnit, grading, and
reward artifacts.

| Public contract area | Instruction section | Deterministic coverage |
| --- | --- | --- |
| Distribution metadata, root exports, typed package | Supports; Root exports | install metadata, `__all__`, function module identity |
| `Config` defaults and cache controls | `Config`; Cache controls | fresh defaults, identity key conversion, size mutation and clear |
| Primitive construction and `Any` | `from_dict` | primitive dataclass and JSON-compatible arbitrary value |
| Nested dataclasses and collections | `from_dict` | nested object, list, mapping, set, fixed tuple, variadic tuple |
| Missing/default/non-init/frozen behavior | `from_dict` | default, fresh factory, optional omission, missing required, non-init, frozen default |
| Basic type checks | `from_dict` | wrong primitive, disabled checking, numeric/collection conversion paths |
| Hooks, casts, and key conversion | `Config` | exact type hook, nested hook, primitive cast, enum-base cast, outer tuple cast, camel-case key mapping |
| Union behavior | `from_dict`; `Config` | first match, dataclass match, no match, strict ambiguity, strict single match |
| Forward and richer typing forms | `from_dict`; `Config` | resolved/missing forward references, `NewType`, `Literal`, `Type`, `InitVar` |
| Generic dataclasses | `from_dict` | concrete generic target and nested generic dataclass field |
| Dataclass lifecycle | `from_dict` | frozen post-init derived field and inherited dataclass mechanics exercised by runtime construction |
| Public exceptions | Exceptions | hierarchy, field path, key set, union match set, stable message fragments |

The frozen upstream suite independently collected and passed 203 tests three
times. Those runs diagnose source/environment health; they are not copied into
the task and are not the production denominator.
