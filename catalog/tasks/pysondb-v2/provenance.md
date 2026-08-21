# pysonDB-v2 Provenance Audit

Status: **packaged**. This task-local record captures the legacy contract,
the immutable verifier image, the upstream source lock, the image/source
comparison, and the frozen denominator. It does not contain hidden tests,
fixtures, a copied upstream tree, or run results. Oracle and negative controls
remain parent-owned gates.

## Legacy Contract

- Task: `test_files/pysondb-v2/`.
- Declared denominator: `96`; `test_case_count.txt` SHA-256 is
  `7b1a278f5abe8e9da907fc9c29dfd432d60dc76e17b0fabab659d2a508bc65c4`.
- Commands: `pip install -e .`, then
  `pytest --continue-on-collection-errors tests`; `test_commands.json` SHA-256
  is `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`.
- Protected path: `tests`; `test_files.json` SHA-256 is
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.
- Public legacy instruction: `start.md` SHA-256 is
  `fd2fa6e725737db82dda186719deab5b93326fbf4a34e74d691818225194a09d`.
- The public Harbor instruction is copied from this legacy instruction. It
  retains the repository-generation contract without copying test assertions.

## Pinned Verifier Image

The canonical conversion-loop record observed at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` records this available
`linux/amd64` image:

`ghcr.io/multimodal-art-projection/nl2repobench/pysondb-v2@sha256:d54c22d710aaf1dbb3aee8894536e2fc3ca26b685c10a427f9b175b4d81e3c96`

The record's tag is
`ghcr.io/multimodal-art-projection/nl2repobench/pysondb-v2:1.0`. A registry
manifest-only request returned:

- raw manifest SHA-256 and content digest:
  `sha256:d54c22d710aaf1dbb3aee8894536e2fc3ca26b685c10a427f9b175b4d81e3c96`;
- media type: `application/vnd.docker.distribution.manifest.v2+json`;
- config digest:
  `sha256:515d6e1a0830417ca49736e023a050e727082e4d1ed91db30fd102990863240e`;
- layer count: `21`.

The config records CPython `3.10.11`, working directory `/workspace`, and a
terminal `tail -f /dev/null` command. Relevant immutable layer evidence is:

| image content | compressed layer digest | bytes |
| --- | --- | ---: |
| test tree copied to `/workspace/tests` | `sha256:24d55b8c853161ed1c146e4c04457e9d4c0454605faf06197fb54f4eb6bbfc35` | 7,708 |
| source checkout copied to `/pysonDB-v2` | `sha256:63a7f81b24fa5a17c5a8866618334a6343b2ca4f61d3f1419d8b20ca049a0f44` | 566,294 |
| `setup.py` | `sha256:6a3735e294c720fac4e99c934b5c86db634279204e28688d9397d80a0ae22fc0` | 171 |
| `setup.cfg` | `sha256:2bb4d793d90161a12a1b2c6220e2a484931ea2fc1e8fdce8a648cebb7d39cf43` | 717 |
| `requirements.txt` | `sha256:82d6613177d546441eb047dca9fcfd464c011757921705c5d9e46aca13c2c414` | 166 |
| `requirements-dev.txt` | `sha256:785a68b0f5608504d1ec2c39095cfceade691f2161327eb6125de391a8b743ff` | 179 |

Only manifest/config metadata and temporary extraction under `/tmp` were
inspected. Docker and Harbor were not run.

## Upstream Source Lock

- Repository: `https://github.com/pysonDB/pysonDB-v2`.
- Full revision: `4399314ecdc3f394ccc92ecd440de4b0180b12a8` (`v2.2.0`, the
  `master` tip observed during this audit).
- Revision tree: `e17b4231abe4958fa80a86238f5d309ff310aae0`.
- Deterministic archive command:
  `git archive --format=tar 4399314ecdc3f394ccc92ecd440de4b0180b12a8`.
- Unprefixed archive size: `122,880` bytes.
- Archive SHA-256:
  `4a80fa0f2e29fa613bd946c536159a5769607c0bd6748d1feb7f65db71bf4f07`.
- License: `MIT`, evidenced by upstream `LICENSE` at this revision.
- License Git blob: `aceacfa6848ac25891285e1a89692369ea7023a`;
  `1,071` bytes; SHA-256
  `317c55eb731a2d8e3c4bec9cadf6e451ae02c09ccb909905a8c698b82a018a73`.

The Oracle script fetches the full revision, verifies the resolved commit and
archive hash, and materializes the archive into `/workspace`. It does not use
a branch, tag, or floating image reference.

## Image Test Comparison And Denominator

The pinned image contains 25 files under `/workspace/tests`, totaling 46,288
raw bytes. The test tree has 62 Python test functions. Twelve parametrized
functions contribute 46 cases and the remaining functions contribute 50:

`50 + (5 + 3 + 5 + 3 + 3 + 2 + 5 + 5 + 3 + 2 + 5 + 5) = 96`.

No skip or xfail decorator was found in the image test tree. Every image test
file and migration JSON fixture compares byte-for-byte with the corresponding
upstream file after normalizing CRLF to LF. The raw image test bytes remain
private; the Harbor verifier copies them from the pinned image at build time,
checks the listed hashes, and never commits them under this task directory.

The image checkout's `.git` metadata resolves to the same full upstream
revision and remote. The only normalized source difference is a packaging
overlay in `setup.cfg`: the image removes `long_description = file: README.md`
and `license_file = LICENSE`. All implementation modules, tests, fixtures,
license text, and remaining metadata match the upstream revision after line
ending normalization. This is recorded as a build-only packaging overlay, not
silently attributed to the upstream source lock. The Oracle script still
materializes the unmodified upstream archive.

## Dependency And Boundary Notes

- The image history installs `prettytable==3.3.0` from `requirements.txt` and
  the unpinned `requirements-dev.txt` set (`pytest`, `pytest-mock`, `mypy`, and
  `pre-commit`), then installs the package and runs its tests. The verifier
  therefore owns the frozen test dependency closure; no wheelhouse is copied
  into this public task package.
- The agent image is separate, digest-pinned Python 3.10.11 with `git` and
  `ca-certificates`; the verifier is derived from the immutable legacy image
  and runs with `no-network`.
- The verifier copies the candidate to `/tmp/candidate`, installs it in a
  candidate-owned `venv --system-site-packages` as UID 10001, replaces the
  candidate's `tests` path with the root-owned private fixture, and checks
  JUnit collection against both `96` collected and `96` effective cases.
- `grade.py` alone writes `/logs/verifier/reward.json` and
  `/logs/verifier/grading.json`; it rejects missing/malformed JUnit output,
  collection mismatch, abnormal pytest exit, and symlinked JUnit output.

## Decision And Parent Gates

The source URL, immutable revision/license/archive, image digest, exact test
overlay (none in behavior), and fixed denominator are coherent. Keep this
task at lifecycle `packaged`, not `oracle-passed` or `published`, until the
parent records three independent valid Oracle runs with stable collection and
reward at least `0.80`, plus empty/stub/forgery/offline controls.

Residual risks are the recorded packaging-only `setup.cfg` overlay, unpinned
development requirements inside the frozen legacy image, and the need for
parent-side verifier boundary/forgery controls. No dataset, shared script,
conversion-loop state, legacy artifact, or other task directory was modified.
