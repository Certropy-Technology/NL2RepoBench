# Zod traceability

| Public behavior | Frozen upstream evidence | Private leaf coverage |
| --- | --- | ---: |
| Package metadata, named `z`, default alias, constructors | package exports and v4 classic index | 1 |
| String type, length, email, trim, lowercase | `string.test.ts`, `validations.test.ts`, `error.test.ts` | 7 |
| Number bounds, integer, positive/nonnegative | `number.test.ts`, `validations.test.ts` | 3 |
| Boolean type behavior | v4 classic primitive schema tests | 1 |
| Literal and enum membership/errors | `literal.test.ts`, `enum.test.ts` | 2 |
| Array item paths and length checks | `array.test.ts`, `error.test.ts` | 3 |
| Object strip/strict/loose and nested paths | `object.test.ts`, `error.test.ts` | 4 |
| Optional, nullable, and default wrappers | `optional.test.ts`, `nullable.test.ts`, `default.test.ts` | 2 |
| Union success and `invalid_union` failure | `union.test.ts`, `error.test.ts` | 1 |

Every private assertion maps to a behavior fully stated in `instruction.md`.
Every constructor, check, transformation, object policy, wrapper, result shape,
path rule, and exact message promised by the bounded instruction is exercised
by at least one leaf. Callback-valued APIs, async behavior, non-JSON values,
type inference, and unlisted constructors are explicitly outside the task.
