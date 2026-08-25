# pysonDB-v2 Provenance Audit

Status: **controls-passed**. This task-local record captures the legacy
contract, upstream source lock, image/source comparison, hash-locked dependency
closure, private subprocess verifier and Oracle artifacts, one official Harbor
Oracle, and the required negative controls. Reviews, pilots, and publication
remain out of scope.

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

## Historical Pinned Verifier Image

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

The production Oracle artifact contains a tree produced by `git archive` at
this revision and a `solve.sh` that copies that immutable tree into
`/workspace`. The Oracle run therefore performs no source fetch and requires
no source-host authorization.

## Image Test Comparison And Denominator

The pinned image contains 25 files under `/workspace/tests`, totaling 46,288
raw bytes. The test tree has 62 Python test functions. Twelve parametrized
functions contribute 46 cases and the remaining functions contribute 50:

`50 + (5 + 3 + 5 + 3 + 3 + 2 + 5 + 5 + 3 + 2 + 5 + 5) = 96`.

No skip or xfail decorator was found in the image test tree. Every image test
file and migration JSON fixture compares byte-for-byte with the corresponding
upstream file after normalizing CRLF to LF. The production verifier does not
direct-import that tree: it maps the same 96 source-named cases to bounded
candidate-user subprocess operations and returns the custom JSON leaf report
to the trusted grader.

The image checkout's `.git` metadata resolves to the same full upstream
revision and remote. The only normalized source difference is a packaging
overlay in `setup.cfg`: the image removes `long_description = file: README.md`
and `license_file = LICENSE`. All implementation modules, tests, fixtures,
license text, and remaining metadata match the upstream revision after line
ending normalization. This is recorded as a build-only packaging overlay, not
silently attributed to the upstream source lock. The Oracle script still
materializes the unmodified upstream archive.

## Dependency And Boundary Notes

- The production build/runtime closure is a private raw requirements lock for
  `prettytable==3.3.0`, `setuptools==75.8.0`, `wcwidth==0.8.2`, and
  `wheel==0.45.1`, with SHA-256 hashes for every distribution. Both images use
  package-index access only during Docker build; no wheelhouse, `--no-index`,
  or vendored wheel is present in the task.
- Agent and verifier use digest-pinned Python 3.12.14 on Debian 13. Both run
  phases are `no-network`; the verifier additionally proves that
  `pypi.org:443` and `1.1.1.1:443` are unreachable.
- The generic supervisor copies the candidate, installs it as UID 10001 into
  `/tmp/candidate-site`, and never exposes the private verifier source to that
  user. Each of the 96 checks imports candidate code only in an isolated child
  process with a ten-second timeout.
- The trusted custom-verifier wrapper creates collection and JUnit reports;
  the generic grader alone writes `/logs/verifier/reward.json` and
  `/logs/verifier/grading.json`.

## Oracle And Control Evidence

Harbor `0.21.0` compiled this source in production mode without
`--allow-incomplete`. The single Package-campaign Oracle completed with
`valid=true`, `96` collected, `96` passed, no collection errors, and reward
`1.0`. Empty completed with valid model-class installation failure and reward
`0.0`. The packaging stub and forgery controls each retained all 96 leaves,
passed 3 inert checks, failed 93 behavioral checks, and scored `0.03125`.
The forgery's candidate-side `reward.json`, `grading.json`, and verifier-source
write attempts did not affect trusted grading.

Every Oracle/control `network.json` records
`public_network_available=false`; both hostname and numeric probes failed.
Exact commands and repository-relative receipts are listed in
`evidence/production-integration.txt`.

## Decision And Remaining Gates

The task is `controls-passed`. The source, license, archive, environment,
dependency lock, fixed denominator, separate verifier boundary, Oracle, empty,
stub, forgery, and offline gates are coherent. No review, pilot, dataset,
publication, shared code, commit, or push is claimed. The historical
packaging-only `setup.cfg` overlay remains recorded, but the production Oracle
uses the unmodified pinned source archive and passed all 96 leaves.
