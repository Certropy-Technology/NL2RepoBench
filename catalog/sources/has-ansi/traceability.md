# has-ansi Traceability

The public instruction sections map to the private collection as follows:

| Contract area | Leaf IDs | Evidence basis |
| --- | --- | --- |
| package name/version, ESM root export, declaration | `has-ansi.test.mjs:package metadata and runtime export`, `has-ansi.test.mjs:package includes the typed default declaration` | frozen `package.json` and `index.d.ts` contract |
| empty, ordinary, whitespace, Unicode, literal, lone and non-control escapes | `empty string is not ANSI` through `escape plus ordinary character is not ANSI` | default function and accepted ANSI grammar |
| SGR, reset, cursor, OSC, C1, parameter and private CSI sequences | `SGR color sequence is ANSI` through `private CSI parameter is detected` | `ansi-regex` 6.3.0 behavior under the frozen lock |
| position, multiline, repeated and intermediate sequences | `embedded sequence is detected` through `control sequence with intermediate byte is detected` | public function position-independence and multiline behavior |
| non-ANSI control boundary | `DEL alone is not ANSI` | accepted ANSI grammar excludes DEL by itself |
| fixed denominator and subprocess isolation | all 24 leaves | child-side JSONL adapter, `node-test-leaf-pass-rate-v1`, expected total 24 |

The upstream two-leaf AVA behavior baseline is represented by the ordinary
positive/negative cases. Additional cases are deterministic public edge cases,
not copied upstream assertions. The verifier owns collection, reports, reward,
timeouts, workspace copy, and network receipts; candidate-written report or
reward files are not read as grading inputs.
