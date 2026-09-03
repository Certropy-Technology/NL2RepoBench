# pytest-xdist authoring provenance

## Source freeze

- Upstream: `https://github.com/pytest-dev/pytest-xdist`
- Revision: `2a0c02df173a8340670b59903426e741811d6ab3`
- Revision check: `git ls-remote ... HEAD refs/heads/master` resolved both refs to this SHA.
- Source archive: unprefixed `git archive --format=tar HEAD`
- Archive SHA-256: `sha256:2dbd281557752aa0463fc18e1eadaee1f5d090e1ae88149687a976afff4622e0`
- License: MIT; `LICENSE` is 1,088 bytes, SHA-256 `sha256:36c15bf831b218a24d122e3b30256b3e1ca285716c24937fe6d8475074ee9032`.
- Commit date: `2026-09-01T06:23:57+02:00`; subject: `[pre-commit.ci] pre-commit autoupdate (#1376)`.

## Inventory and tests

The runtime contains 18 Python modules under `src/xdist`, seven upstream test
files plus `conftest.py` and `util.py`, and 237 collected upstream leaves.
The first full run on Python 3.12.11 with pytest 9.0.1, execnet 2.1.2 and
psutil 7.1.3 passed 210 leaves, skipped 5, xfailed 10, and failed 12 locking
cases because `filelock` was absent. This is an environment omission, not a
source failure. The lock adds exact `filelock`; a follow-up run confirmed the
extra is installed, but the repository's parent pytest configuration leaked
coverage options into pytester subprocesses, producing a separate 163-failure
configuration result. The scored contract therefore uses isolated child
scenarios and records the upstream suite as authoring evidence rather than
pretending that the polluted follow-up is a source pass.

The scored denominator is a 14-leaf private contract executed through the
repository's UID-separated `custom-json-v1` candidate client. It covers the
stable local API and popen distribution behavior while excluding external SSH,
socket, interactive TTY, and obsolete pytest-hook conditions.

## Network and boundary

The candidate and verifier use `no-network`; `agent_allowed_hosts` and
`verifier_allowed_hosts` are empty. The Oracle `solve.sh` alone fetches the
frozen revision from the exact upstream host, verifies the resulting commit and
archive digest, and extracts it into the trusted Oracle workspace. Hidden
verifier and adapter bytes are private CAS artifacts and never enter the agent
image or public instruction.
