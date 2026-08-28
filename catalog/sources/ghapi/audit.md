# ghapi authoring audit

## Frozen source

- Upstream: `https://github.com/fastai/ghapi`
- Revision: `7acab1fa0571968aff2bf6508a6f51c5334d7584`
- Source archive: `git archive --format=tar HEAD`, SHA-256
  `sha256:9f823d7704bf929b3afb8f772399dce2b240521bb7570b34c6c8bb893d0b2bf2`
- License: Apache-2.0; the frozen `LICENSE` bytes are retained in the local
  authoring checkout and are hash-recorded in provenance evidence.
- Package version: `2.1.3`.

## Inventory and adaptation

The upstream checkout contains generated REST/OpenAPI modules and no tracked
pytest suite. Network, OAuth, Git, archive, and generated endpoint behavior is
therefore excluded from the scored task. The selected helper contract is
deterministic and local: date conversion, dependency graph planning, RFC 5988
link parsing, pagination control flow, and issue-template formatting.

## Runtime and dependency closure

The candidate is built on CPython 3.12.14 / Debian 12 amd64 with the exact
hash-locked requirements file under `provenance/requirements.lock.txt`.
Candidate and verifier execution are network-isolated; dependencies are
installed only during image build.

## Verifier boundary

The private verifier uses `custom-json-v1`. Each scenario is executed in a
UID-isolated child process with the candidate installed under
`/tmp/candidate-site`; the trusted verifier never imports candidate code into
its own interpreter. The private bundle and Oracle bundle are CAS-addressed in
the task-local authoring evidence.

## Traceability

| Contract area | Scenarios |
| --- | --- |
| package identity and exports | package-and-exports |
| date parsing/formatting | date-format, date-parse |
| PEP 508 key and graph planning | dependency-key, local-graph, closure, dependency-order, dependents |
| RFC 5988 parsing | link-header, link-header-quoted |
| async/sync pagination | async-paged, async-pages, sync-paged |
| issue form rendering and errors | issue-body, issue-body-errors |
| containers/auth helper | ghrows-repr, scope-string |
| determinism | repeat-determinism |

No private assertion requires an external service or candidate-controlled
trusted report.
