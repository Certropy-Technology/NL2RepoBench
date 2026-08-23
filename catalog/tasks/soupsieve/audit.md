# SoupSieve Candidate Audit

Status: **blocked / audit-only**

## Pin And Provenance

- Upstream: `https://github.com/facelessuser/soupsieve`
- Required commit: `4caaf89344dc9a9baaedb7f0ab04d45526e61293`
- Source checkout/archive: **not materialized in this checkout**.
- Archive SHA-256 and byte size: **not measured**.
- License file and SPDX conclusion: **not independently verified**; the
  catalog intentionally records `license_spdx = "unknown"`.
- Source-only LOC: **not measured**; count only tracked Python source under
  package roots, excluding tests, fixtures, docs, generated, vendored, blank,
  and comment-only lines.

The commit pin is copied from the task request. It is not evidence that the
object is reachable or that an archive is byte-identical. Add a source lock
only after a clean checkout or archive has been verified against the full
commit and recorded digest.

## Required Bounded Probes

Run these probes in a clean disposable directory and preserve concise output
as authoring evidence. Do not add the checkout, wheelhouse, pytest cache, or
command output to this task directory.

1. Fetch the full commit, verify `git rev-parse HEAD`, list submodules, create
   a deterministic archive, hash it, and inspect license files.
2. Measure source-only LOC with a deterministic file list and explicit
   exclusions; record Python version, package roots, files, and final count.
3. Install the frozen source with BeautifulSoup4 only, run pytest collection
   and the suite using `html.parser`, and record collected/skipped/errors/
   failures. Repeat collection and require a stable denominator.
4. Exercise `select`, `select_one`, `iselect`, `match`, `closest`, `filter`,
   `compile`, `escape`, and `purge` over small BeautifulSoup trees. Record
   that selector inputs are text and API outputs are BeautifulSoup objects,
   not JSON replacements.
5. Resolve the complete dependency closure offline and prove no install/test
   step reaches the network. `lxml` and `html5lib` must be absent. Record
   dependency hashes and lock/tool versions.
6. Inspect pytest fixtures, plugins, test data, environment variables, local
   files, network calls, and parser availability. External or non-stdlib
   fixtures require an adaptation record or keep the task blocked.

## Gate Matrix

| Gate | Evidence in this candidate | Result |
| --- | --- | --- |
| Exact source/archive | Not materialized | blocked |
| License | Not captured | blocked |
| Source-only LOC | Not measured | blocked |
| Pytest collection | Not run | blocked |
| Stdlib parser lane | Declared, not executed | blocked |
| CSS selector API | Contract drafted, no parity run | blocked |
| JSON/text boundary | Contract documented, no probe | blocked |
| Offline closure | No lock/install evidence | blocked |
| Fixture risks | Test tree unavailable | blocked |

## Publication Decision

Do not promote this task beyond `blocked` or assign a frozen denominator. This
directory contains only catalog metadata, an instruction draft, and this
audit. It contains no hidden tests, Harbor/private/shared assets, Oracle,
verifier, or large cache. Re-open the gates from a clean source materialization
and update metadata only after evidence is independently reproducible.
