# `es-to-primitive` traceability

Frozen source revision: `f33dccb3a8950f4abc67f43bec81f776da9cdf13`
(`v1.3.4`). The upstream project has four Tape files and 400 assertions. The
production verifier removes fixture repetition while preserving every public
behavioral branch in a fixed 33-leaf separate-process contract.

| Leaf range | Public contract | Frozen source/test basis |
| --- | --- | --- |
| 1-2 | package identity, CommonJS entry, declarations, function name/length, non-enumerable root aliases | `package.json`, `index.js`, four `.d.ts` files, `test/index.js` |
| 3-11 | all primitive categories are returned unchanged, including NaN, negative zero, BigInt, and Symbol | `helpers/isPrimitive.js`, primitive loops in `test/es2015.js` |
| 12-14 | arrays use ordinary string fallback for default, String, and Number hints | array assertions in `test/es2015.js` |
| 15-17 | Date default/String use string order; Number uses numeric order | Date assertions in `test/es2015.js` |
| 18-24 | ordinary method order, first-primitive return, fallback, non-callable skip, exact failure | `OrdinaryToPrimitive` and object/exception assertions in `test/es2015.js` |
| 25-31 | Symbol.toPrimitive hint strings, null fallback, non-callable rejection, primitive-result requirement, exception propagation | nested Symbol.toPrimitive assertions in `test/es2015.js` |
| 32 | boxed Symbol converts to the primitive Symbol in ES2015 | Symbols section in `test/es2015.js` |
| 33 | ES5 String order and ES6/ES2015 aliases | `test/es5.js`, `test/es6.js`, `test/index.js` |

Every production leaf maps to text in `instruction.md`. The verifier does not
test private helper module names, implementation source text, lint rules,
coverage thresholds, changelog content, publication scripts, or network access.
