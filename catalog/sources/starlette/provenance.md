# Starlette provenance

- Authoring mode: `author-one`.
- Candidate checkout: `.nl2repo/authoring-work/python-author-wave2-20260828/starlette-upstream`.
- Frozen revision: `d9ed5b0f98fdf081fb138473129b72eb035153a3` (`refs/heads/main` at freeze time).
- Source archive: no-prefix `git archive`, SHA-256 `sha256:044f15d81b61b252cca22d4ea0893626dbbbbe56f3400090b304c083cfe71bb5`.
- License: BSD-3-Clause; `LICENSE.md` bytes are hash-recorded in `evidence/source-freeze.json`.
- Runtime: CPython 3.12.14, Debian 12 amd64, digest-pinned `python:3.12-slim-bookworm`.
- Candidate closure: AnyIO, hatchling and build transitive dependencies in `provenance/requirements.lock.txt`; all entries are exact pins with SHA-256 hashes.
- The candidate and verifier build phases install from the private hash lock. Agent and verifier execution are no-network.
- Oracle bundle contains `solve.sh` and the frozen source archive; `solve.sh` verifies archive bytes before extraction. It receives no model-agent authorization.
- Large checkout, CAS artifacts, Docker contexts, and replay logs remain under `.nl2repo/authoring-work`; no private tests or reference source are in the public instruction.
