# minimist instruction revalidation blocker

- Task: `minimist` 2.0.0
- Queue/source digest: `sha256:d22b27805558ef1cb4a9924944e71d0acd547f320862f5e468594dc9fc4dbfb4`
- Frozen revision: `ecfdaea23e7931c0d529c52b743c711c3278a8ce`
- Frozen source digest: `sha256:880c54feb7058c36a6600d35d58a17d834d403b4460cb9c62c33cb455c8adc3c`
- Classification: `artifact/verifier`; lifecycle and historical production evidence unchanged.

`uv run nl2repo task validate-source catalog/sources/minimist` passed and matched the
queue digest. All four declared private CAS objects were checked offline by exact size
and SHA-256; see `artifact-check.json`. The exact Oracle bundle was inspected without
execution; it contains only `solve.sh`, no source archive, and performs a runtime
`git fetch` from GitHub at the frozen revision. This violates the required NoNetwork
contract, so no compile, Oracle, control, or receipt result is claimed. Payload details
are in `oracle-payload.json`.

Next step: recover or register a provenance-equivalent source archive and an Oracle
bundle that verifies it without network access, then compile twice and run fresh
Oracle plus supported controls. Do not reuse historical receipts or change the
denominator, lifecycle, generated projection, or production evidence for this blocker.
