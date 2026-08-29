# `h11` Static Authoring Audit

## Identity and scope

The candidate is `python-hyper/h11` at detached commit
`62c5068c971579d61fa1b55373390e12f25fd856`. The checkout has no submodules,
no native extension, and no runtime dependency outside the Python standard
library. Its tracked source tree contains 69 files, including the package and
11 upstream test modules plus one test helper and one test data file.
`setup.py` uses `setuptools`, reports the development version `0.16.0+dev`, and
declares the MIT license.

The source archive is the exact unprefixed `git archive --format=tar HEAD`
whose SHA-256 is recorded in `task.toml`. The license file is `LICENSE.txt`;
its SHA-256 is recorded in provenance. The package is suitable for a bounded
no-network task because the protocol engine has no sockets, subprocesses, or
external services in its runtime path.

## Behavior boundary

The complete upstream suite was collected at 78 leaves and passed 78/78 when
ambient coverage/addopts were disabled. The task does not claim full upstream
pytest parity. The scored contract is a 24-leaf custom JSON suite that tests
event normalization, header validation, serialization, parsing, body framing,
sentinel flow control, lifecycle transitions, and deterministic exports through
an unprivileged candidate subprocess.

The standard-library integration transport, fuzz harness, sendfile placeholder
objects, and documentation-only helpers are excluded because they either
require external I/O or are not a stable JSON-compatible candidate boundary.

## Remediation completed

- The legacy `setup.py` build backend is closed with exact `setuptools` and
  `wheel` pins in the private lock artifact.
- The verifier is separate and does not import candidate code in the trusted
  process; it calls the canonical candidate runner through `custom-json-v1`.
- The Oracle receives only a private archive containing `solve.sh` and the
  digest-verified source archive; model Agent and verifier metadata retain
  `no-network` with no static allowed hosts.
- The source revision, archive digest, license, toolchain, dependency lock,
  frozen denominator, and scenario IDs are all recorded in task-local files.

## Production gate refresh

The current production compile was regenerated at
`.nl2repo/compile-handoff-final-h11/h11` with Harbor 0.21.0, `toolchain.lock.toml`,
the private artifact store, and `--allow-private` (no `--allow-incomplete`). The
bundle manifest digest is
`sha256:b666c65d67379b97bc955522f207a203d686ab3a57ae77222b17bbfb6eeb2273`.

The official Harbor Oracle run completed one trial without exceptions and
returned 24/24, reward 1.0. Official `nop` empty, generated stub, and
generated forgery controls each completed without exceptions; empty used the
documented installation-failure exception with reward 0.0, while stub and
forgery collected all 24 leaves and passed 0. The forgery result was produced
by the trusted verifier despite the workspace reward file. Every receipt
reported `public_network_available=false` and both public probes failed.

The task remains `controls-passed`, not `published`: no model Agent Run,
blind review, pilot, dataset integration, or publication was performed in
this lane. The verifier retains bounded 120-second candidate-install and
360-second candidate-total budgets; no separate hang-control receipt was
claimed because the current production control registry requires only
empty/stub/forgery/offline for this Python source.

The shared toolchain locks the agent runtime to image ID
`sha256:70525a5fbee81f4d202b7f7de14857fe78f961ce2ec3995efd1a4850e45c7ea5`,
but that image was not present. The same tag resolved locally to
`sha256:55f9ac341e8782cbd31e57abe8e6ee2941dab68526894c2386a70f5f96c3fce7`.
Its fork-commit label, SDK/tools/LiteLLM versions, and no-network smoke match
the runtime contract, but content identity does not. The integrator must
restore the locked image and rerun the matrix before release; this source is
therefore evidence-backed `controls-passed`, not production-valid/published.
