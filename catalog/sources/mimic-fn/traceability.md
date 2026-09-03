# Contract Traceability

| Contract area | Public instruction | Private leaves |
| --- | --- | --- |
| Package identity, ESM root export, types entry | Supports | `package` |
| Return exact destination and copy name/properties/symbols | `mimicFunction` | `return-value`, `copy-name`, `copy-property`, `copy-symbol` |
| Preserve length/prototype, copy descriptors/inheritance/classes | `mimicFunction` | `keep-length`, `descriptors`, `inherited`, `keep-prototype`, `classes` |
| Wrapped source text and method properties | Wrapped `toString()` | `to-string*`, `native-to-string`, `string-coercion`, `to-string-name`, `patched-source-to-string` |
| Non-configurable conflict policy | `options.ignoreNonConfigurable` | `nonconfig-*` |

The private adapter constructs all functions, symbols, descriptors and errors in
the candidate child. The trusted process only sends an operation identifier and
checks JSON observations plus the fixed `node:test` leaf collection.
