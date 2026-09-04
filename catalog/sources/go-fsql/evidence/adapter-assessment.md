# go-fsql adapter assessment

## Frozen source

- Upstream: `https://github.com/kashav/fsql`
- Revision: `5cfe17e9b3c69aee6e65cc5d73b7c40cc1ffa87e`
- Git archive SHA-256: `52a1d205d660c7b3cec7e3e8d40502502f6425e7669de46b8ebf63a0e60b4897`
- License: MIT
- `LICENSE` SHA-256: `694c91613d9a32941e2548472f6c1a8099eb54078273d8782f7829da0bb8c266`

## Surface and boundary

The source is a filesystem-search CLI. The parser and tokenizer are mostly pure,
but the public behavior exposed by `fsql.Run`, `query.Query.Execute`, the
transform hash modifier, and the CLI depends on host state:

- `filepath.Walk` traverses included roots and glob matches and follows source
  aliases/exclusions with host path ordering.
- `os.FileInfo` supplies names, sizes, modes, and modification times; `~` is
  expanded using `os/user.Current`.
- SHA1 hashing reads the selected path and has symlink handling.
- Output includes formatted paths and tabular alignment derived from the walked
  results.
- The no-query CLI path enters an interactive `terminal.Start` loop using stdin
  and terminal state; output can launch an external pager through `exec.Command`.
- The CLI uses process arguments, environment expansion, current working
  directory, and external commands in addition to the query parser.

A separate verifier would need a child-side protocol for a virtual filesystem,
stable metadata and ordering, hash fixtures, home-directory expansion, glob
matching, pager substitution, and bounded terminal input/output. Directly
importing the candidate from the trusted verifier would violate the Go lane
isolation contract. No reviewed adapter or private module closure is available
in this task-local authoring lane.

## Dependency and test evidence

The frozen checkout contains 43 Go files and 20 test files with 52 test
functions. The normal source-health run passed with 59 pass events and 3 skip
events. A clean `GOMODCACHE` and `GOCACHE` with `GOPROXY=off` failed before
collection because four third-party modules were absent. The exact command
outputs are retained in the task-local evidence logs.

## Blocker and remediation

Primary failure class: `verifier`. Secondary failure class: `environment` for
the missing offline module closure. To unblock, materialize and hash-lock the
four modules, define a deterministic child-side virtual-host fixture, add public
behavior tests for the CLI and exported packages, and rerun collection, compile,
Oracle, and all controls against the resulting final bundle.

Until that work is complete, this task remains blocked. No Harbor runtime,
Oracle, controls, reward, or production denominator is claimed.
