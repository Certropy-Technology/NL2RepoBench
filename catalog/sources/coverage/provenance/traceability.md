# Contract Traceability

| Contract area | Verifier leaf IDs | Instruction section |
| --- | --- | --- |
| Tracing and branch collection | `basic-measurement`, `branch-measurement` | `Coverage` |
| SQLite line/arc/context storage | `data-roundtrip`, `data-arcs`, `contexts`, `combine-data` | `CoverageData` |
| Report generation | `reports` | `Coverage` |
| Lifecycle and configuration | `lifecycle`, `configuration` | `Coverage` |
| CLI entry points | `cli` | `Command line` |
| Exceptions and aliases | `errors` | `Root exports`, `CoverageData` |
| Plugin protocol | `plugin-protocol` | `Plugin protocol` |

The frozen denominator is 12 unique leaves. The verifier writes its own
collection and JUnit reports from the JSONL leaf result; candidate output,
candidate-written reward files, and candidate-written test reports are not
trusted.
