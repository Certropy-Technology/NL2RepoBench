# Traceability

| Public contract area | Private leaf coverage |
| --- | --- |
| Root ESM default export and TypeScript declaration | `package metadata and default ESM export are available` |
| Non-Windows `TERM=linux` exception | `non-Windows linux console marker is unsupported` |
| Non-Windows ordinary, missing, and empty TERM behavior | `non-Windows ordinary TERM values are supported`, `non-Windows missing and empty TERM are supported` |
| Windows default behavior | `Windows without a supported marker is unsupported` |
| Windows `WT_SESSION` and `TERMINUS_SUBLIME` | `Windows Terminal session marker is supported`, `Terminus Sublime legacy session marker is supported` |
| Windows exact terminal-program values | `Windows terminal program markers are supported`, `Windows terminal program matching is case sensitive` |
| Windows exact TERM values | `Windows TERM markers are supported`, `Windows TERM markers require exact values` |
| Windows exact ConEmu and JetBrains values | `Windows ConEmu Cmder marker is supported`, `Windows JetBrains terminal marker is supported` |
| Empty/nonmatching Windows markers | `empty Windows markers are unsupported`, `unrecognized Windows markers are unsupported` |
| Per-call state observation and boolean return | `environment changes are observed on the next call`, `platform changes are observed on the next call`, `each supported marker returns a primitive boolean`, `arguments do not change the result`, `Windows marker alternatives remain independent` |

The verifier uses a task-specific child-side adapter because `process.platform`
and `process.env` are process-global, non-JSON state. The trusted test process
never imports the candidate package: it serializes the requested state to a
candidate-owned Node child process, which loads the root export and returns a
bounded JSON response.
