# portalocker authoring audit

- Mode: `author-one`; assigned discovery status: `needs-evidence`.
- Upstream: `https://github.com/wolph/portalocker` at
  `c86f80c2505de8e44fb9d2493eb94ab96201fef6`.
- Frozen commit tree: `5d1d209fea107a443ab3e6adf1424d35836123fa`.
- Source archive: SHA-256 `b38150745012d3fa9086c1df4a4ac6a2c633914796ec8bc5509bd651f1c6ccac`.
- License: BSD-3-Clause; `LICENSE` SHA-256
  `a50570fa3b3102a42d7babb0569238b0b3c0aedce0063c8e4d65060dfd3f7293`.
- Runtime closure: pure Python on Linux/POSIX; Redis and Windows extras are
  excluded because they require external services or platform-specific APIs.
- NoNetwork: candidate, verifier, Oracle, controls and Agent are network
  isolated. Only pre-freeze authoring accessed the immutable upstream source.
- Verifier boundary: trusted run.py launches an unprivileged candidate adapter;
  candidate output is bounded JSON and trusted grading is generated separately.
- Fixed denominator: 32 scenario leaves, collected automatically by the
  custom-json-v1 verifier.
- Remediation evidence: source, license, API, test and dependency probes are
  recorded in `evidence/` and the private handoff manifest outside this tree.
