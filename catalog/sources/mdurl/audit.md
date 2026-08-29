# mdurl authoring audit

- Frozen upstream: `https://github.com/executablebooks/mdurl` at commit
  `524d2edbbcb8bb48301ba716c7482827bcabb281`.
- License: MIT; the frozen `LICENSE` is 2,338 bytes with SHA-256
  `7c605df6e28667a9603118e98274f64a49ce3eed0d26fccce9534a345e0ef955`.
- Unprefixed `git archive --format=tar HEAD` is 81,920 bytes with SHA-256
  `f0caa116deb9e08c885a2ae9df766a05b9a4974ea684d298fbaed0f2d0884595`.
- Runtime is pure Python with no third-party runtime dependencies. The source
  uses Flit Core `>=3.2,<4`; the task pins `flit_core==3.12.0` in a hash lock.
- Frozen upstream collection under CPython 3.12.11: 189 leaves, all passed.
  The private verifier adds ten API/edge leaves, preserving all 88 parse and
  88 format fixture leaves plus the decode and encode behavior leaves.
- The verifier imports candidate code only in the unprivileged candidate child
  process. The trusted process owns the expected values, fixed denominator,
  JUnit, collection, and reward.
- Agent and verifier execution are `no-network`; only the trusted Oracle
  solution receives a run-scoped authorization for `github.com`.
