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

## Remediation record (2026-08-25)

A declarative blocked descriptor was added after reviewing the candidate audit.
The immutable revision and declared BSD-2-Clause license are recorded as
provisional provenance, but the audit did not contain a detached Git archive
hash or license-byte hash. The remediation therefore does not promote
`source.status` to `known` and does not claim source-freeze completion.

The dependency names are observations from the audit, not an approved lock:
`feedparser-sgmllib`, `requests`, and optional `chardet`. No private test
bundle, child-side verifier, Oracle source bundle, or Harbor runtime exists.
The runtime directory `catalog/tasks/feedparser/` is intentionally absent.

The executed remediation commands and outcomes are recorded in
`evidence/remediation.log`; no Oracle, control, or source archive command was
represented as successful. The sole blocker is `environment`, because the
reproducible image/dependency/verifier closure is not available. Reopen by
freezing the detached source archive and license bytes, then materializing the
hash-locked build closure, separate verifier, Oracle bundle, and controls.
