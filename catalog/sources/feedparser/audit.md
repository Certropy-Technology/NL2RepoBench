# feedparser candidate audit

Status: `blocked` / audit-only. No task manifest, Harbor bundle, hidden tests,
Oracle artifact, or dependency cache is included.

## Source candidate

- Repository: `https://github.com/kurtmckee/feedparser`
- Candidate revision: `a22c5521cbb109871f1a2318948581901bd47e26`
- License: BSD-2-Clause, pending detached archive/license byte hashing.
- Discovery evidence describes a large local pytest and fixture corpus and a
  Python 3.10--3.15 tox matrix. Exact source-only LOC, archive digest and final
  collection are not frozen here.

## Proposed deterministic boundary

Restrict the first task to parsing local bytes, strings and file-like values:

- Atom/RSS/RDF/JSON feed parsing;
- namespaces, encodings, dates, sanitization and relative links;
- normalized JSON output and error/status fields.

Do not permit real URL fetching, DNS, external HTTP, mutable network metadata or
secret-like feed contents. URL behavior must use local fixtures or a reviewed
loopback mock inside the verifier.

## Risks and blockers

- `feedparser-sgmllib`, `requests`, optional `chardet` and test tooling need a
  hash-locked offline closure;
- the fixture corpus requires provenance/license review before it can become a
  private test artifact;
- test collection must be repeated in the final immutable image and its leaf IDs
  frozen; the discovery count is not a denominator;
- candidate subprocess adapter and separate verifier do not exist yet;
- Oracle x3, empty/stub/forgery/hang/offline controls and blind review are absent.

This record remains a candidate audit until all blockers are independently
verified. It must not be counted as a published Harbor task.
