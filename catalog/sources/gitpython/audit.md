# GitPython Authoring Audit

Status: **controls-passed**, awaiting a separately authorized model Agent Run.

## Frozen source

- Upstream: `https://github.com/gitpython-developers/GitPython`
- Revision: `3481da9618e69063464c94447167d83bd45505a9`
- Version file: `3.1.60`
- License: BSD-3-Clause, `LICENSE`
- Unprefixed `git archive --format=tar` SHA-256:
  `8d6e3300bf477e7276e3a7280abf0bcb84c0f6b63ce05caa1ca70bfa4e50e8d8`

The revision is a merge commit and has no submodules. The source package is `git/`; the
repository also contains the independently packaged `gitdb/` and `smmap/` source trees, but
GitPython's `setup.py` installs only `git` and declares `gitdb>=4.0.1,<5` as its runtime
dependency.

## Scope decision

GitPython shells out to the system `git` executable and offers remote/network APIs. A complete
upstream test run would include remote, submodule, platform, and performance behavior that is
not suitable for a no-network Harbor Agent run. The private contract freezes 20 local scenarios
covering the install boundary, local repository lifecycle, objects, history, refs, index/diff,
configuration, actor parsing, local clone, and error behavior. Remote fetch/push, SSH, and
submodules are explicitly outside the scored surface.

The verifier never imports candidate code in the trusted verifier process. Each scenario starts a
fresh child interpreter with `PYTHONPATH` pointing to the candidate install and the hash-locked
`gitdb`/`smmap` dependencies.

## Environment and dependency closure

- CPython `3.12.14` on `debian-12-amd64`.
- Base image digest is pinned in `task.toml`.
- System package: `git`.
- Build/test lock contains exact hashes for `gitdb==4.0.12`, `smmap==5.0.2`, and
  `setuptools==84.0.0`.
- Agent and verifier run with `no-network`; only Oracle receives a run-scoped upstream host
  authorization while restoring the digest-checked archive.

## Final production gates

- Harbor `0.21.0` production compile completed without `--allow-incomplete` at
  `.nl2repo/authoring-work/python-author-wave2-20260828/gitpython/compiled-production-final/gitpython`.
  The generated manifest contains 59 files and has SHA-256
  `e14232a58733cd2c7ff5c4e4dba80f58aa24fbb4ec9cb827bb8b2e9cecb8d17b`.
- The trusted Oracle run passed all 20 deterministic child-side cases: `valid=true`,
  collection `20/20`, reward `1.0`, and exit code 0.
- Empty workspace, stub, and forgery controls completed with `valid=true`, collection
  denominator 20, and reward `0.0`. The forgery run produced no trusted score change.
- Install-hang and call-hang controls completed within bounded Harbor deadlines with
  `valid=true`, reward `0.0`, and no verifier exceptions. Install-hang was classified as
  `candidate-installation-failed`; call-hang collected all 20 leaves and recorded 20 failures.
- The verifier network receipt reported `public_network_available=false` for Oracle and
  every control run. A separate absolute-path offline smoke executed all 20 cases with
  `20/20` passed and no package download.
- Source validation, Python/Bash syntax checks, hash checks for source/lock/verifier/Oracle
  artifacts, and `git diff --check` passed. The full-catalog network lint returned zero
  errors; its unrelated warning findings are outside this task.

The task remains `awaiting-agent-run` at handoff because this lane is prohibited from
starting a Harbor model Agent Run. Review, pilot, and publication are not claimed.

## Reopen conditions

Recompile and rerun all gates if the frozen revision, public instruction, dependency lock,
private verifier bundle, Oracle bundle, or denominator changes.
