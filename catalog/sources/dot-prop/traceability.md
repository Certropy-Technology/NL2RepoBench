# dot-prop traceability

| Public contract area | Inventory source | Private leaves |
| --- | --- | --- |
| Package exports and ESM entry point | `api-inventory.json` | `exports all documented runtime functions` |
| `getProperty` defaults, falsy values, escaped/bracket/dot paths | `instruction.md` API Usage Guide | leaves 2–7 |
| `setProperty` mutation, array creation, primitive replacement, security | `instruction.md` API Usage Guide | leaves 8–11, 24 |
| `deleteProperty` and `hasProperty` semantics | `instruction.md` API Usage Guide | leaves 12–15, 35 |
| `escapePath`, `parsePath`, malformed indexes | `instruction.md` API Usage Guide | leaves 16–20 |
| `stringifyPath`, numeric rules, validation | `instruction.md` API Usage Guide | leaves 21–25 |
| `deepKeys` ordering, empty containers, sparse/cyclic/function graphs | `instruction.md` API Usage Guide | leaves 26–30 |
| `unflatten`, escaping, conflicts, prototype filtering | `instruction.md` API Usage Guide | leaves 31–34 |
| Parse/stringify round trip | `instruction.md` API Usage Guide | leaf 36 |

The 36 leaves are collected automatically from one private `node:test` file.
The denominator is frozen from the successful Oracle report: collected 36,
passed 36, collection errors 0. The upstream AVA test blocks and type tests
were used only for inventory and boundary selection; they are not the scored
test source.
