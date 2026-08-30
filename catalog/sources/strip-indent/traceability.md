# `strip-indent` traceability

Frozen source revision: `102b553f9efaec1c2451cd9ac2385269768f1fed`
(`4.1.1`).

| Leaf range | Public contract | Source/test basis |
| --- | --- | --- |
| 1-3 | package root exposes callable default and `dedent` exports with string results | package metadata and declarations |
| 4-9 | minimum common leading ASCII space/tab count is removed from non-empty content lines | upstream README, implementation contract, and `main` assertions |
| 10-13 | empty, unindented, blank, and whitespace-only inputs preserve the documented `stripIndent` behavior | upstream minimum-indent guard and blank-line assertions |
| 14-17 | LF/CRLF, trailing spaces, and Unicode content are preserved | string transformation contract and upstream boundary coverage |
| 18-25 | `dedent` trims all surrounding whitespace-only lines, then applies common indentation | upstream `dedent` assertions including CRLF and mixed line endings |
| 26-28 | internal empty/whitespace-only lines remain while outer boundaries are removed | upstream internal-empty assertions |
| 29-30 | both exports reject non-string JSON-compatible inputs with `TypeError` | declared string-only API and native string-method behavior |
| 31-32 | repeated and alternating calls are deterministic and stateless | synchronous pure utility contract |

The verifier tests only the documented package-root exports and JSON-compatible
inputs. It does not test private files, a CLI, callbacks, symbols, BigInt,
custom prototypes, locale, filesystem state, or network behavior.
