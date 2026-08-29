# propcache authoring provenance

The authoring claim supplied revision `1ab64c4a5c9b0bbaa94679a546afbdf28e79533f`
from `https://github.com/aio-libs/propcache`. The detached checkout resolved to
that exact commit. `git archive --format=tar HEAD` produced a 307200-byte source
archive with SHA-256
`8f4d7e6e6a388c7d45e4830dcbfe286d3b43df40b97df0b7611f37f987ec79f2`.
The corresponding Git tree is
`c40251898aff4c4156dfc0a4a88a3b039e933caa`.
The upstream `LICENSE` is Apache-2.0 and hashes to
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.

The source contains 2240 lines across Python/Cython files and one `src/propcache`
package. Its public runtime surface is the two descriptors exposed by the
top-level facade and `propcache.api`; the `_helpers_py` and `_helpers_c` modules
are implementation variants. The upstream tests cover API wiring, cache hits and
misses, descriptor metadata, invalid cache state, assignment protection,
`__set_name__`, generic aliases, and reference-count behavior for both variants.

Native behavior is adapted into a deterministic child-side contract: the fixed
28-leaf verifier checks the observable descriptor and module behavior, while
benchmark-only `tests/test_benchmarks.py` is excluded because it requires the
external `pytest_codspeed` performance harness. No live service, native external
library, or network behavior is part of the task contract.

A fresh source-only collection at the frozen revision found 43 nodes across the
four functional upstream test files. With `PYTHONPATH=src` and no extension
build, the pure-Python/API slice passed 25 tests and deselected the 18 native
parameter cases. The production Oracle then built the CPython extension through
PEP 517 and passed all 28 adapted contract leaves, including the three explicit
native-extension checks.

The initial probe from the worktree root failed with pytest exit code 4 because
the root project's pytest configuration was selected; a direct upstream run
then succeeded. A first uv target-install probe failed with exit code 1 because
the minimal uv environment does not ship the `pip` module; the corrected uv
install path succeeded and built the C-extension package. These are recorded as
authoring environment remediation observations, not task blockers.

The first Harbor Oracle attempt rejected the archive because a changelog
symlink is not allowed in the candidate workspace; the Oracle solution now
removes only symlinks after verifying the frozen archive digest. The next Oracle
attempt reached the real Cython build and exposed the missing C standard headers
in the slim image (`stdlib.h`); the environment lock now installs `libc6-dev`
alongside `gcc`. The digest-pinned Harbor image was then inspected directly:
it is Debian GNU/Linux 13 (trixie) amd64 with CPython 3.12.14, so the source
environment lock records those container facts rather than the host probe
version. A subsequent verifier image smoke found that `runuser` is
provided at `/usr/sbin/runuser` by the base image, so the private child bridge
uses that resolved path. Because the verifier bundle is root-only, the trusted
runner stages a byte-identical adapter copy at `/tmp/propcache-adapter.py`,
changes ownership to UID 10001, and then launches it with `runuser`; the staged
file is removed after all leaves complete.
