# Public Contract Traceability

This record maps the frozen private verifier categories to commitments in the
public instruction. It intentionally describes behavior classes, not hidden
inputs or assertion text.

| Public commitment | Private coverage | Boundary |
| --- | --- | --- |
| `validate`, `compile`, and `compile_to_code` accept JSON-compatible schemas and values | Draft 04, 06, 07, and 2019-09 JSON Schema compatibility cases plus a package-root API surface scenario | JSONL request to unprivileged candidate child |
| Valid values are returned; invalid values raise a public schema exception | Valid and invalid cases for scalar, array, object, composition, numeric, string, and boolean constraints | The trusted parent only observes normalized pass/fail JSON |
| Draft is selected by `$schema` | Per-draft frozen suite groups | Request includes a public draft URI, no network fetch |
| Object defaults and required fields have observable semantics | Dedicated default and required scenarios | Trusted parent compares the returned JSON value after candidate execution |
| Static reference resolution has no unrestricted network behavior | Materialized local reference fixtures and allowlisted handler recipes | Candidate child resolves only verifier-provided URI content |
| Generated code provides the same validation behavior | Valid and invalid generated-code scenarios | Candidate child compiles and invokes its generated `validate` function |
| Named callback recipes are reconstructible across JSON | Identifier-format scenario | Only `is_identifier` and `is_ascii` recipes are accepted |
| Error behavior is deterministic and public | Invalid cases require a `JsonSchemaException` subclass rather than a process crash | Exact private error text is not scored |
| Root exports include `VERSION`, three callables, and the four public exception classes | Dedicated package-root metadata scenario | Candidate child returns normalized type/hierarchy facts; trusted parent asserts them |

The frozen denominator is 2,899 unique report IDs: 2,891 compatibility cases
and eight API-focused scenarios. Some upstream descriptions repeat; the trusted
verifier appends an occurrence suffix before writing its collection and JUnit
files so the metric denominator remains unique and stable.
