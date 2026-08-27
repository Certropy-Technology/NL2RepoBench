# google-auth Authoring Provenance

Status: `awaiting-agent-run` for downstream Harbor model execution. This lane
restored the private artifacts, compiled the production bundle, ran the trusted
Oracle and the control matrix, and did not start a Harbor model Agent Run. The
catalog `[lifecycle].status` is `controls-passed` because the shared lifecycle
enum has no `awaiting-agent-run` value.

## Source lock

- Upstream: `https://github.com/googleapis/google-cloud-python`
- Package path: `packages/google-auth`
- Commit: `b4d97179f151d5ff37e6c7dbbd190a84c7d936a9`
- Commit date: `2026-08-22T00:17:55+05:30`
- Package version: `2.56.3`
- Package subtree archive: 313 members, 2,949,120 bytes,
  SHA-256 `c78d2dfa82d178bfff82dc803ca9c6aa1d836947849082ea6caafd2a63574e89`.
  Two independent `git archive --format=tar HEAD packages/google-auth` streams
  reproduced this digest in this lane.
- License: Apache-2.0. `LICENSE` Git blob `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`,
  file SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
- No submodules.

The monorepo archive is not used as the source identity because it contains
unrelated workspaces. The package subtree is the exact source closure.

## Environment

The digest-pinned base image from `toolchain.lock.toml`
(`python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`)
was inspected directly in this lane: Python 3.12.14, Debian 13.6, glibc 2.41,
x86_64, pip 25.0.1. The earlier recorded `3.12.11` / `debian-12` values were
wrong and have been corrected in `task.toml`.

That image ships **no setuptools and no wheel**. A probe confirmed that an
offline `pip install .` fails with
`Could not find a version that satisfies the requirement setuptools>=40.8.0`.
This was remediated rather than treated as a blocker: the task now carries a
hash-locked wheelhouse that is installed into both images and exported through
`PIP_NO_INDEX` / `PIP_FIND_LINKS`.

## Dependency closure

`setup.py` (setuptools, no `pyproject.toml`) declares `pyasn1-modules>=0.2.1`
and a `cryptography` floor. The frozen closure is:

```text
cffi==2.1.1            cryptography==50.0.0   pyasn1==0.6.4
pyasn1-modules==0.4.2  pycparser==3.0         setuptools==80.9.0
wheel==0.45.1
```

All seven wheels carry `--hash=sha256:` pins in `requirements.lock.txt`. Offline
proof in the built agent image: DNS fails with `gaierror` and `pypi.org:443` is
unreachable, yet `pip download setuptools` and `pip install .` both succeed from
`/opt/wheelhouse`, and `import google.auth, google.oauth2, cryptography` works
with `version.__version__ == "2.56.3"`.

## Network posture

`agent_network_mode = "no-network"` with empty `agent_allowed_hosts`; the
verifier is a separate image, also `no-network`. The verifier compose sets
`network_mode: none`, while the Agent compose is intentionally omitted so
Harbor's egress sidecar can enforce its run-scoped policy. The verifier's own `network.json` records
`public_network_available: false`.

The private `solution/solve.sh` still checks out the frozen revision over the network.
That is intentional and applies only to the trusted Oracle run, which receives a
run-scoped `--allow-agent-host` for the exact upstream host. The model Agent
never gets that override and cannot fetch the reference implementation.

## Verifier boundary

`verifier.protocol = "custom-json-v1"`, entrypoint `run.py`. The generic Harbor
wrapper copies the workspace, installs the candidate into a candidate-owned
site, and then runs `python -I /tests/verifier/run.py`. `run.py` is root-owned,
imports no candidate code, and spawns the hidden adapter as UID 10001. Only that
child imports the candidate package.

Three real defects were found by the control matrix and fixed in this lane:

