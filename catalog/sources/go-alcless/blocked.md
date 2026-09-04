# `go-alcless` Go authoring audit: blocked

**Status: blocked.** This source-local record is an evidence-backed audit, not a
published Harbor task. No `catalog/tasks/go-alcless/` runtime, private test
bundle, Oracle bundle, dependency cache, credential, or shared-index change is
created by this lane.

## Frozen source

- Upstream: `https://github.com/AkihiroSuda/alcless`
- Exact revision: `0a1a474ef54f4bc995ecb15f2814202129273ae7`
- Revision assertion: passed after a depth-1 fetch and detached checkout.
- Git archive SHA-256: `d22a70ed3ec9889122b61b45af8e5508b73e64170c0111a06ed4e659bd8764df`
- License: Apache-2.0
- `LICENSE` SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- Source inventory: 15 Go implementation files, 1 Go test file, 1,465 physical
  implementation/test lines, and 1,078 non-comment implementation SLOC in the
  discovery report.
- Module path: `github.com/AkihiroSuda/alcless`.
- Go directive: `1.26.3`; the locked task toolchain available to this repository
  is Go `1.26.5` on Linux/amd64.

The source archive and command logs are retained under the task-local authoring
work directory and are not copied into the public source. The source digest in
`task.toml` binds the exact archive bytes observed by this lane.

## Test inventory and denominator

The frozen checkout contains one test function:

```text
cmd/alclessctl/commands/create/create_test.go: TestResolveInstName
```

It tests the unexported `resolveInstName` helper, including default naming,
explicit names, the `template://default` sentinel, slash rejection, unknown
templates, and conflicting positional/flag names. The static test inventory
therefore observes one test function and no public API assertion. It does not
justify a production task that claims to reproduce the command's host-level
behavior. `expected_total = 1` is recorded as the observed source-test count;
no Harbor collection or verifier denominator was claimed.

## Public behavior assessment

The public implementation is primarily a host integration CLI rather than a
portable Go library. Its behavior depends on:

- `create`: OS user creation, sudoers configuration, Homebrew detection and
  optional Homebrew installation;
- `delete`: OS user deletion and sudoers cleanup;
- `list`: host account enumeration and JSON/table output;
- `shell`: `sudo`/`su`, optional PTY, current working directory mapping,
  rsync in both directions, and arbitrary child commands;
- `pkg/userutil`: `getent` on Linux or `dscl` on macOS, plus user database state;
- `pkg/sudo`: host `sudo`, `su`, current-user lookup and shell quoting;
- `pkg/rsync`: the installed executable path and an external `rsync` command;
- `pkg/brew`: host filesystem, GitHub Homebrew checkout, and platform-specific
  Homebrew prefixes.

These behaviors require native host state, privilege boundaries, filesystem
side effects, external processes, optional TTY semantics, and in one path a
network checkout of Homebrew. The current Go production profile requires a
single deterministic `custom-json-v1` leaf through a typed subprocess bridge;
it cannot preserve these semantics without an approved task-specific adapter
and a deterministic host fixture. The only upstream test does not supply such
coverage.

## Dependency probe

The bounded Linux/amd64 no-network probe was:

```text
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local go test -json ./...
```

It exited with code 1 before test collection. Missing modules included
`al.essio.dev/pkg/shellescape`, Cobra/pflag dependencies,
`github.com/containerd/containerd/v2`, `github.com/lmittmann/tint`, and
`golang.org/x/term`. The task-local lane did not write a module bundle or use
the central CAS. This is an environment/dependency failure, preserved as
evidence rather than treated as a model result.

## Blocker and remediation

Primary failure class: `verifier`.

The task cannot enter the current Go production profile because there is no
reviewed adapter that can express its host-user, privilege, rsync, Homebrew,
external-process, and TTY semantics while keeping the verifier separate and
deterministic. The dependency probe is a secondary `environment` blocker.

Next unblock action:

1. Decide whether a separately approved host-fixture/CLI adapter is in scope;
2. freeze a complete Go module closure and an OS/toolchain image that contains
   the required non-Go utilities without allowing candidate-side network access;
3. add tests for the public CLI behavior, not only the private naming helper;
4. design and review a bounded subprocess protocol for host-state operations;
5. rerun source-only collection, production compile, Oracle, and all controls.

Until those decisions and artifacts exist, this task must remain blocked. No
runtime is generated and no Oracle/control receipt is fabricated.
