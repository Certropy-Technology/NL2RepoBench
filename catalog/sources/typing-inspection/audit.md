# Authoring Audit

- Frozen upstream: `pydantic/typing-inspection` at full commit
  `83d4dbb74fc367db4403c76be8c0f83cd4b63fbe`, tagged `v0.4.4`.
- Source archive SHA-256: `ae6f6606c1f75628cae5254817e4448da25225123f70ae06ae7e406d6db7418b`.
- License: MIT; the exact 1,090-byte license is preserved under `source/LICENSE`.
- Source behavior: pure Python, no CLI, filesystem, subprocess, network, native,
  random, locale, clock, callback, or external-service boundary.
- Upstream source collection: 94 tests; all 94 passed on Python 3.12.11.
- Hidden contract: 32 deterministic JSON leaves executed through the candidate
  UID subprocess boundary. Trusted verifier code never imports the candidate.
- Dependency closure: eight exact packages with 16 SHA-256 hashes, installed at
  image build time. Candidate and verifier phases run without network.
- Oracle: trusted-only bundle fetches the exact commit from the declared
  upstream, asserts `FETCH_HEAD`, and verifies the unprefixed Git archive digest.
- Model Agent run: intentionally not started in this authoring lane.

The public instruction documents every tested API family and boundary without
copying implementation bodies or private expected-value tables.
