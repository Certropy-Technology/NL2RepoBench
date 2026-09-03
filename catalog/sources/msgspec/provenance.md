# msgspec Provenance

- Upstream: `https://github.com/jcrist/msgspec`
- Frozen revision: `f51f378335b01dc0026dc6553a0b9e1915a8edae`
- Revision check: `git -C .nl2repo/authoring-work/msgspec/upstream rev-parse HEAD` returned the frozen revision.
- License: BSD-3-Clause; upstream `LICENSE` SHA-256 is `6fde8b6723885e8508808f65ac372feb97d3eee2eab2b91d34d796b75b7ac734`.
- Source scanner digest: `sha256:758f580f703a0413ac4536c5815a5d90e4c9c83ffc6a4a5cb4063b7c187bb9f6`; reproducible `git archive` source digest bound in the task manifest: `sha256:0583e9ecf3d8f3f233722ba02361894e01f4bdc470e8fbe74d797ae758004390`.
- Build metadata: setuptools `setuptools.build_meta`, dynamic setuptools-scm version, Python `>=3.10`.
- Inventory: 33 Python implementation files, 30 test files, 1,431 statically named tests, 3,676 implementation LOC, and 18,887 test LOC. The package contains a native C extension in `src/msgspec/_core.c`.
- Frozen collection: 37 deterministic custom-verifier leaves, recorded in `test-inventory.json` and matched one-for-one by the private verifier `LEAF_IDS`.
- Environment remediation: added `gcc`, `libc6-dev`, `git`, and `ca-certificates` to the frozen system package contract; no runtime dependency is fetched by the Agent.
- Local build probe: `python3 -m pip install --no-deps -e .nl2repo/authoring-work/msgspec/upstream` exited 0 and compiled the extension on Linux amd64.
- Exact-runtime build probe: `uv run --python 3.12 --with pip python -m pip install --no-deps -e .nl2repo/authoring-work/msgspec/upstream` exited 0 and produced a `cp312` editable wheel.
- Frozen upstream unit probe: `python3 -m pytest -q tests/unit` exited 0 with `6410 passed, 113 skipped in 15.43s` after installing pytest `9.1.1`, pluggy `1.6.0`, iniconfig `2.3.0`, packaging `26.3`, and pygments `2.21.0`.
- Final production compile: `uv run nl2repo harbor compile catalog/sources/msgspec --output .nl2repo/authoring-work/msgspec/compiled-production-final --toolchain toolchain.lock.toml --artifact-root .nl2repo/artifacts --allow-private` exited 0; bundle manifest SHA-256 is `8e78dade1ac0edc14c66073ac01d4a28ee1cf613d9dbdecd336d2516d8529e5d`.
- Verifier-only smoke in the pinned verifier image with `--network none` collected 37/37 leaves, passed 37, reward 1.0, and recorded `public_network_available=false`; this is not an official Harbor Oracle receipt.
- Empty/offline controls completed with the permitted `candidate-installation-failed` exception; stub and forgery collected all 37 leaves with reward 0; call-hang collected all 37 leaves with reward 0; install-hang reached the bounded candidate-install timeout after approximately 182 seconds. Control receipts are task-local under `.nl2repo/authoring-work/msgspec/control-logs/`.
- Full Harbor Oracle and official control runs were not started in this lane by contract. The handoff therefore remains `awaiting-agent-run`; the trusted integrator must run Oracle with exact source-host authorization and official Harbor controls before changing lifecycle to a later gate.
