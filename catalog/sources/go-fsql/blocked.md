# `go-fsql` Go authoring audit: blocked

**Status: blocked.** This is a source-local audit, not a published Harbor task.
It contains no generated `catalog/tasks/go-fsql` runtime, private Oracle,
controls, dependency cache, credentials, or shared-index changes.

## Project description

`fsql` is a command-line filesystem search tool with SQL-esque `SELECT`, `FROM`,
and `WHERE` syntax. It can select name, size, time, hash, and mode attributes;
walk multiple directories and glob patterns; exclude paths; apply formatting
modifiers; and run interactively through a terminal prompt.

## Frozen revision and test baseline

- Upstream: `https://github.com/kashav/fsql`
- Revision: `5cfe17e9b3c69aee6e65cc5d73b7c40cc1ffa87e`
- Git archive SHA-256: `52a1d205d660c7b3cec7e3e8d40502502f6425e7669de46b8ebf63a0e60b4897`
- License: MIT
- `LICENSE` SHA-256: `694c91613d9a32941e2548472f6c1a8099eb54078273d8782f7829da0bb8c266`
- Source inventory: 43 Go files, 20 test files, and 52 test functions.
- Normal source-health run: 52 test runs, 59 pass events, 3 skips, exit code 0.

The source test baseline is not a production denominator. A production Go task
requires a separate verifier with an independently frozen collection contract.

## Public behavior inventory

The exported packages include `fsql.Run`, `parser.Run`, `query.Query`,
`query.NewQuery`, `query.Query.Execute`, `tokenizer.NewTokenizer`,
`transform.Parse`, `transform.Format`, `evaluate.Evaluate`, `meta.Meta`, and
terminal/pager entry points. The CLI is `cmd/fsql/main.go` and supports `-v`,
`-version`, positional queries, stdin, and interactive mode.

## Dependency probe

The clean offline command was:

```text
GOMODCACHE=/tmp/go-fsql-empty-modcache GOCACHE=/tmp/go-fsql-empty-cache GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local go test -json ./...
```

It exited 1 before collection because the task-local empty cache did not contain
`github.com/oleiade/lane@v1.0.1`, `golang.org/x/crypto@v0.17.0`,
`golang.org/x/sys@v0.15.0`, or `golang.org/x/term@v0.15.0`. No module bundle was
created in the shared CAS.

## Why the task is blocked

The current typed Go bridge cannot faithfully represent the package's host
contract. The implementation reads real filesystem trees and metadata, expands
home paths, resolves globs, computes file hashes, invokes an external pager, and
offers an interactive terminal path. Result ordering and formatted paths are
also host-state dependent. Direct trusted/root imports or unrestricted host
access would violate verifier isolation and determinism.

## Remediation

1. Materialize and hash-lock all four Go modules in a private artifact bundle.
2. Approve a child-side protocol for virtual files, metadata/time/mode/hash
   fixtures, path/glob/home expansion, ordering, pager substitution, and bounded
   terminal input/output.
3. Add public-behavior assertions for the CLI and exported packages, then freeze
   their collection as a positive production denominator.
4. Compile the final source through the locked Go compiler and run one official
   Oracle plus empty, stub, forgery, and offline controls.

No Oracle, controls, reward, generated runtime, or production validity is
claimed until these steps are complete.
