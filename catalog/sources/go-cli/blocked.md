# `go-cli` Go authoring audit: blocked

**Status: blocked.** This source-local record is an evidence-backed audit, not a
published Harbor task. No `catalog/tasks/go-cli/` runtime, private test bundle,
Oracle bundle, dependency cache, credential, or shared-index change is created.

## Frozen source

- Upstream: `https://github.com/smallstep/cli`
- Exact revision: `eb1901e52427e629b5932b087f06807ce0dcc8ab`
- Revision assertion: passed after a filtered clone and detached checkout.
- Git archive SHA-256: `6669bc71d169ed6d06f3afd987ceb83f8edb31ce1897259d5384a0f8ab1ad301`
- License: Apache-2.0
- `LICENSE` SHA-256: `6fac0a40e0507e3ba32cd3471c808fa5ba4b088700bd22d81250f40f6cc74db5`
- The checkout contains 222 Go files, approximately 60,184 nonblank Go source
  lines, 32 Go test files, and 101 top-level test functions.
- The module declares Go `1.25.8`; the locked repository Go lane is Go `1.26.5`
  on Linux/amd64.

The source archive and command logs are retained only in the task-local authoring
work directory and are not copied into the public source. The source digest in
`task.toml` binds the exact archive bytes observed by this lane.

## Surface and command breadth

The `cmd/step` binary registers these top-level groups: `base64`, `path`,
`certificate`, `completion`, `context`, `crl`, `crypto`, `oauth`, `version`,
`ca`, `beta`, and `ssh` (plus help). Static inspection found approximately 151
`Command` constructors across 82 command directories. The source includes CA
initialization and administration, X.509 and SSH certificate issuance,
provisioner and policy management, ACME, OAuth/OIDC, JWT/JWK/JWE/JWS, KDF,
NaCl, OTP, key and certificate installation, fileserver, and shell completion.

This breadth cannot be expressed honestly as a small fixed API contract. The
upstream tests also cover a mixture of private helpers, integration subprocesses,
cryptography, certificate files, prompts, and CLI registration rather than one
bounded public package contract.

## Host, network, and security dependencies

The implementation directly uses HTTP/TLS and TCP listeners for CA, ACME, CRL,
API-token, OAuth, and fileserver workflows. It invokes child processes and
platform commands for exec, browser opening, pagers, renewal, and plugin flows;
uses OS-specific syscall, signal, terminal, SSH-agent, and Windows code; and
supports password prompts, browser redirects, system trust stores, filesystem
state, and optional PKCS#11, TPM, cloud-KMS, and HSM-backed keys. Several command
paths depend on `step-ca` or another remote CA, OAuth providers, external SSH
agents, or an available browser/TTY.

The current Go production profile requires a separate verifier and a typed
subprocess bridge. A faithful adapter would need deterministic fixtures for
network/CA and OAuth protocols, certificate and trust-store state, TTY/browser
behavior, external command results, filesystem installation, SSH-agent state,
and optional hardware-backed cryptography. No such approved adapter exists, and
weakening the task to pure helper tests would no longer represent this CLI.

## Test and dependency probe

The frozen checkout has 101 statically observed test functions across 32 test
files. The candidate denominator is not frozen because the no-network probe
cannot complete dependency resolution and collection. The bounded probe was:

```text
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local go test -json ./...
```

It exited with code 1 before complete collection because offline module lookup
was disabled and required modules such as `github.com/rogpeppe/go-internal`
and `github.com/smallstep/assert` were not in the local module cache. The source
contains 135 direct/declared module requirements and `go list -m all` resolves
632 modules when network-backed resolution is available. This is recorded as a
secondary environment/dependency blocker, not a model result.

## Blocker and remediation

Primary failure class: `verifier`.

The task cannot enter the current Go production profile because the CLI's
observable behavior spans network services, PKI/crypto state, host filesystem
and trust stores, subprocesses, TTY/browser interaction, OS-specific APIs, and
optional KMS/TPM/HSM devices. The source tests do not provide a reviewed,
deterministic adapter for these contracts. The dependency probe is a secondary
`environment` blocker.

Next unblock action:

1. Approve or reject a scoped task contract, rather than silently representing
   the full CLI with a small helper subset;
2. If approved, define a deterministic CA/OAuth/network fixture and a bounded
   subprocess protocol for filesystem, child-process, TTY, browser, SSH-agent,
   and trust-store operations;
3. Freeze the complete Go module closure and a reviewed image containing all
   required non-Go utilities without candidate-side network access;
4. Add public-behavior tests and freeze collection after the adapter is reviewed;
5. Rerun source-only collection, production compile, Oracle, and all controls.

Until those decisions and artifacts exist, this task must remain blocked. No
runtime is generated and no Oracle/control receipt is fabricated.
