# `wifiphisher` Static Conversion Audit

Status: **blocked**. This directory contains only this audit record. No
Harbor bundle, source archive, dependency bundle, verifier code, or hidden
test bytes are included. No dataset file, legacy file, or conversion-loop
state was changed.

## Decision

Do not publish a Harbor 1.4 bundle from the current legacy contract. The
upstream source tree is identifiable and the pinned image is immutable, but
the image-backed test collection is incompatible with the legacy denominator.
The image also contains an unapproved `setup.py` overlay and was built from
mutable dependency URLs without a task-local offline dependency closure.
Finally, the tests import candidate modules in-process and have no
candidate-client adapter for the required separate-verifier boundary.

Reopen only after the owner supplies a new frozen denominator and an approved
setup/dependency/verifier contract. Do not lower `43` to the image-derived
count or silently replace the setup overlay.

## Legacy Contract

The four files under `test_files/wifiphisher/` were read without modification:

| Artifact | Bytes | SHA-256 | Meaning |
| --- | ---: | --- | --- |
| `start.md` | 79,760 | `059282385a4e9968017d44ab79405f44eed746b2647123de46a99bc3ad7d204d` | Public instruction |
| `test_case_count.txt` | 2 | `44cb730c420480a0477b505ae68af508fb90f96cf0ec54c6ad16949dd427f13a` | Declares `43` (no trailing newline) |
| `test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`; `pytest --continue-on-collection-errors tests` |
| `test_files.json` | 9 | `af7f0b2bd3428222f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The legacy contract has no source revision, license lock, image content
manifest, frozen collection manifest, dependency lock, or verifier adapter.

## Immutable Verifier Image

The read-only conversion-loop record at
`/data/NL2RepoBench-current/.nl2repo/conversion-loop/state.json` assigns:

```text
ghcr.io/multimodal-art-projection/nl2repobench/wifiphisher@sha256:d71879503213ed94bf6fed3c001dc5e9d75668a5cdc9853816195fa44fbab613
```

Static registry evidence:

- manifest SHA-256 and `Docker-Content-Digest`:
  `d71879503213ed94bf6fed3c001dc5e9d75668a5cdc9853816195fa44fbab613`;
- platform: `linux/amd64`;
- config digest:
  `sha256:96967a8360f989a4997dc355d9280313744413931aa6a3d42d73f5f121d85692`;
- runtime: CPython `3.11.13`, working directory `/workspace`;
- task layers were fetched read-only and each compressed layer digest and
  registry size matched.

Relevant image history and layer identities are:

| Image history | Layer digest | Size | Content/operation |
| --- | --- | ---: | --- |
| `COPY ./wifiphisher-master/tests /workspace/tests` | `sha256:3c35800ee575080e23f4fcaf5922661139e18db686f7d527dfd20564f8ae932c` | 12,345 | Initial test overlay |
| `COPY ./wifiphisher-master/setup.py /workspace/` | `sha256:b6dfe41c3f08c3b5459152ba855853bb7afcd1cf9e3a22a0978394ae0e82f241` | 2,483 | Initial setup overlay |
| `COPY ./wifiphisher-master/ /project/` | `sha256:21ca5de6e41560325c079992c4bfd5b27c5e78f67ada4ea89710798614eb9676` | 1,764,960 | Full source used for image build |
| `pip install ... roguehostapd ... pyric` | `sha256:435ff9055c54e98a42fd96c0af29be6b709ed38f57cfac03d5005bd15d1659cf` | 8,119,386 | Mutable URL dependency install |
| `cd /project && pip install .` | `sha256:5905e68f65d2e421081315fb8045ae19967812ae191a8cc77d9f48566aa88689` | 14,081,921 | Project install |
| `pytest /workspace/tests` | `sha256:0e49f72e0805082fbb7589001d89dcbb2940f84293abd056fb43f15b23589c29` | 1,086,981 | Historical image test step/cache |
| Final workspace overlay | `sha256:7d75c624d5bfd1ed464af3cd78d33ad76cee25d19898370d24dea9f4bc4a2d23` | 46,108 | Replaces `setup.py` and test tree, retains cache |

The image history is provenance evidence only. No Docker container, Harbor
run, Oracle, or pytest command was executed in this audit.

## Upstream Source Lock

The full source copied into the image's `/project` tree is byte-identical at
all 133 paths to this GitHub revision:

- URL: `https://github.com/wifiphisher/wifiphisher`;
- full commit: `b11da3566b1c3430a23341a3b007ddcbf9cf61cc`;
- parent: `bc4a077e090d59b065cf2c65b0ec1890b9eb4698`;
- tree: `cb9a500bc49136d93d24c2f71944082585545df6`;
- commit subject/date: `Update README.md`, `2025-02-04T15:04:05-06:00`;
- archive command: `git archive --format=tar b11da3566b1c3430a23341a3b007ddcbf9cf61cc`;
- unprefixed archive size: `4,669,440` bytes;
- archive SHA-256: `80fc19836ca699dc065ccb3d5e394e5cf2bbe4423eb349f62434cfd5022a6ef5`;
- source tree: 133 files, 4,539,611 tracked bytes;
- license blob: `9cecc1d4669ee8af2ca727a5d8cde10cd8b2d7cc`, 35,141 bytes,
  SHA-256 `589ed823e9a84c56feb95ac58e7cf384626b9cbf4fda2a907bc36e103de1bad2`;
