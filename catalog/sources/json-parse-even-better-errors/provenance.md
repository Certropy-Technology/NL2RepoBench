# Source Freeze

- Upstream: `https://github.com/npm/json-parse-even-better-errors`
- Revision: `098b8d00e72e4807adba733c2cdde686b2b9bf82`
- Commit date: `2026-06-18T08:48:16-07:00`
- License: MIT, `LICENSE.md` SHA-256 `50627796eb4236cd05674e71d090e594447995225b7d94cd59e57c25fa3a0217`
- Reproducible archive command: `git archive --format=tar 098b8d00e72e4807adba733c2cdde686b2b9bf82`
- Archive size: `112640` bytes
- Archive SHA-256: `sha256:6bcf80e775ad5481a30fc401ede155fc49ebc44ae03a2f76f323430ce28c5f9f`
- Independent collection: `node --test --test-reporter=tap './test/**/*.js'` collected 60 leaf tests and exited 0.

The task is a bounded JSON-safe adaptation of the upstream CommonJS API. The
adapter preserves success values, formatting symbols, reviver behavior, and
error metadata while excluding non-serializable callback objects and direct
candidate imports from the trusted verifier process.
