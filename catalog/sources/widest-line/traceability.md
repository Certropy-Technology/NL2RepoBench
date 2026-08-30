# Widest-line Traceability

| Public specification area | Private leaves | Upstream behavior family |
| --- | --- | --- |
| default export and ordinary strings | `ascii`, `multiline`, `long-line`, `repeated-call`, `tied-lines` | `widestLine('a')`, `widestLine('a\\nbe')` |
| line-feed splitting and empty lines | `empty`, `trailing-newline`, `blank-lines`, `newline-only`, `multiple-separators` | `string.split('\\n')` and max reduction |
| Unicode terminal width | `cjk`, `emoji`, `combining`, `zwj-emoji`, `regional-flag`, `fullwidth`, `ambiguous` | `string-width` default width |
| ANSI and controls | `ansi`, `ansi-around-wide`, `controls`, `tab`, `carriage-return`, `osc-link` | `string-width` stripping and zero-width controls |
| input/error contract | `number-input`, `object-input`, `undefined-input`, `null-input` | JavaScript string method type error |

The adapter never imports the candidate in the trusted test process. Each leaf
invokes the candidate default export through the generic Node subprocess
boundary and compares a bounded JSON result. Package metadata, lockfile
integrity, lifecycle-script rejection, and network isolation are checked by the
compiled verifier runtime rather than by candidate-controlled tests.
