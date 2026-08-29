# Contract Traceability

This record maps every frozen verifier leaf to behavior stated in
`instruction.md`. It intentionally records public behavior categories rather
than private fixtures or assertions. The frozen denominator is 24.

| Leaf | Public contract |
| --- | --- |
| production-element | Production `jsx` selection, primitive text preservation, and runtime callback shape |
| static-root | Root `Fragment`, `jsxs` selection for multiple children, and deterministic per-name keys |
| root-text | Fragment wrapping for a root text result |
| development-runtime | `jsxDEV` callback arguments, source metadata, and static-child flag |
| require-fragment | Required `Fragment` error contract |
| require-jsx | Required production `jsx` error contract |
| require-jsxs | Required production `jsxs` error contract |
| require-jsxdev | Required development `jsxDEV` error contract |
| html-properties | React property names, boolean values, and omitted nullish/`NaN` values |
| token-properties | Space-separated and comma-separated property serialization |
| dom-style | Style parsing with DOM-cased property names |
| invalid-style | `VFileMessage` failure and `ignoreInvalidStyle` behavior |
| svg-properties | SVG property schema selection and nested schema switching |
| table-whitespace | Whitespace-only child filtering for table-family elements |
| omit-keys | `passKeys: false` behavior |
| component-node | Component replacement with `passNode: true` |
| component-basic | Component replacement without a node prop |
| mdx-literal | MDX JSX literal attribute handling |
| mdx-expression | Expression delegation through `evaluateExpression` |
| mdx-program | ESM delegation through `evaluateProgram` |
| mdx-member | Dynamic member component evaluation |
| table-align-css | Table-cell alignment conversion and CSS-cased style names |
| html-casing-align | HTML attribute casing and disabled table alignment conversion |
| development-position | One-based line and zero-based column metadata |

The reverse mapping is also complete for the scored surface: every behavior
promised under `API Usage Guide` and `Implementation Notes` is represented by
at least one row above. Packaging, ESM exports, offline installation, process
isolation, report ownership, and network denial are enforced by the verifier
wrapper and controls rather than counted as additional functional leaves.
