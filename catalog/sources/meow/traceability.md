# Meow Specification Traceability

| Published contract | Private behavior group |
| --- | --- |
| ESM root callable and package metadata | package shape and inventory |
| Positional values and input type conversion | input conversion |
| String, boolean, number, negation, defaults | typed flags |
| Short flags, aliases, camel-case keys, repeated values | flag aliases and normalization |
| Choices and invalid option boundaries | validation |
| `commands` and pass-through arguments | command handling |
| `description`, help trimming, indentation, version | help and metadata |
| JSON-safe result fields | result projection |

Reverse review: every private scenario maps to a published behavior above. Excluded process-exit and callback behavior is explicitly named in the instruction and has no hidden leaf.
