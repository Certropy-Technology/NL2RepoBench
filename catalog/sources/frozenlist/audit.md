# frozenlist authoring audit

## Frozen source

- Upstream: `https://github.com/aio-libs/frozenlist`
- Revision: `381c91e4663b067d5debab4cc19b400d3c459b44`
- Exact `git archive --format=tar HEAD` SHA-256: `sha256:0fa249ef870bbbd9267b5427dbcbe7d5a3dc92d439ab677c1f9f6f84717f9b5b`
- License: Apache-2.0; `LICENSE` SHA-256: `sha256:6fd5243e92dd7f98ec69c7ac377728e74905709ff527a5bf98d6d0263c04f5b6`
- Upstream package version at this revision: `1.8.1.dev0`
- No submodules.

The revision is the upstream `master` HEAD at freeze time and was resolved with
`git ls-remote` before a detached checkout. Two independent archive/checksum
operations must remain bound to this digest.

## Inventory and probes

The exact source tree contains one runtime module, one Cython source, one typing
stub, and one `py.typed` marker. The upstream test module contains 112 collected
leaves at CPython 3.12 with pytest 9.1.1. The accelerator and pure-Python probes
each passed 110 leaves. Two upstream re-import assertions fail because this
revision no longer exports the historical `NO_EXTENSIONS` module attribute;
those stale assertions are excluded from this task's fixed contract.

The task's private verifier instead collects 21 stable scenarios over an
unprivileged candidate subprocess. It checks both default import behavior and
`FROZENLIST_NO_EXTENSIONS=1`, without importing candidate code in the trusted
verifier process.

## Environment and dependency remediation

The source's in-tree PEP 517 backend needs `expandvars`, setuptools, and Cython
when building the extension. Those exact build inputs are hash-locked in
`provenance/requirements.lock.txt` and are installed only during the generated
Docker image build. The selected image is
`python:3.12.14-slim-bookworm@sha256:0f5b26b9518d002b6173fd61daad821fa340635ebfec5bba471013f9ca114579`.
No runtime package dependency is declared by frozenlist itself.

The candidate install is bounded and uses the compiler's `pip-target-no-deps-v1`
child boundary. Runtime agent and verifier network policy is `no-network` with
no task-local allowed hosts. Only a trusted Oracle invocation receives the
exact upstream host override to restore the frozen source.

## Verifier boundary

`evidence/run.py` is trusted and only compares JSON observations. It stages the
private adapter into a temporary read-only path, then runs that adapter as UID
10001 with `python -I -B`. The adapter imports only from the candidate target
directory and returns JSON-safe projections. The verifier owns collection,
JUnit, grading, reward, and network reports.

## Residual upstream risk

This is a native-capable package. The verifier passes `CFLAGS=-O0 -g0` and has
bounded address-space, CPU, file-size, process, and install-time limits. A
candidate may implement the contract in pure Python; the task tests the public
fallback and does not require a particular compiler artifact filename.
