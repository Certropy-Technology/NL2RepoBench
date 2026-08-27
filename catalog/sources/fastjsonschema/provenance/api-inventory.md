# Public API Inventory

Frozen revision `b88fa37cd46bb81e8d9dce91a7e1bc4debedd3a2` declares this package-root
public surface through `fastjsonschema.__all__`:

| Name | Kind | Public contract scope |
| --- | --- | --- |
| `VERSION` | `str` constant | Package version string. |
| `JsonSchemaException` | exception class | Base public schema exception; derives from `ValueError`. |
| `JsonSchemaValueException` | exception class | One value-validation failure. |
| `JsonSchemaValuesException` | exception class | Aggregated value-validation failures. |
| `JsonSchemaDefinitionException` | exception class | Invalid or unresolvable schema definition. |
| `validate` | function | Validate one JSON value and return it, with optional defaults. |
| `compile` | function | Build a reusable validator callable. |
| `compile_to_code` | function | Return Python source defining an equivalent validator. |

The three function signatures and their common keyword arguments are stated in
`instruction.md`. Internal code generators, reference resolver helpers, CLI
implementation details, and arbitrary Python callback transport are not part
of this benchmark's explicit JSON-safe public boundary.
