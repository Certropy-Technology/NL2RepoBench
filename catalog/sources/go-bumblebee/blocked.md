# `go-bumblebee` authoring audit: blocked

**Status: blocked.** This source-local record freezes and audits the exact
upstream revision. It is not a Harbor task. No `catalog/tasks/go-bumblebee/`
runtime, private test bundle, Oracle bundle, dependency cache, or shared index
is created by this lane.

## Frozen source

- Upstream: `https://github.com/perplexityai/bumblebee`
- Exact revision: `d76e369a0b34d6506dc249b4d573f7859cac7a19`
- Revision assertion: passed after a detached checkout.
- Git archive SHA-256: `b6f1583784c46dd8469829bcff5cd4b9b284c484272ee4e2d66930ad6ce74c7e`
- License: Apache-2.0
- `LICENSE` SHA-256: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`
- Module path: `github.com/perplexityai/bumblebee`.
- Module directive: `go 1.25`.
- Frozen checkout: 30 implementation Go files, 28 Go test files, 58 Go files
  total, and 15,501 physical Go lines.

## Upstream test and dependency result

The exact checkout was tested with the locked local toolchain:

```text
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off \
  GOSUMDB=off GOTOOLCHAIN=local go test -json ./...
```

Go `go1.26.5-X:nodwarf5 linux/amd64` collected 231 test leaves across 23
packages: 227 passed and 4 skipped, with no failed leaves. The repository has
no third-party module requirements and the no-network build probe succeeds.
This is source evidence only; it is not a production verifier receipt.

## Public behavior and adapter assessment

The package is a read-only endpoint inventory command rather than a portable
library. Its user-facing commands are:

- `bumblebee scan`: walks explicit or profile-derived filesystem roots,
  parses npm/pnpm/Yarn/Bun, PyPI, Go modules, RubyGems, Composer, MCP,
  editor-extension, browser-extension, Homebrew, and agent-skill metadata,
  optionally matches an exposure catalog, and emits package/finding/summary
  NDJSON records.
- `bumblebee roots`: resolves host-dependent baseline/project/deep roots.
- `bumblebee selftest`: extracts embedded fixtures and scans them in a
  temporary directory.
- `bumblebee version`: reports build/VCS/runtime metadata.

The scanner reads arbitrary filesystem trees and derives endpoint hostname,
OS, architecture, username, UID, and optional environment-provided device ID.
Run IDs are random and scan records contain current UTC timestamps. The HTTP
sink can make authenticated HTTPS requests, batch and gzip records, and retry
or report non-2xx responses. Root resolution and Homebrew/browser paths are
platform-specific; scanner cancellation uses OS signals. The embedded
self-test uses `embed.FS` and temporary filesystem extraction.

The current Go production profile requires a separate verifier and a bounded
child-side typed bridge. A faithful bridge for this revision would need a
reviewed virtual filesystem/root resolver, deterministic endpoint and clock
injection, embedded-fixture support, all ten ecosystem/config parsers, and a
network-sink test double that does not alter the public CLI contract. The
upstream tests exercise these behaviors through in-process internal packages
and host fixtures; they do not define such a child-side protocol. Invoking the
candidate directly from trusted tests would violate the verifier boundary.

Consequently, narrowing the task to one parser or replacing endpoint/time/
network behavior would no longer be a faithful task for this frozen project.
The task is blocked pending an approved task-specific CLI/host-fixture adapter.

## Remediation

1. Approve a deterministic child-side CLI adapter with virtual roots,
   endpoint/time/run-ID controls, fixture extraction, and a local HTTP sink
   test double, or explicitly exclude this candidate from the production set.
2. If approved, add public-contract tests for every supported scan profile,
   ecosystem filter, findings-only mode, roots resolution, self-test, output
   sink, and malformed-input/error behavior.
3. Freeze the adapter protocol and collection denominator, then compile the
   task, run one Oracle, and run empty/stub/forgery/offline controls against
   the final compiled manifest.

Until that remediation exists, no runtime or Oracle/control result is claimed.
