# CSS Tree Specification Traceability

| Public contract | Private behavior group | Leaves |
| --- | --- | ---: |
| Package identity and named exports | package-shape | 2 |
| Stylesheet, value, selector, declaration parsing and generation | parse-generate | 8 |
| CSS token boundaries and token names | tokenizer | 4 |
| Plain-object round trip, clone, walk, find and findAll | ast-conversion-and-walk | 6 |
| Definition-syntax parse and generate | definition-syntax | 4 |
| Property lexer success, failure and match metadata | lexer | 3 |
| CSS string, identifier and URL escaping | css-escape-utilities | 5 |
| **Total frozen denominator** | **node:test** | **32** |

Reverse review rule: every private leaf must use only the import paths and
input domains documented in `instruction.md`. No leaf may depend on a network,
filesystem fixture, clock, random value, TTY, upstream source path, candidate
written report, or undocumented private module.