1. `python -I` ignores `PYTHONPATH`, so the candidate site was invisible and
   every leaf failed with `ModuleNotFoundError: No module named 'google'`. The
   parent now passes sys.path entries as argv and the adapter inserts them.
2. The generic wrapper treats any non-zero entrypoint exit as
   `verifier-internal-error`. `run.py` now always exits 0 once it has emitted a
   valid report, so genuine leaf failures score as `model`, not `verifier`.
3. The compiled image installs `/tests/verifier` as root-only `0500`, so the
   unprivileged child could not read the adapter. The adapter is now staged as a
   root-owned `0444` copy under a `0555` directory.

Anti-forgery: the parent generates a per-run nonce, the adapter pops it out of
its environment and duplicates the real stdout before any candidate import, and
the report is only accepted when the nonce matches and the report has exactly 32
unique leaves. The forgery control plants `reward.json`, `grading.json`, a fake
`grade.py`/`run_scenarios.py`, and prints a well-formed full-marks marker from
its own package import; it still grades 0.0.

## Scope decision

The scored 32-leaf adapter covers deterministic credential and token semantics
only. It deliberately excludes GCE/AWS metadata, STS exchange, mTLS device
state, external-account exchange, Flask/localserver integration, and
`system_tests/`. These exclusions are stated in `instruction.md`; no functional
assertion was deleted to reach a threshold.

The earlier `google.auth.google_auth_rpc` requirement was removed from the
instruction. It forced candidates to implement evaluator plumbing rather than the
library itself; the verifier now supplies its own adapter.

## Results

Current task-local bundle:
`.nl2repo/authoring-work/python-author-wide-20260826-r2/google-auth/build/harbor-final/google-auth`.
Its bundle manifest digest is
`sha256:f6d8434f59606becb247bfd4f8b058efbdde100d27388d609cc0aa96ade2cad2`;
the pinned base image digest is
`sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
Harbor removes ephemeral runtime image tags after each job, so no post-run
agent/verifier image digest is claimed here:

```text
oracle             reward=1.0  valid=true   32/32
empty              reward=0.0  valid=true   0/0    candidate-installation-failed  model
stub               reward=0.0  valid=true   0/32
forgery            reward=0.0  valid=true   0/32
workspace-invalid  reward=0.0  valid=true   0/0    candidate-workspace-rejected   model
install-hang       reward=0.0  valid=true   0/0    candidate-installation-failed  model  (114s)
call-hang          reward=0.0  valid=true   0/32   adapter timeout                       (184s)
```

Frozen denominator is 32, generated by the adapter's own collection and echoed by
the wrapper's `collection.json` with zero collection errors.

The private artifacts used by this compile are content-addressed under
`.nl2repo/artifacts`: dependency lock
`sha256:dbb0487545ec7c74e5deaa0f4a3f4e7ef31a62d8820128dfb499c1751ba1b1c6`,
verifier bundle
`sha256:b809ff4081afa8ad1c7161ad7e7e4953a7d43cf1c35b9e382265e438f802eb2d`,
and Oracle bundle
`sha256:24795a7aedebd541803cf4243a7d52af575c325d7d8f2eeb79b92f0a04a13dd0`.

## Shared-code change

`src/nl2repobench/harbor/compiler.py` `_write_environment` previously generated
the Agent Dockerfile without any dependency closure, so every `no-network` Python
task compiled to an image that could not run `pip install .`. The minimal generic
fix materializes the locked dependency bundle into the Agent build context and
preinstalls it offline when `agent_network_mode == "no-network"`. This change is
kept in this worktree for integrator review.

## Residual risk

- The adapter proves 32 deterministic contracts, not the full upstream surface
  (2,025 upstream unit nodes). It is a behavior sample, not full coverage.
- One Oracle run is recorded. Cross-run stability was not studied here.
- No model Agent Run was performed, so real difficulty is unmeasured.
- Failures of downstream compile/image mechanics are `verifier`/`environment`,
  not a model score of zero.