- license: GNU General Public License, Version 3 (`setup.py` declares
  `LICENSE = "GPL"`; SPDX interpretation: `GPL-3.0-only`).

The source provenance and license are coherent. The source layer was removed
by the image build after installation, so it is not a candidate-visible
source bundle.

## Tests And Denominator

The image contains six authored test files and no behavioral test overlay was
found beyond those files. Their final `/workspace/tests` raw SHA-256 values
also match the corresponding files in the pinned source revision:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/test_deauth.py` | 31,201 | `d5688037e50342191f62b84159f4ad57bcafd07013f4db19ac7e37ebf37550fe` |
| `tests/test_extensions.py` | 5,102 | `8b93437c8aee38612b306af87cbd011ed9ca3815e18818a09b046184f584524c` |
| `tests/test_interfaces.py` | 52,276 | `d20ba343df209630c53ace6953e7c29dd76a5b9ed87208f348e74121e0e8b41f` |
| `tests/test_lure10.py` | 5,805 | `f7fa41dfeac5b6c36c38d151cbe628a2a7a7750cba351c7904a01902a227078f` |
| `tests/test_victims.py` | 4,100 | `55245c4eb3ba0b20c02153eeb7dc7bda1e07f1cfd49f7f2a98e3f7f6f90278f` |

Static test inventory is:

```text
test_deauth.py       29 definitions
test_extensions.py    2 definitions
test_interfaces.py   82 definitions, but one duplicate method name
test_lure10.py        9 definitions
test_victims.py       3 definitions
effective Python test methods: 124
```

The duplicate `TestIsManagedByNetworkManager.test_is_managed_by_networkmanager_is_managed_false`
appears at lines 255 and 284 of `test_interfaces.py`; the latter definition
overwrites the former. The retained image `.pytest_cache/v/cache/nodeids`
contains 124 node IDs, consistent with the static effective count. This is
historical image evidence, not a fresh collection run.

Therefore the legacy denominator is not frozen-collection coherent:

```text
legacy expected total: 43
image-derived effective collection: 124
unexplained difference: 81 tests
```

This is a publication-blocking verifier/denominator mismatch. The authored
test bytes are not copied into this audit directory.

## Setup And Dependency Blockers

The initial image setup copy matches the pinned source (`5,793` bytes, raw
SHA-256 `7a2d7d83bac3ae2b3b3ceb8a9955fae96eb738d6fd6b66a1c649cbfa266c9dee`).
The final `/workspace/setup.py` is a different overlay: `1,283` bytes, raw
SHA-256 `3b666e2ee6786dbb74192bd16344dc76f4e5a4829a1448abcccafe01b62c14fd`.
Compared with upstream it removes the console entry point, native library and
`dnsmasq` checks, `dependency_links`, and the `roguehostapd`/`pyric` install
requirements. It retains only `pbkdf2`, `scapy`, and `tornado>=5.0.0`.
This image-only setup overlay is not represented in the legacy manifest or
the public instruction and cannot be silently promoted to a task source.

The image build history installs dependencies using mutable, non-HTTPS
`master` URLs:

```text
http://github.com/wifiphisher/roguehostapd/tarball/master#egg=roguehostapd
http://github.com/sophron/pyric/tarball/master#egg=pyric
```

The project requirements also contain unpinned `pbkdf2`, `scapy`, and
`tornado>=5.0.0`; the historical test setup installed `mock` without a
version pin. No hash-locked wheelhouse, dependency manifest, or offline build
closure is recorded in the task. The immutable image digest freezes one
resulting runtime, but does not make these source inputs reproducible from the
task-local artifacts.

## Candidate Boundary

All five nonempty test modules import `wifiphisher.*` directly and exercise
candidate objects in the pytest process, including mocked `dbus`, Scapy
packets, interface managers, extensions, and victims. The current legacy
contract provides no `candidate_client` subprocess protocol or task-specific
adapter. Running these tests as trusted verifier code would violate the
separate-verifier boundary required for a production Harbor task.

## Static Validation

The following checks were performed without starting infrastructure:

- SHA-256 and byte-size checks for all four legacy artifacts;
- read-only conversion-loop image record inspection;
- read-only registry manifest/config/layer digest and size verification;
- extraction of task-specific image layers under temporary storage only;
- source tree, full-SHA commit, Git archive, license, setup, and test blob
  comparisons;
- AST test inventory and retained image cache node-ID comparison;
- clean worktree/diff inspection after the audit.

No Docker, Harbor, Oracle, pytest, candidate execution, dataset update, or
conversion-loop update was performed.

**Recommendation: blocked.**
