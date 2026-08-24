# Source Freeze And Remediation Evidence

Status: `packaged`. This repair replaces the static blocked record with a
bounded Linux/Unix contract, a private child-process JSON verifier, an
offline candidate build closure, and an exact-revision Oracle solve bundle.
The task is not marked `oracle-passed` until the compiled Harbor smoke has
completed.

## Frozen source and license

- Repository: `https://github.com/tox-dev/platformdirs`
- Source commit: `d3cf61ce5e729f2c35f830b69e14adb7b6970a00`
- Required source tree: `9a2e1a4f3e8bfcda7896d35c4e156e3d90090dbd`
- Commit subject: `[pre-commit.ci] pre-commit autoupdate (#525)`
- Deterministic unprefixed archive SHA-256:
  `01837750779cd8f90d271f9b6184cf7d8d78fac37c72ce40ac97ccfb4064d572`
- MIT license blob: `f35fed9191b1142ddaada8a96de4a9461c5d796c`
- MIT license SHA-256:
  `29e0fd62e929850e86eb28c3fdccf0cefdf4fa94879011cffb3d0d4bed6d4db6`
- Submodules: none.
- Package version from the frozen discovery record: `4.11.3`.

The tree hash is recorded separately because Git trees are not checkout-able
commits. The Oracle fetches only the full commit above and verifies that its
tree matches the required tree before copying source files.

## Environment and dependency closure

The verifier uses the repository toolchain's digest-pinned `linux/amd64`
Python image and no network. Candidate installation uses a private bundle
containing only hash-locked build requirements:

```text
setuptools==80.10.2
wheel==0.45.1
```

The upstream Hatch VCS backend is not usable from a source archive without a
Git checkout. The Oracle solve therefore writes the generated static version
module and a minimal setuptools build configuration after verifying the
archive. This is packaging remediation; runtime files are copied unchanged
from the frozen source tree.

The dependency archive and verifier archive are content-addressed private
artifacts referenced by `task.toml`. Their bytes are kept on project disk in
the task-local `.work` artifact store and are not copied into public
instruction text.

## Contract boundary

The original upstream suite directly imports the package, patches
`sys.platform`, native APIs, module caches, and filesystem state. Those tests
are not used as a trusted-process denominator. The repaired contract covers
the deterministic Unix/XDG surface only: constructors, directory/path
properties, multipath ordering, XDG overrides, user-dirs parsing, iterators,
opt-in temporary-directory creation, convenience functions, exports, and the
module report. The candidate is imported only by a subprocess launched by the
private verifier.

## Attempted commands and next unblock action

1. `git init .work/source && git fetch --depth 1 origin d3cf61ce5e729f2c35f830b69e14adb7b6970a00` - passed;
   the checked-out tree is the required `9a2e1a4f3e8bfcda7896d35c4e156e3d90090dbd`.
2. `git fetch ... 9a2e1a4f3e8bfcda7896d35c4e156e3d90090dbd` - intentionally not
   used for checkout because the value is a tree object, not a commit.
3. Two archive and license digest checks - passed with the values above.
4. `pip download --only-binary=:all:` for the pinned build/verifier closure -
   passed; wheel hashes are recorded in `evidence/wheelhouse.sha256`.
5. Candidate installation probe with the generated static build metadata -
   passed locally; the installed package reports version `4.11.3`.
6. Harbor source validation, generic compilation, and one Oracle/control smoke
   are attempted after the private bundles are ingested. Any Docker or
   artifact-store failure remains an infrastructure blocker with its command
   and log path recorded in the handoff.

Next unblock action if the smoke cannot run: provide the missing Docker image
or local Harbor/private-artifact access, then rerun the exact compile and
Oracle command without changing the source revision or frozen denominator.

## Generic compiled evidence

- The first Oracle attempt was an artifact/environment failure because the
  Oracle solve script required `git`, which was absent from the initial agent
  image; it was not counted as a candidate result.
- After adding `git` and `ca-certificates` to the pinned agent environment and
  recompiling, the generic compiled Oracle passed `20/20`, reward `1.0`, at
  `.nl2repo/runs/oracle/platformdirs-custom-compiled-v2/2026-08-24__14-55-00/platformdirs__h8jF3Rw/verifier/grading.json`.
- Empty: reward `0.0`, candidate-install failure classified as `model`, at
  `.nl2repo/runs/controls/platformdirs-custom-empty-v1/2026-08-24__14-58-55/platformdirs-empty__4BrDcrM/verifier/grading.json`.
- Stub: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/platformdirs-custom-stub-v2/2026-08-24__14-56-59/platformdirs-stub__mMTLXXA/verifier/grading.json`.
- Forgery: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/platformdirs-custom-forgery-v2/2026-08-24__14-56-59/platformdirs-forgery__uDdohct/verifier/grading.json`.
- Offline: the compiled verifier uses the no-network profile.
