# `cherry` Static Provenance Audit

Status: **blocked**. This directory is an audit record only. It is not a
publishable Harbor task. No public instruction copy, Harbor descriptor,
verifier bundle, Oracle solution, dataset entry, conversion-loop mutation, or
hidden test bytes are included.

## Legacy Contract

- Legacy task: `test_files/cherry/`.
- Declared denominator: `34` (`test_case_count.txt`, 2 bytes, SHA-256
  `86e50149658661312a9e0b35558d84f6c6d3da797f552a9657fe0558ca40cdef`).
- Commands: `pip install -e .`, then `pytest
  --continue-on-collection-errors tests` (`test_commands.json`, 68 bytes,
  SHA-256
  `97cf150f7a0ce56f7d5bbb9d6987e62413c1944209b983cbdec9360408693d8d`).
- Protected path: `tests` (`test_files.json`, 9 bytes, SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Public instruction: 43,852 bytes, SHA-256
  `7efc587494e468c4d95bb1b6dc358ff242ac35187121309573e1142e882b9943`.

Static AST inspection found 34 test functions in eight retained Python files,
with no `parametrize` marker or `pytest_generate_tests` hook. This is
numerically consistent with the legacy denominator, but it is not a frozen
pytest collection record.

| Image fixture path | Test functions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `tests/__init__.py` | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/test_api.py` | 7 | 2,988 | `0b8add46bf1227a01612838ccd7652005727dde477fe86ae60432972002802eb` |
| `tests/test_base.py` | 19 | 10,146 | `79131fa9280d150b7954ae4f687de3c1b3d802e1973655cf29aa7f57c3a630dd` |
| `tests/test_classify.py` | 2 | 932 | `4334b9a4ce74f3bbed500813b518e72e8d2de15ec80583d6d0e5884b5f843f9b` |
| `tests/test_display.py` | 1 | 736 | `c836055519376f802254c0e38f50fb12248f617823fca45c6c0080806d0ac0c4` |
| `tests/test_performance.py` | 1 | 591 | `87d4c89c4741dc91a1bbcd7ee1991923360d453ca30a60e4de7dc651a3c52d3c` |
| `tests/test_search.py` | 1 | 789 | `3a72aeda4c46ffef69190e5224283c3ac21c6408eeb6b3a1d92a493a3eec40a5` |
| `tests/test_trainer.py` | 3 | 2,209 | `bc304179d7a34ff51899be24d661cc117adfb1c5ee6dbcbc9256e7748d85d3f7` |

The fixture totals are eight files, 18,391 bytes, and 34 test functions. A
canonical, path-sorted manifest containing only each relative path and file
SHA-256 has SHA-256
`a2ca25d873d65adf138da2fabf9496b259cb81238380cf73a3709b30cd9dc729`.
The manifest and fixture bytes were used only in temporary inspection storage
and are not added here.

## Pinned Image Evidence

The conversion-loop state record observed for `cherry` had `status =
"available"`, platform `linux/amd64`, and this immutable verifier reference:

`ghcr.io/multimodal-art-projection/nl2repobench/cherry@sha256:a99b8029e934fc887491ef41cbdc950e8aa08ea182fa3f4ed4fa2a344421421d`

Registry inspection resolved the immutable reference to that exact manifest
digest. Additional static image evidence is:

- Config digest:
  `sha256:bb4c90b42e31f1b933fd0a3044bf14df432677c586ccab852f1f55c18db0af7a`.
- Created: `2025-09-02T03:19:39.363439631Z`; working directory:
  `/workspace`; configured runtime: CPython `3.7.9` on `linux/amd64`.
- Retained test-copy layer: compressed digest
  `sha256:eeb248b4cc80cb53edb0fa82fc212b329de9f056948cabf33d54ee160cc03add`;
  uncompressed diff ID
  `sha256:7c71631de4cd031a7caa266884a32308c90e8c039397d3461521d0619887446c`.
- Source-copy layer: compressed digest
  `sha256:c3d36e5edb3f20437c8163b5704fd5f305c896241079eefc57788712fd2da514`;
  uncompressed diff ID
  `sha256:d5cf65ac12cc13e5e38dbb68b679617e908de1e13b8715dd1cbd90ae483e579a`.

The test-copy layer contains exactly the eight files and 18,391 bytes listed
above. All eight files are byte-identical to their counterparts in the image's
source-copy layer. Image history records online editable/dependency installs,
a historical build-time `pytest` command, and deletion of `/cherry`. Those
history entries are provenance only; they are not accepted as a collection,
Oracle, or offline-control result.

## Source And License Lock

- Upstream: `https://github.com/Windsooon/cherry`.
- Full revision:
  `8246824e7b50b84be6697bb4cc2a6381ddcd0ca9` (`master`, committed
  `2022-01-19T17:27:03+08:00`).
- Git tree: `d80e7a123d288a73a96a3d06853db2177079d6e4`.
- Deterministic unprefixed `git archive --format=tar <revision>`: 235,520
  bytes, SHA-256
  `28c6fff07d2f94ef3c305addaa4fb1a6aa6322a51ab79905ef91faaaf0cf67da`.
- License: MIT, evidenced by `LICENSE.txt` at the frozen revision and the
  GitHub license endpoint. The file is 1,069 bytes, Git blob
  `eee734f7e248f8468c20bb90186fd592ba1e9e4e`, SHA-256
  `cfd192784e29bdf972c96466af6ae97bb06bae0e5ae0bf5e80eb57fd6add0521`.

The revision was selected by comparing every image source path with all 328
commits reachable from the upstream heads and tags. The selected revision is
the unique maximum: all 34 upstream-tracked paths are present, 28 are
byte-identical, and six are image modifications. The next closest commits
match only 27 paths. This resolves the source baseline without pretending that
the modified files are upstream blobs.

## Overlay Match

The image source has 34 upstream-tracked files plus ten generated Python cache
files and one test log. Against the frozen revision:

- 28 of 34 tracked files are exact byte matches.
- `requirements.txt` and three of the eight retained test files are exact
  upstream matches.
- The image modifies `setup.py` and five retained test files. The setup change
  disables long-description loading; the test changes adjust temporary
  directory creation and broaden four imports. They do not change assertion
  bodies, but they are still a benchmark overlay.

| Modified path | Upstream SHA-256 | Image SHA-256 |
| --- | --- | --- |
| `setup.py` | `2dc5664498ec0efcf44b8dc7e00c192a7dc0cc75c70b29f9772b629a14b7d0a9` | `807f6fee20c29d7533c63ec39de44891b506cf0b68cad9d5ff952f72beddc3f4` |
| `tests/test_base.py` | `646a8eda200569453c6f7034df15b8aafa537a9234ac673101a02a44bfe11c28` | `79131fa9280d150b7954ae4f687de3c1b3d802e1973655cf29aa7f57c3a630dd` |
| `tests/test_display.py` | `90c0f861b513234bd58438d7c2b5ef29983b333523c167b2f128008660ed8e8f` | `c836055519376f802254c0e38f50fb12248f617823fca45c6c0080806d0ac0c4` |
| `tests/test_performance.py` | `784e2eb05b5154138efec9369597508fd330914b148f0c88bf7f82b9469da9fd` | `87d4c89c4741dc91a1bbcd7ee1991923360d453ca30a60e4de7dc651a3c52d3c` |
| `tests/test_search.py` | `6029d56fd3ed38b19244521a14e3c5288fff28fefcdb6341929a085123578bad` | `3a72aeda4c46ffef69190e5224283c3ac21c6408eeb6b3a1d92a493a3eec40a5` |
| `tests/test_trainer.py` | `ec14a3f2e70e68d33fa978b012e5fe409f672efb56b1307caaa3f2b70bebbf70` | `bc304179d7a34ff51899be24d661cc117adfb1c5ee6dbcbc9256e7748d85d3f7` |

- The canonical six-file patch has 10 additions and 10 deletions, is 3,219
  bytes over 91 lines, and has SHA-256
  `9a0212864b575236d354ac984bb3b0de66950c02f38c98ba3d587d3817985c9d`.
- None of the six image Git blob IDs occurs in any commit reachable from the
  inspected upstream heads or tags.

The patch was generated only for comparison and is not committed. The image
config and history contain no upstream revision label, overlay revision,
license declaration for the overlay, or owner-approved overlay manifest.

## Decision

Keep `cherry` **blocked** and do not create a Harbor bundle from the current
evidence. Treating the five modified tests as unmodified tests from revision
`8246824e...` would fabricate provenance. Treating the immutable legacy image
as a production verifier would also retain direct in-process imports of
candidate code rather than the required `candidate_client` subprocess
boundary.

Other publication gates are intentionally unresolved: there is no frozen
structured collection, offline dependency bundle, three-run Oracle record,
or empty/stub/forgery/offline control evidence. Static denominator agreement
does not substitute for those gates.

To reopen, obtain an owner-approved, immutable, licensed manifest for the
six-file overlay or replace it with exact tests and packaging from a declared
upstream revision. Then adapt the behavior checks to the hardened candidate
subprocess contract, lock the offline dependency closure, collect in the final
verifier image, and run the required Oracle and negative controls in a
separate validation campaign.

## Static Validation

No container process, pytest, Harbor run, Oracle, or negative control was
executed. Static inspection consisted of the conversion-loop state lookup,
immutable registry manifest/config/layer verification, image pull and
non-running filesystem extraction, upstream clone/ref enumeration, Git tree
and archive hashing, license hashing, exhaustive blob/path comparison, and
Python AST counting. Shared scripts, datasets, conversion-loop state, legacy
files, and other task directories were not edited.
